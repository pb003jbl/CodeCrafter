
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.multi_agent_system import AgentOrchestrator
from utils.agent_metrics import performance_tracker
from components.sidebar import render_sidebar

st.set_page_config(page_title="Agent Performance", page_icon="📊", layout="wide")

def main():
    render_sidebar()
    
    st.title("📊 Agent Performance & Accuracy Metrics")
    st.markdown("Monitor and analyze the performance of your AI agents in real-time")
    
    # Initialize orchestrator
    orchestrator = AgentOrchestrator()
    
    # Control panel
    st.markdown("### ⚙️ Metrics Control Panel")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        time_window = st.selectbox(
            "Time Window",
            [1, 6, 12, 24, 48, 168],  # Hours
            index=3,
            format_func=lambda x: f"Last {x} hours" if x < 24 else f"Last {x//24} days"
        )
    
    with col2:
        auto_refresh = st.checkbox("Auto Refresh", value=True)
        
    with col3:
        if st.button("🔄 Refresh Metrics", type="primary"):
            st.rerun()
    
    # Real-time metrics summary
    st.markdown("### 📈 Real-Time Performance Summary")
    
    try:
        # Get performance metrics
        metrics = orchestrator.get_performance_metrics(time_window)
        session_summary = metrics.get('session_summary', {})
        
        if session_summary.get('message'):
            st.info("📊 No metrics available yet. Start using the multi-agent features to see performance data!")
            
            # Show sample metrics layout
            st.markdown("#### 🎯 What You'll See Here:")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Tasks", "0", "0")
            with col2:
                st.metric("Success Rate", "0%", "0%")
            with col3:
                st.metric("Avg Response Time", "0.0s", "0.0s")
            with col4:
                st.metric("Quality Score", "0/10", "0")
            
            return
        
        # Display key metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            total_tasks = session_summary.get('total_tasks', 0)
            st.metric("Total Tasks", total_tasks)
        
        with col2:
            success_rate = session_summary.get('success_rate', 0)
            st.metric("Success Rate", f"{success_rate}%")
        
        with col3:
            avg_time = session_summary.get('avg_execution_time', 0)
            st.metric("Avg Response Time", f"{avg_time:.2f}s")
        
        with col4:
            avg_quality = session_summary.get('avg_quality_score', 0)
            st.metric("Quality Score", f"{avg_quality:.1f}/10")
        
        with col5:
            session_duration = session_summary.get('session_duration_minutes', 0)
            st.metric("Session Duration", f"{session_duration:.1f}m")
        
        # Agent comparison
        st.markdown("### 🤖 Agent Performance Comparison")
        
        agent_stats = metrics.get('agent_statistics', {})
        
        if agent_stats:
            # Create comparison dataframe
            comparison_data = []
            for agent_name, stats in agent_stats.items():
                comparison_data.append({
                    'Agent': agent_name,
                    'Tasks': stats.get('total_tasks', 0),
                    'Success Rate (%)': stats.get('success_rate', 0),
                    'Avg Time (s)': stats.get('avg_execution_time', 0),
                    'Quality Score': stats.get('avg_quality_score', 0),
                    'Total Tokens': stats.get('total_tokens', 0)
                })
            
            df = pd.DataFrame(comparison_data)
            
            if not df.empty:
                # Performance comparison chart
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.bar(df, x='Agent', y='Success Rate (%)', 
                               title="Success Rate by Agent",
                               color='Success Rate (%)',
                               color_continuous_scale='RdYlGn')
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = px.scatter(df, x='Avg Time (s)', y='Quality Score',
                                   size='Tasks', color='Agent',
                                   title="Response Time vs Quality",
                                   hover_data=['Tasks'])
                    st.plotly_chart(fig, use_container_width=True)
                
                # Agent performance table
                st.markdown("#### 📋 Detailed Agent Statistics")
                st.dataframe(df, use_container_width=True)
        
        # Task type analysis
        st.markdown("### 📊 Task Type Performance")
        
        task_analysis = metrics.get('task_analysis', {})
        
        if task_analysis:
            task_data = []
            for task_type, stats in task_analysis.items():
                task_data.append({
                    'Task Type': task_type,
                    'Tasks': stats.get('total_tasks', 0),
                    'Success Rate (%)': stats.get('success_rate', 0),
                    'Avg Time (s)': stats.get('avg_execution_time', 0),
                    'Quality Score': stats.get('avg_quality_score', 0)
                })
            
            task_df = pd.DataFrame(task_data)
            
            if not task_df.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.pie(task_df, values='Tasks', names='Task Type',
                               title="Task Distribution")
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = px.bar(task_df, x='Task Type', y='Avg Time (s)',
                               title="Average Response Time by Task Type")
                    st.plotly_chart(fig, use_container_width=True)
        
        # Error analysis
        st.markdown("### 🚨 Error Analysis")
        
        error_analysis = metrics.get('error_analysis', {})
        
        if error_analysis and not error_analysis.get('message'):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_errors = error_analysis.get('total_errors', 0)
                st.metric("Total Errors", total_errors)
            
            with col2:
                error_rate = error_analysis.get('error_rate', 0)
                st.metric("Error Rate", f"{error_rate}%")
            
            with col3:
                if st.button("📥 Export Error Log"):
                    filename = performance_tracker.export_metrics()
                    st.success(f"Error log exported to {filename}")
            
            # Error breakdown
            errors_by_agent = error_analysis.get('errors_by_agent', {})
            if errors_by_agent:
                st.markdown("#### 🤖 Errors by Agent")
                error_df = pd.DataFrame(list(errors_by_agent.items()), 
                                      columns=['Agent', 'Error Count'])
                fig = px.bar(error_df, x='Agent', y='Error Count',
                           title="Error Count by Agent")
                st.plotly_chart(fig, use_container_width=True)
            
            # Common error messages
            common_errors = error_analysis.get('common_error_messages', {})
            if common_errors:
                st.markdown("#### 💬 Most Common Error Messages")
                for error_msg, count in list(common_errors.items())[:5]:
                    st.markdown(f"• **{count}x** - {error_msg}")
        
        else:
            st.success("🎉 No errors detected in the selected time window!")
        
        # Performance trends
        st.markdown("### 📈 Performance Trends")
        
        if st.button("📊 Generate Trend Analysis"):
            trends = orchestrator.get_agent_trends(hours_back=time_window)
            trend_data = trends.get('trends', [])
            
            if trend_data:
                trend_df = pd.DataFrame(trend_data)
                trend_df['timestamp'] = pd.to_datetime(trend_df['timestamp'])
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.line(trend_df, x='timestamp', y='success_rate',
                                title="Success Rate Over Time")
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = px.line(trend_df, x='timestamp', y='avg_execution_time',
                                title="Response Time Trend")
                    st.plotly_chart(fig, use_container_width=True)
            
            else:
                st.info("Not enough data points for trend analysis. Use the system more to generate trends!")
    
    except Exception as e:
        st.error(f"Error loading performance metrics: {str(e)}")
        st.info("Make sure you have used the multi-agent features to generate performance data.")
    
    # Performance optimization suggestions
    st.markdown("---")
    st.markdown("### 💡 Performance Optimization Suggestions")
    
    with st.expander("🎯 How to Improve Agent Performance"):
        st.markdown("""
        **For Better Success Rates:**
        - Ensure API keys are properly configured
        - Use appropriate chunk sizes for large files
        - Monitor rate limits and adjust request frequency
        
        **For Faster Response Times:**
        - Use parallel processing for large analyses
        - Enable smart chunking for complex files
        - Consider upgrading API tiers for higher limits
        
        **For Higher Quality Scores:**
        - Provide clear, specific analysis requests
        - Use comprehensive analysis mode when needed
        - Leverage specialized agents for domain-specific tasks
        
        **For Lower Error Rates:**
        - Validate input data before analysis
        - Monitor token usage to avoid limits
        - Implement proper error handling in workflows
        """)
    
    # Real-time monitoring setup
    if auto_refresh:
        st.markdown("🔄 Auto-refresh enabled - metrics update automatically")
        
        # Use session state to track refresh interval
        if 'last_refresh' not in st.session_state:
            st.session_state.last_refresh = datetime.now()
        
        # Refresh every 30 seconds
        if (datetime.now() - st.session_state.last_refresh).seconds > 30:
            st.session_state.last_refresh = datetime.now()
            st.rerun()

if __name__ == "__main__":
    main()
