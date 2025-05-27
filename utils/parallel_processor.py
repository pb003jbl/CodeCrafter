import asyncio
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Optional, Callable
import queue
import streamlit as st
from dataclasses import dataclass
from utils.groq_client import GroqClient
import json

@dataclass
class ProcessingTask:
    """Represents a single processing task"""
    task_id: str
    content: str
    language: str
    task_type: str
    priority: int = 1
    metadata: Dict[str, Any] = None

@dataclass
class ProcessingResult:
    """Represents the result of a processing task"""
    task_id: str
    success: bool
    result: Dict[str, Any]
    error: Optional[str] = None
    processing_time: float = 0.0

class RateLimitManager:
    """Manages API rate limits across multiple workers"""
    
    def __init__(self, requests_per_minute: int = 50, tokens_per_minute: int = 5000):
        self.requests_per_minute = requests_per_minute
        self.tokens_per_minute = tokens_per_minute
        self.request_times = queue.Queue()
        self.token_usage = queue.Queue()
        self.lock = threading.Lock()
        
    def can_make_request(self, estimated_tokens: int = 1000) -> bool:
        """Check if we can make a request without hitting rate limits"""
        current_time = time.time()
        
        with self.lock:
            # Clean old request times (older than 1 minute)
            while not self.request_times.empty():
                try:
                    old_time = self.request_times.queue[0]
                    if current_time - old_time > 60:
                        self.request_times.get()
                    else:
                        break
                except:
                    break
            
            # Clean old token usage
            total_tokens = 0
            temp_queue = queue.Queue()
            while not self.token_usage.empty():
                try:
                    timestamp, tokens = self.token_usage.get()
                    if current_time - timestamp <= 60:
                        total_tokens += tokens
                        temp_queue.put((timestamp, tokens))
                except:
                    break
            
            # Restore valid token entries
            while not temp_queue.empty():
                self.token_usage.put(temp_queue.get())
            
            # Check limits
            requests_in_last_minute = self.request_times.qsize()
            tokens_in_last_minute = total_tokens
            
            can_request = (
                requests_in_last_minute < self.requests_per_minute and
                tokens_in_last_minute + estimated_tokens < self.tokens_per_minute
            )
            
            if can_request:
                self.request_times.put(current_time)
                self.token_usage.put((current_time, estimated_tokens))
            
            return can_request
    
    def get_wait_time(self) -> float:
        """Get recommended wait time before next request"""
        if self.request_times.empty():
            return 0.0
        
        oldest_request = self.request_times.queue[0]
        time_since_oldest = time.time() - oldest_request
        
        if time_since_oldest < 60:
            return 60 - time_since_oldest + 1  # Add 1 second buffer
        
        return 0.0

class ParallelProcessor:
    """Parallel processing engine for large file analysis"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.groq_client = GroqClient()
        self.rate_limiter = RateLimitManager()
        self.task_queue = queue.PriorityQueue()
        self.results = {}
        self.processing_stats = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'total_processing_time': 0.0
        }
    
    def chunk_large_content(self, content: str, chunk_size: int = 2000, overlap: int = 200) -> List[Dict[str, Any]]:
        """Intelligently chunk large content for parallel processing"""
        
        lines = content.splitlines()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for i, line in enumerate(lines):
            line_size = len(line) + 1
            
            # If adding this line would exceed chunk size and we have content
            if current_size + line_size > chunk_size and current_chunk:
                # Create chunk with overlap from previous chunk
                chunk_content = '\n'.join(current_chunk)
                
                chunks.append({
                    'content': chunk_content,
                    'start_line': i - len(current_chunk) + 1,
                    'end_line': i,
                    'chunk_id': len(chunks) + 1,
                    'total_chunks': 0,  # Will be updated later
                    'overlap_lines': min(overlap // 20, len(current_chunk))  # Estimate overlap in lines
                })
                
                # Keep overlap lines for context
                overlap_lines = current_chunk[-min(overlap // 20, len(current_chunk)):]
                current_chunk = overlap_lines
                current_size = sum(len(line) + 1 for line in overlap_lines)
            
            current_chunk.append(line)
            current_size += line_size
        
        # Add final chunk
        if current_chunk:
            chunks.append({
                'content': '\n'.join(current_chunk),
                'start_line': len(lines) - len(current_chunk) + 1,
                'end_line': len(lines),
                'chunk_id': len(chunks) + 1,
                'total_chunks': 0,
                'overlap_lines': 0
            })
        
        # Update total chunks count
        for chunk in chunks:
            chunk['total_chunks'] = len(chunks)
        
        return chunks
    
    def create_processing_tasks(
        self, 
        content: str, 
        language: str, 
        analysis_type: str = "comprehensive",
        priority: int = 1
    ) -> List[ProcessingTask]:
        """Create processing tasks from content"""
        
        tasks = []
        
        # Determine if we need to chunk the content
        if len(content) > 3000:  # Large content threshold
            chunks = self.chunk_large_content(content)
            
            for chunk in chunks:
                task = ProcessingTask(
                    task_id=f"{analysis_type}_chunk_{chunk['chunk_id']}",
                    content=chunk['content'],
                    language=language,
                    task_type=analysis_type,
                    priority=priority,
                    metadata={
                        'chunk_info': chunk,
                        'is_chunked': True,
                        'analysis_type': analysis_type
                    }
                )
                tasks.append(task)
        else:
            # Single task for smaller content
            task = ProcessingTask(
                task_id=f"{analysis_type}_full",
                content=content,
                language=language,
                task_type=analysis_type,
                priority=priority,
                metadata={
                    'is_chunked': False,
                    'analysis_type': analysis_type
                }
            )
            tasks.append(task)
        
        return tasks
    
    def process_task(self, task: ProcessingTask) -> ProcessingResult:
        """Process a single task with rate limiting"""
        
        start_time = time.time()
        
        try:
            # Check rate limits
            estimated_tokens = min(len(task.content) // 2, 3000)  # Rough estimate
            
            if not self.rate_limiter.can_make_request(estimated_tokens):
                wait_time = self.rate_limiter.get_wait_time()
                if wait_time > 0:
                    time.sleep(min(wait_time, 30))  # Cap wait time at 30 seconds
            
            # Process the task based on type
            if task.task_type == "security":
                result = self.groq_client.analyze_code(task.content, task.language, "security")
            elif task.task_type == "performance":
                result = self.groq_client.analyze_code(task.content, task.language, "performance")
            elif task.task_type == "comprehensive":
                result = self.groq_client.analyze_code(task.content, task.language, "general")
            else:
                result = self.groq_client.analyze_code(task.content, task.language, "general")
            
            processing_time = time.time() - start_time
            
            if result:
                return ProcessingResult(
                    task_id=task.task_id,
                    success=True,
                    result=result,
                    processing_time=processing_time
                )
            else:
                return ProcessingResult(
                    task_id=task.task_id,
                    success=False,
                    result={},
                    error="API call failed or returned empty result",
                    processing_time=processing_time
                )
        
        except Exception as e:
            processing_time = time.time() - start_time
            return ProcessingResult(
                task_id=task.task_id,
                success=False,
                result={},
                error=str(e),
                processing_time=processing_time
            )
    
    async def process_parallel(
        self, 
        tasks: List[ProcessingTask],
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, ProcessingResult]:
        """Process tasks in parallel with progress tracking"""
        
        self.processing_stats['total_tasks'] = len(tasks)
        results = {}
        
        # Use ThreadPoolExecutor for true parallelism
        with ThreadPoolExecutor(max_workers=min(self.max_workers, len(tasks))) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(self.process_task, task): task 
                for task in tasks
            }
            
            completed = 0
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                
                try:
                    result = future.result()
                    results[task.task_id] = result
                    
                    if result.success:
                        self.processing_stats['completed_tasks'] += 1
                    else:
                        self.processing_stats['failed_tasks'] += 1
                    
                    self.processing_stats['total_processing_time'] += result.processing_time
                    
                except Exception as e:
                    # Handle executor exceptions
                    results[task.task_id] = ProcessingResult(
                        task_id=task.task_id,
                        success=False,
                        result={},
                        error=f"Executor error: {str(e)}"
                    )
                    self.processing_stats['failed_tasks'] += 1
                
                completed += 1
                
                # Call progress callback if provided
                if progress_callback:
                    progress_callback(completed, len(tasks), results[task.task_id])
        
        return results
    
    def combine_chunk_results(self, results: Dict[str, ProcessingResult]) -> Dict[str, Any]:
        """Combine results from multiple chunks into a comprehensive analysis"""
        
        combined_result = {
            'analysis_type': 'parallel_processing',
            'total_chunks': len(results),
            'successful_chunks': sum(1 for r in results.values() if r.success),
            'failed_chunks': sum(1 for r in results.values() if not r.success),
            'processing_stats': self.processing_stats.copy(),
            'combined_findings': [],
            'overall_recommendations': [],
            'chunk_details': []
        }
        
        # Aggregate findings from all successful chunks
        all_issues = []
        security_scores = []
        performance_scores = []
        quality_scores = []
        
        for task_id, result in results.items():
            if result.success and result.result:
                # Extract findings based on result structure
                if 'vulnerabilities' in result.result:
                    for vuln in result.result['vulnerabilities']:
                        all_issues.append({
                            'type': 'security',
                            'severity': vuln.get('severity', 'Medium'),
                            'title': vuln.get('title', 'Security Issue'),
                            'description': vuln.get('description', ''),
                            'chunk_id': task_id,
                            'fix': vuln.get('fix', '')
                        })
                    
                    if 'security_score' in result.result:
                        security_scores.append(result.result['security_score'])
                
                if 'performance_issues' in result.result:
                    for issue in result.result['performance_issues']:
                        all_issues.append({
                            'type': 'performance',
                            'severity': issue.get('severity', 'Medium'),
                            'title': issue.get('title', 'Performance Issue'),
                            'description': issue.get('description', ''),
                            'chunk_id': task_id,
                            'optimization': issue.get('optimization', '')
                        })
                
                if 'issues' in result.result:
                    for issue in result.result['issues']:
                        all_issues.append({
                            'type': 'quality',
                            'severity': issue.get('severity', 'Medium'),
                            'title': issue.get('title', 'Quality Issue'),
                            'description': issue.get('description', ''),
                            'chunk_id': task_id,
                            'suggestion': issue.get('suggestion', '')
                        })
                    
                    if 'code_quality' in result.result:
                        quality_scores.append(result.result['code_quality'])
                
                # Add chunk details
                combined_result['chunk_details'].append({
                    'chunk_id': task_id,
                    'success': result.success,
                    'processing_time': result.processing_time,
                    'issues_found': len([i for i in all_issues if i.get('chunk_id') == task_id])
                })
        
        # Calculate overall scores
        combined_result['overall_scores'] = {
            'security': sum(security_scores) / len(security_scores) if security_scores else 70,
            'performance': sum(performance_scores) / len(performance_scores) if performance_scores else 70,
            'quality': sum(quality_scores) / len(quality_scores) if quality_scores else 70
        }
        
        # Prioritize and filter issues
        combined_result['combined_findings'] = self.prioritize_issues(all_issues)
        
        # Generate comprehensive recommendations
        combined_result['overall_recommendations'] = self.generate_comprehensive_recommendations(
            combined_result['combined_findings'],
            combined_result['overall_scores']
        )
        
        return combined_result
    
    def prioritize_issues(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize and deduplicate issues from multiple chunks"""
        
        # Define severity order
        severity_order = {'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1}
        
        # Sort by severity and type
        sorted_issues = sorted(
            issues,
            key=lambda x: (
                severity_order.get(x.get('severity', 'Medium'), 2),
                x.get('type', 'quality')
            ),
            reverse=True
        )
        
        # Remove similar issues (simple deduplication)
        unique_issues = []
        seen_titles = set()
        
        for issue in sorted_issues:
            title_key = f"{issue.get('type')}_{issue.get('title', '').lower()}"
            if title_key not in seen_titles:
                unique_issues.append(issue)
                seen_titles.add(title_key)
        
        return unique_issues[:20]  # Limit to top 20 issues
    
    def generate_comprehensive_recommendations(
        self, 
        findings: List[Dict[str, Any]], 
        scores: Dict[str, float]
    ) -> List[str]:
        """Generate comprehensive recommendations based on parallel analysis"""
        
        recommendations = []
        
        # Security recommendations
        security_issues = [f for f in findings if f.get('type') == 'security']
        if security_issues:
            critical_security = [f for f in security_issues if f.get('severity') == 'Critical']
            if critical_security:
                recommendations.append(
                    f"🔴 URGENT: Address {len(critical_security)} critical security vulnerabilities immediately"
                )
            recommendations.append(
                f"🔒 Implement security best practices - {len(security_issues)} security issues identified"
            )
        
        # Performance recommendations
        performance_issues = [f for f in findings if f.get('type') == 'performance']
        if performance_issues:
            recommendations.append(
                f"⚡ Optimize performance - {len(performance_issues)} bottlenecks identified"
            )
        
        # Quality recommendations
        quality_issues = [f for f in findings if f.get('type') == 'quality']
        if quality_issues:
            recommendations.append(
                f"✨ Improve code quality - {len(quality_issues)} quality issues found"
            )
        
        # Overall recommendations
        if scores.get('security', 0) < 60:
            recommendations.append("🛡️ Consider security audit and penetration testing")
        
        if scores.get('performance', 0) < 60:
            recommendations.append("📊 Implement performance monitoring and optimization")
        
        if scores.get('quality', 0) < 60:
            recommendations.append("🔧 Refactor code for better maintainability")
        
        # Parallel processing insights
        recommendations.append("🚀 Large file analysis completed using parallel processing")
        recommendations.append("📈 Consider implementing continuous code analysis in CI/CD pipeline")
        
        return recommendations
    
    def get_processing_metrics(self) -> Dict[str, Any]:
        """Get detailed processing metrics"""
        
        total_tasks = self.processing_stats['total_tasks']
        completed_tasks = self.processing_stats['completed_tasks']
        failed_tasks = self.processing_stats['failed_tasks']
        
        success_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        avg_processing_time = (
            self.processing_stats['total_processing_time'] / total_tasks 
            if total_tasks > 0 else 0
        )
        
        return {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'failed_tasks': failed_tasks,
            'success_rate': round(success_rate, 2),
            'average_processing_time': round(avg_processing_time, 2),
            'total_processing_time': round(self.processing_stats['total_processing_time'], 2),
            'parallel_efficiency': round(
                (total_tasks * avg_processing_time) / self.processing_stats['total_processing_time'] 
                if self.processing_stats['total_processing_time'] > 0 else 1.0, 2
            )
        }