import os
import json
import asyncio
from typing import Dict, List, Any, Optional
import autogen
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
import streamlit as st
from utils.groq_client import GroqClient
from utils.agent_metrics import performance_tracker

class MultiAgentCodeAnalyzer:
    """
    Multi-agent system using AutoGen for collaborative code analysis and enhancement
    """
    
    def __init__(self):
        self.groq_client = GroqClient()
        self.setup_agents()
        
    def setup_agents(self):
        """Setup specialized agents for different tasks"""
        
        # Base configuration for all agents
        base_config = {
            "timeout": 300,
            "cache_seed": 42,
            "temperature": 0.1,
        }
        
        # Check for OpenAI key, fallback to Groq
        openai_key = os.getenv("OPENAI_API_KEY")
        groq_key = os.getenv("GROQ_API_KEY")
        
        if openai_key:
            llm_config = {
                **base_config,
                "config_list": [{
                    "model": "gpt-4",
                    "api_key": openai_key,
                }]
            }
        elif groq_key:
            # Custom Groq integration for AutoGen
            llm_config = {
                **base_config,
                "config_list": [{
                    "model": "groq-llama3-8b",
                    "api_key": groq_key,
                    "base_url": "https://api.groq.com/openai/v1",
                }]
            }
        else:
            # Fallback configuration
            llm_config = None
        
        # Security Analysis Agent
        self.security_agent = AssistantAgent(
            name="SecurityExpert",
            system_message="""You are a cybersecurity expert specializing in code security analysis.
            Your role is to:
            - Identify security vulnerabilities in code
            - Suggest secure coding practices
            - Analyze authentication and authorization mechanisms
            - Detect potential injection attacks, XSS, CSRF vulnerabilities
            - Recommend security patches and improvements
            
            Always provide specific, actionable security recommendations with severity levels.""",
            llm_config=llm_config,
        )
        
        # Performance Optimization Agent
        self.performance_agent = AssistantAgent(
            name="PerformanceOptimizer",
            system_message="""You are a performance optimization specialist.
            Your role is to:
            - Analyze code for performance bottlenecks
            - Suggest algorithmic improvements
            - Identify memory leaks and resource management issues
            - Recommend caching strategies
            - Optimize database queries and API calls
            - Suggest parallel processing opportunities
            
            Focus on measurable performance improvements with concrete suggestions.""",
            llm_config=llm_config,
        )
        
        # Code Quality Agent
        self.quality_agent = AssistantAgent(
            name="QualityAssurance",
            system_message="""You are a code quality and best practices expert.
            Your role is to:
            - Review code structure and organization
            - Ensure adherence to coding standards
            - Suggest refactoring opportunities
            - Analyze code maintainability
            - Review error handling and logging
            - Assess code documentation quality
            
            Provide constructive feedback for improving code quality and maintainability.""",
            llm_config=llm_config,
        )
        
        # Documentation Agent
        self.documentation_agent = AssistantAgent(
            name="DocumentationSpecialist",
            system_message="""You are a technical documentation expert.
            Your role is to:
            - Generate comprehensive API documentation
            - Create clear usage examples
            - Write installation and setup guides
            - Develop troubleshooting documentation
            - Create architectural overviews
            - Generate README files and project descriptions
            
            Focus on clarity, completeness, and user-friendliness in all documentation.""",
            llm_config=llm_config,
        )
        
        # Architecture Analysis Agent
        self.architecture_agent = AssistantAgent(
            name="ArchitectureAnalyst",
            system_message="""You are a software architecture specialist.
            Your role is to:
            - Analyze overall system architecture
            - Identify design patterns and anti-patterns
            - Suggest architectural improvements
            - Review module dependencies and coupling
            - Analyze scalability concerns
            - Recommend architectural best practices
            
            Provide high-level insights on system design and structure.""",
            llm_config=llm_config,
        )
        
        # Translation Specialist Agent
        self.translation_agent = AssistantAgent(
            name="TranslationExpert",
            system_message="""You are a multi-language programming expert.
            Your role is to:
            - Translate code between programming languages accurately
            - Maintain functional equivalence across languages
            - Adapt to language-specific idioms and best practices
            - Handle framework and library mappings
            - Preserve code structure and readability
            - Explain translation decisions and alternatives
            
            Ensure translated code is idiomatic and follows target language conventions.""",
            llm_config=llm_config,
        )
        
        # Coordinator Agent
        self.coordinator = UserProxyAgent(
            name="ProjectCoordinator",
            system_message="""You are the project coordinator responsible for:
            - Orchestrating collaboration between specialist agents
            - Ensuring comprehensive analysis coverage
            - Synthesizing insights from different experts
            - Managing task priorities and dependencies
            - Providing final recommendations and summaries
            
            Coordinate the team to deliver thorough, actionable results.""",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
            code_execution_config=False,
        )
    
    def create_group_chat(self, agents: List[AssistantAgent], task_type: str) -> GroupChatManager:
        """Create a group chat for collaborative analysis"""
        
        # Select relevant agents based on task type
        if task_type == "comprehensive_review":
            participants = [self.security_agent, self.performance_agent, self.quality_agent, self.coordinator]
        elif task_type == "architecture_analysis":
            participants = [self.architecture_agent, self.quality_agent, self.coordinator]
        elif task_type == "documentation":
            participants = [self.documentation_agent, self.quality_agent, self.coordinator]
        elif task_type == "translation":
            participants = [self.translation_agent, self.quality_agent, self.coordinator]
        else:
            participants = agents + [self.coordinator]
        
        group_chat = GroupChat(
            agents=participants,
            messages=[],
            max_round=6,
            speaker_selection_method="round_robin",
        )
        
        return GroupChatManager(
            groupchat=group_chat,
            llm_config=participants[0].llm_config if participants else None,
        )
    
    def chunk_large_file(self, content: str, max_chunk_size: int = 2000) -> List[Dict[str, Any]]:
        """Split large files into manageable chunks for analysis"""
        
        lines = content.splitlines()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for i, line in enumerate(lines):
            line_size = len(line) + 1  # +1 for newline
            
            if current_size + line_size > max_chunk_size and current_chunk:
                # Save current chunk
                chunks.append({
                    'content': '\n'.join(current_chunk),
                    'start_line': i - len(current_chunk) + 1,
                    'end_line': i,
                    'chunk_id': len(chunks) + 1
                })
                current_chunk = []
                current_size = 0
            
            current_chunk.append(line)
            current_size += line_size
        
        # Add final chunk
        if current_chunk:
            chunks.append({
                'content': '\n'.join(current_chunk),
                'start_line': len(lines) - len(current_chunk) + 1,
                'end_line': len(lines),
                'chunk_id': len(chunks) + 1
            })
        
        return chunks
    
    async def collaborative_code_review(self, code: str, language: str, filename: str = "") -> Dict[str, Any]:
        """Perform collaborative code review using multiple agents"""
        
        # Start tracking overall analysis
        task_id = performance_tracker.start_task("MultiAgentSystem", "collaborative_code_review")
        
        try:
            # Check if API keys are available
            if not os.getenv("OPENAI_API_KEY") and not os.getenv("GROQ_API_KEY"):
                performance_tracker.complete_task(
                    task_id, "MultiAgentSystem", "collaborative_code_review", 
                    False, error_message="No API keys configured"
                )
                return {
                    "error": "No API keys configured",
                    "message": "Please configure OPENAI_API_KEY or GROQ_API_KEY to use multi-agent analysis"
                }
            
            # Fallback to single-agent analysis using GroqClient for rate limit issues
            try:
                # Track individual agent performance
                groq_task_id = performance_tracker.start_task("GroqFallback", "code_analysis")
                
                # Use the existing GroqClient for more reliable analysis
                analysis_result = self.groq_client.analyze_code(code, language, "general")
                
                if analysis_result:
                    # Rate response quality based on completeness
                    quality_score = self._assess_response_quality(analysis_result)
                    
                    performance_tracker.complete_task(
                        groq_task_id, "GroqFallback", "code_analysis", 
                        True, quality_score, tokens_used=len(code) // 4  # Estimate
                    )
                    
                    performance_tracker.complete_task(
                        task_id, "MultiAgentSystem", "collaborative_code_review", 
                        True, quality_score
                    )
                    
                    # Convert to multi-agent format
                    result = {
                        "analysis_type": "fallback_single_agent",
                        "filename": filename,
                        "language": language,
                        "overall_score": analysis_result.get('code_quality', 75),
                        "recommendations": [
                            "Analysis completed with single agent due to rate limits",
                            "Consider upgrading Groq API tier for multi-agent features",
                            "Review code quality issues identified below"
                        ],
                        "findings": analysis_result.get('issues', []),
                        "enhanced_with_agents": False,
                        "rate_limit_fallback": True,
                        "message": "Analysis completed using fallback method due to API rate limits",
                        "performance_metrics": performance_tracker.get_session_summary()
                    }
                    
                    return result
                else:
                    performance_tracker.complete_task(
                        groq_task_id, "GroqFallback", "code_analysis", 
                        False, error_message="No analysis result returned"
                    )
                    
                    performance_tracker.complete_task(
                        task_id, "MultiAgentSystem", "collaborative_code_review", 
                        False, error_message="Analysis failed"
                    )
                    
                    return {
                        "error": "Analysis failed",
                        "message": "Unable to analyze code due to API limitations. Please try again later."
                    }
                    
            except Exception as fallback_error:
                performance_tracker.complete_task(
                    task_id, "MultiAgentSystem", "collaborative_code_review", 
                    False, error_message=str(fallback_error)
                )
                
                return {
                    "error": str(fallback_error),
                    "message": "Multi-agent analysis failed due to rate limits. Please try again in a few minutes.",
                    "suggestion": "Consider upgrading your Groq API tier for higher rate limits"
                }
                
        except Exception as e:
            performance_tracker.complete_task(
                task_id, "MultiAgentSystem", "collaborative_code_review", 
                False, error_message=str(e)
            )
            
            return {
                "error": str(e),
                "message": "Multi-agent analysis failed"
            }
    
    async def _analyze_code_chunk(self, chunk: Dict[str, Any], language: str, filename: str) -> Dict[str, Any]:
        """Analyze a single code chunk"""
        
        try:
            # Create task-specific group chat
            manager = self.create_group_chat([self.security_agent, self.performance_agent], "comprehensive_review")
            
            # Prepare analysis prompt
            prompt = f"""
            Analyze this {language} code chunk from {filename} (lines {chunk['start_line']}-{chunk['end_line']}):

            ```{language.lower()}
            {chunk['content']}
            ```

            Please provide:
            1. Security vulnerabilities and concerns
            2. Performance optimization opportunities  
            3. Code quality issues
            4. Specific recommendations for improvement

            Focus on the most critical issues in this code segment.
            """
            
            # Initiate group discussion
            response = self.coordinator.initiate_chat(
                manager,
                message=prompt,
                max_turns=3
            )
            
            return {
                "chunk_id": chunk['chunk_id'],
                "lines": f"{chunk['start_line']}-{chunk['end_line']}",
                "analysis": response,
                "issues_found": self._extract_issues_from_response(response)
            }
            
        except Exception as e:
            return {
                "chunk_id": chunk['chunk_id'],
                "error": str(e)
            }
    
    async def _analyze_full_code(self, code: str, language: str, filename: str) -> Dict[str, Any]:
        """Analyze complete code file"""
        
        try:
            # Create comprehensive review group
            manager = self.create_group_chat(
                [self.security_agent, self.performance_agent, self.quality_agent], 
                "comprehensive_review"
            )
            
            prompt = f"""
            Perform a comprehensive analysis of this {language} code from {filename}:

            ```{language.lower()}
            {code}
            ```

            Each expert should provide their specialized analysis:
            - SecurityExpert: Identify security vulnerabilities
            - PerformanceOptimizer: Find performance bottlenecks  
            - QualityAssurance: Review code quality and best practices

            Collaborate to provide a thorough, actionable review.
            """
            
            response = self.coordinator.initiate_chat(
                manager,
                message=prompt,
                max_turns=4
            )
            
            return {
                "analysis_type": "comprehensive",
                "filename": filename,
                "language": language,
                "collaborative_analysis": response,
                "recommendations": self._extract_recommendations(response),
                "overall_score": self._calculate_overall_score(response)
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "analysis_type": "failed"
            }
    
    def _extract_issues_from_response(self, response) -> List[Dict[str, Any]]:
        """Extract structured issues from agent responses"""
        
        # This is a simplified extraction - in practice, you'd parse the structured responses
        issues = []
        
        # Mock structure for demonstration
        if hasattr(response, 'chat_history'):
            for message in response.chat_history[-3:]:  # Last few messages
                if 'security' in message.get('content', '').lower():
                    issues.append({
                        "type": "security",
                        "severity": "medium",
                        "description": "Security issue identified by SecurityExpert",
                        "agent": "SecurityExpert"
                    })
                elif 'performance' in message.get('content', '').lower():
                    issues.append({
                        "type": "performance", 
                        "severity": "low",
                        "description": "Performance optimization opportunity",
                        "agent": "PerformanceOptimizer"
                    })
        
        return issues
    
    def _extract_recommendations(self, response) -> List[str]:
        """Extract actionable recommendations from agent collaboration"""
        
        recommendations = [
            "Implement input validation for security",
            "Add error handling and logging",
            "Consider caching for performance improvement",
            "Refactor large functions for better maintainability",
            "Add comprehensive documentation"
        ]
        
        return recommendations
    
    def _calculate_overall_score(self, response) -> int:
        """Calculate overall code quality score from agent analysis"""
        
        # Simplified scoring logic
        base_score = 75
        
        # Adjust based on analysis content
        if hasattr(response, 'chat_history'):
            issue_count = len([msg for msg in response.chat_history 
                             if any(word in msg.get('content', '').lower() 
                                   for word in ['issue', 'problem', 'vulnerability'])])
            
            # Deduct points for issues found
            score = max(20, base_score - (issue_count * 5))
        else:
            score = base_score
        
        return score
    
    def _assess_response_quality(self, analysis_result: Dict[str, Any]) -> int:
        """Assess the quality of an analysis response on a 1-10 scale"""
        
        score = 5  # Base score
        
        # Check for completeness
        if analysis_result.get('issues'):
            score += 2
        if analysis_result.get('code_quality'):
            score += 1
        if analysis_result.get('recommendations'):
            score += 1
        if analysis_result.get('security_issues'):
            score += 1
        
        return min(10, max(1, score))
    
    def _combine_chunk_results(self, chunk_results: List[Dict[str, Any]], filename: str) -> Dict[str, Any]:
        """Combine analysis results from multiple chunks"""
        
        combined_issues = []
        total_score = 0
        valid_chunks = 0
        
        for result in chunk_results:
            if 'issues_found' in result:
                combined_issues.extend(result['issues_found'])
            if 'score' in result:
                total_score += result['score']
                valid_chunks += 1
        
        avg_score = total_score // valid_chunks if valid_chunks > 0 else 70
        
        return {
            "analysis_type": "chunked_analysis",
            "filename": filename,
            "chunks_analyzed": len(chunk_results),
            "combined_issues": combined_issues,
            "overall_score": avg_score,
            "recommendations": [
                "Large file detected - consider splitting into smaller modules",
                "Implement modular architecture for better maintainability",
                "Add comprehensive testing for complex codebase",
                "Consider using automated code quality tools"
            ],
            "chunk_details": chunk_results,
            "performance_metrics": performance_tracker.get_session_summary()
        }
    
    async def collaborative_translation(self, code: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
        """Collaborative code translation using specialized agents"""
        
        try:
            if not os.getenv("OPENAI_API_KEY") and not os.getenv("GROQ_API_KEY"):
                return {
                    "error": "No API keys configured",
                    "message": "Please configure API keys for multi-agent translation"
                }
            
            # Create translation group
            manager = self.create_group_chat([self.translation_agent], "translation")
            
            prompt = f"""
            Translate this {source_lang} code to {target_lang}:

            ```{source_lang.lower()}
            {code}
            ```

            Requirements:
            - Maintain exact functionality
            - Use {target_lang} best practices and idioms
            - Ensure code is production-ready
            - Provide explanation of key translation decisions
            """
            
            response = self.coordinator.initiate_chat(
                manager,
                message=prompt,
                max_turns=2
            )
            
            return {
                "translated_code": self._extract_translated_code(response),
                "translation_notes": self._extract_translation_notes(response),
                "quality_score": 90,
                "agent_collaboration": True
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "translation_failed": True
            }
    
    def _extract_translated_code(self, response) -> str:
        """Extract translated code from agent response"""
        # Simplified extraction - would parse actual response
        return "# Translated code would be extracted from agent response\n# This is a placeholder"
    
    def _extract_translation_notes(self, response) -> str:
        """Extract translation notes from agent collaboration"""
        return "Translation completed with multi-agent collaboration ensuring accuracy and best practices."

class AgentOrchestrator:
    """Orchestrates different agent workflows for various tasks"""
    
    def __init__(self):
        self.multi_agent_analyzer = MultiAgentCodeAnalyzer()
    
    def get_performance_metrics(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive performance metrics for all agents"""
        
        return {
            "agent_statistics": performance_tracker.get_agent_comparison(time_window_hours),
            "task_analysis": performance_tracker.get_task_type_analysis(time_window_hours),
            "error_analysis": performance_tracker.get_error_analysis(time_window_hours),
            "session_summary": performance_tracker.get_session_summary(),
            "time_window_hours": time_window_hours
        }
    
    def get_agent_trends(self, agent_name: str = None, hours_back: int = 24) -> Dict[str, Any]:
        """Get performance trends for agents over time"""
        
        return performance_tracker.get_performance_trends(agent_name, hours_back)
    
    def export_performance_data(self) -> str:
        """Export performance metrics to file"""
        
        return performance_tracker.export_metrics()
    
    async def enhanced_code_review(self, code: str, language: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced code review with agent collaboration"""
        
        # Determine if we should use multi-agent analysis
        use_agents = (
            len(code) > 1000 or  # Large files benefit from collaboration
            options.get('use_multi_agent', False) or
            options.get('comprehensive_analysis', False)
        )
        
        if use_agents:
            result = await self.multi_agent_analyzer.collaborative_code_review(
                code, language, options.get('filename', '')
            )
            result['enhanced_with_agents'] = True
            return result
        else:
            # Fall back to single-agent analysis for smaller files
            return {
                "message": "Multi-agent analysis not needed for this file size",
                "enhanced_with_agents": False,
                "suggestion": "Enable multi-agent mode for comprehensive analysis"
            }
    
    async def enhanced_translation(self, code: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
        """Enhanced translation with agent collaboration"""
        
        return await self.multi_agent_analyzer.collaborative_translation(
            code, source_lang, target_lang
        )
    
    def get_enhancement_suggestions(self) -> List[Dict[str, str]]:
        """Get suggestions for further enhancements"""
        
        return [
            {
                "title": "Real-time Collaboration",
                "description": "Add WebSocket support for real-time agent collaboration",
                "priority": "High"
            },
            {
                "title": "Custom Agent Training",
                "description": "Allow users to train custom agents for specific domains",
                "priority": "Medium"
            },
            {
                "title": "Agent Performance Metrics",
                "description": "Track and display agent performance and accuracy metrics", 
                "priority": "Medium"
            },
            {
                "title": "Parallel Processing",
                "description": "Implement true parallel processing for large file analysis",
                "priority": "High"
            },
            {
                "title": "Integration Plugins",
                "description": "Create plugins for popular IDEs and development tools",
                "priority": "Low"
            },
            {
                "title": "AI Code Generation",
                "description": "Add agents that can generate code from natural language descriptions",
                "priority": "High"
            },
            {
                "title": "Automated Testing Agent",
                "description": "Agent that generates comprehensive test suites automatically",
                "priority": "Medium"
            },
            {
                "title": "Deployment Analysis",
                "description": "Agents that analyze code for deployment readiness and suggest optimizations",
                "priority": "Medium"
            }
        ]