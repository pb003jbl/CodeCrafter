
import time
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import statistics
from dataclasses import dataclass, asdict
from collections import defaultdict

@dataclass
class AgentMetric:
    """Individual agent performance metric"""
    agent_name: str
    task_type: str
    start_time: float
    end_time: float
    success: bool
    response_quality: int  # 1-10 scale
    tokens_used: int
    error_message: Optional[str] = None
    
    @property
    def execution_time(self) -> float:
        return self.end_time - self.start_time
    
    @property
    def timestamp(self) -> str:
        return datetime.fromtimestamp(self.start_time).isoformat()

class AgentPerformanceTracker:
    """Track and analyze agent performance metrics"""
    
    def __init__(self):
        self.metrics: List[AgentMetric] = []
        self.session_start = time.time()
        self.active_tasks: Dict[str, float] = {}
        
    def start_task(self, agent_name: str, task_type: str, task_id: str = None) -> str:
        """Start tracking a task for an agent"""
        task_id = task_id or f"{agent_name}_{int(time.time() * 1000)}"
        self.active_tasks[task_id] = time.time()
        return task_id
    
    def complete_task(self, task_id: str, agent_name: str, task_type: str, 
                     success: bool, response_quality: int = 5, 
                     tokens_used: int = 0, error_message: str = None):
        """Complete a task and record metrics"""
        if task_id not in self.active_tasks:
            return
        
        start_time = self.active_tasks.pop(task_id)
        end_time = time.time()
        
        metric = AgentMetric(
            agent_name=agent_name,
            task_type=task_type,
            start_time=start_time,
            end_time=end_time,
            success=success,
            response_quality=response_quality,
            tokens_used=tokens_used,
            error_message=error_message
        )
        
        self.metrics.append(metric)
    
    def get_agent_statistics(self, agent_name: str = None, 
                           time_window_hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive statistics for agents"""
        
        # Filter metrics by time window
        cutoff_time = time.time() - (time_window_hours * 3600)
        recent_metrics = [m for m in self.metrics if m.start_time >= cutoff_time]
        
        if agent_name:
            recent_metrics = [m for m in recent_metrics if m.agent_name == agent_name]
        
        if not recent_metrics:
            return {"message": "No metrics available for the specified criteria"}
        
        # Calculate statistics
        total_tasks = len(recent_metrics)
        successful_tasks = len([m for m in recent_metrics if m.success])
        success_rate = (successful_tasks / total_tasks) * 100 if total_tasks > 0 else 0
        
        execution_times = [m.execution_time for m in recent_metrics]
        quality_scores = [m.response_quality for m in recent_metrics if m.response_quality > 0]
        token_usage = sum(m.tokens_used for m in recent_metrics)
        
        stats = {
            "total_tasks": total_tasks,
            "successful_tasks": successful_tasks,
            "success_rate": round(success_rate, 2),
            "average_execution_time": round(statistics.mean(execution_times), 3) if execution_times else 0,
            "median_execution_time": round(statistics.median(execution_times), 3) if execution_times else 0,
            "min_execution_time": round(min(execution_times), 3) if execution_times else 0,
            "max_execution_time": round(max(execution_times), 3) if execution_times else 0,
            "average_quality_score": round(statistics.mean(quality_scores), 2) if quality_scores else 0,
            "total_tokens_used": token_usage,
            "average_tokens_per_task": round(token_usage / total_tasks, 2) if total_tasks > 0 else 0,
            "time_window_hours": time_window_hours
        }
        
        return stats
    
    def get_agent_comparison(self, time_window_hours: int = 24) -> Dict[str, Dict[str, Any]]:
        """Compare performance across all agents"""
        
        cutoff_time = time.time() - (time_window_hours * 3600)
        recent_metrics = [m for m in self.metrics if m.start_time >= cutoff_time]
        
        # Group by agent
        agent_groups = defaultdict(list)
        for metric in recent_metrics:
            agent_groups[metric.agent_name].append(metric)
        
        comparison = {}
        for agent_name, agent_metrics in agent_groups.items():
            if agent_metrics:
                comparison[agent_name] = self._calculate_agent_stats(agent_metrics)
        
        return comparison
    
    def get_task_type_analysis(self, time_window_hours: int = 24) -> Dict[str, Dict[str, Any]]:
        """Analyze performance by task type"""
        
        cutoff_time = time.time() - (time_window_hours * 3600)
        recent_metrics = [m for m in self.metrics if m.start_time >= cutoff_time]
        
        # Group by task type
        task_groups = defaultdict(list)
        for metric in recent_metrics:
            task_groups[metric.task_type].append(metric)
        
        analysis = {}
        for task_type, task_metrics in task_groups.items():
            if task_metrics:
                analysis[task_type] = self._calculate_agent_stats(task_metrics)
        
        return analysis
    
    def _calculate_agent_stats(self, metrics: List[AgentMetric]) -> Dict[str, Any]:
        """Calculate statistics for a group of metrics"""
        
        total_tasks = len(metrics)
        successful_tasks = len([m for m in metrics if m.success])
        success_rate = (successful_tasks / total_tasks) * 100 if total_tasks > 0 else 0
        
        execution_times = [m.execution_time for m in metrics]
        quality_scores = [m.response_quality for m in metrics if m.response_quality > 0]
        token_usage = sum(m.tokens_used for m in metrics)
        
        return {
            "total_tasks": total_tasks,
            "success_rate": round(success_rate, 2),
            "avg_execution_time": round(statistics.mean(execution_times), 3) if execution_times else 0,
            "avg_quality_score": round(statistics.mean(quality_scores), 2) if quality_scores else 0,
            "total_tokens": token_usage,
            "avg_tokens_per_task": round(token_usage / total_tasks, 2) if total_tasks > 0 else 0
        }
    
    def get_performance_trends(self, agent_name: str = None, 
                             hours_back: int = 24, 
                             interval_hours: int = 1) -> Dict[str, List[Dict[str, Any]]]:
        """Get performance trends over time"""
        
        end_time = time.time()
        start_time = end_time - (hours_back * 3600)
        
        trends = []
        current_time = start_time
        
        while current_time < end_time:
            interval_end = current_time + (interval_hours * 3600)
            
            # Get metrics for this time interval
            interval_metrics = [
                m for m in self.metrics 
                if current_time <= m.start_time < interval_end
            ]
            
            if agent_name:
                interval_metrics = [m for m in interval_metrics if m.agent_name == agent_name]
            
            # Calculate stats for interval
            if interval_metrics:
                stats = self._calculate_agent_stats(interval_metrics)
                stats["timestamp"] = datetime.fromtimestamp(current_time).isoformat()
                trends.append(stats)
            
            current_time = interval_end
        
        return {"trends": trends, "interval_hours": interval_hours}
    
    def get_error_analysis(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """Analyze errors and failure patterns"""
        
        cutoff_time = time.time() - (time_window_hours * 3600)
        recent_metrics = [m for m in self.metrics if m.start_time >= cutoff_time]
        
        failed_metrics = [m for m in recent_metrics if not m.success]
        
        if not failed_metrics:
            return {"message": "No errors found in the specified time window"}
        
        # Group errors by agent and type
        error_by_agent = defaultdict(list)
        error_by_task = defaultdict(list)
        error_messages = defaultdict(int)
        
        for metric in failed_metrics:
            error_by_agent[metric.agent_name].append(metric)
            error_by_task[metric.task_type].append(metric)
            if metric.error_message:
                error_messages[metric.error_message] += 1
        
        return {
            "total_errors": len(failed_metrics),
            "errors_by_agent": {agent: len(errors) for agent, errors in error_by_agent.items()},
            "errors_by_task_type": {task: len(errors) for task, errors in error_by_task.items()},
            "common_error_messages": dict(sorted(error_messages.items(), key=lambda x: x[1], reverse=True)[:10]),
            "error_rate": round((len(failed_metrics) / len(recent_metrics)) * 100, 2) if recent_metrics else 0
        }
    
    def export_metrics(self, filename: str = None) -> str:
        """Export metrics to JSON file"""
        
        filename = filename or f"agent_metrics_{int(time.time())}.json"
        
        export_data = {
            "session_start": self.session_start,
            "export_time": time.time(),
            "total_metrics": len(self.metrics),
            "metrics": [asdict(metric) for metric in self.metrics]
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return filename
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get overall session performance summary"""
        
        if not self.metrics:
            return {"message": "No metrics available for this session"}
        
        session_duration = time.time() - self.session_start
        unique_agents = len(set(m.agent_name for m in self.metrics))
        unique_task_types = len(set(m.task_type for m in self.metrics))
        
        overall_stats = self._calculate_agent_stats(self.metrics)
        
        return {
            "session_duration_minutes": round(session_duration / 60, 2),
            "unique_agents_used": unique_agents,
            "unique_task_types": unique_task_types,
            "tasks_per_minute": round(len(self.metrics) / (session_duration / 60), 2),
            **overall_stats
        }

# Global instance for tracking across the application
performance_tracker = AgentPerformanceTracker()
