import streamlit as st
import os
from utils.constants import SUPPORTED_LANGUAGES, COLORS, FEATURES, APP_TITLE, APP_VERSION

def render_sidebar():
    """
    Render the main sidebar with navigation and configuration status
    """
    
    with st.sidebar:
        # Application header
        st.markdown(f"# 🚀 {APP_TITLE}")
        st.markdown(f"*Version {APP_VERSION}*")
        st.markdown("---")
        
        # Navigation menu
        st.markdown("### 📍 Navigation")
        
        # Main pages navigation
        nav_options = {
            "🏠 Home": "app.py",
            "🔄 Code Translation": "pages/1_Code_Translation.py", 
            "🔍 Code Review": "pages/2_Code_Review.py",
            "📚 Documentation": "pages/3_Documentation_Generator.py",
            "🐙 GitHub Analysis": "pages/4_GitHub_Analysis.py",
            "🤖 Multi-Agent AI": "pages/5_Multi_Agent_Analysis.py",
            "🎯 AI Companion": "pages/7_AI_Companion.py",
            "⚡ Enhancements": "pages/6_Enhancements_Overview.py"
        }
        
        # Get current page
        current_page = st.session_state.get('current_page', 'Home')
        
        # Navigation buttons
        for label, page_path in nav_options.items():
            if st.button(label, use_container_width=True, key=f"nav_{label}"):
                if "Home" not in label:
                    st.switch_page(page_path)
                else:
                    # Navigate to home
                    st.rerun()
        
        st.markdown("---")
        
        # Configuration status
        st.markdown("### ⚙️ Configuration")
        
        # Check API keys and services
        groq_key = st.session_state.get('groq_api_key') or os.getenv("GROQ_API_KEY")
        github_token = os.getenv("GITHUB_TOKEN")
        
        # Groq API status
        if groq_key:
            st.success("✅ Groq API Connected")
            
            # Option to update API key
            with st.expander("🔑 Update API Key"):
                new_api_key = st.text_input(
                    "Enter new Groq API Key",
                    type="password",
                    placeholder="gsk_...",
                    help="Enter your new Groq API key to update"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Update Key", use_container_width=True):
                        if new_api_key and new_api_key.strip():
                            # Update session state
                            st.session_state['groq_api_key'] = new_api_key.strip()
                            st.success("API key updated for this session!")
                            st.rerun()
                        else:
                            st.error("Please enter a valid API key")
                
                with col2:
                    if st.button("Clear Key", use_container_width=True):
                        if 'groq_api_key' in st.session_state:
                            del st.session_state['groq_api_key']
                        st.warning("API key cleared from session")
                        st.rerun()
        else:
            st.error("❌ Groq API Key Missing")
            with st.expander("ℹ️ Setup API Key"):
                st.markdown("""
                **Option 1: Set Environment Variable**
                1. Get API key from [Groq Console](https://console.groq.com)
                2. Set environment variable: `GROQ_API_KEY=your_key`
                3. Restart the application
                
                **Option 2: Enter Key Below**
                """)
                
                # Allow entering API key directly
                new_api_key = st.text_input(
                    "Enter Groq API Key",
                    type="password",
                    placeholder="gsk_...",
                    help="Enter your Groq API key for this session"
                )
                
                if st.button("Set API Key", use_container_width=True):
                    if new_api_key and new_api_key.strip():
                        st.session_state['groq_api_key'] = new_api_key.strip()
                        st.success("API key set for this session!")
                        st.rerun()
                    else:
                        st.error("Please enter a valid API key")
        
        # GitHub token status
        if github_token:
            st.success("✅ GitHub Token Set")
        else:
            st.warning("⚠️ GitHub Token Optional")
            with st.expander("ℹ️ GitHub Setup"):
                st.markdown("""
                **For private repositories:**
                1. Generate token at [GitHub Settings](https://github.com/settings/tokens)
                2. Set environment variable: `GITHUB_TOKEN=your_token`
                3. Required scopes: `repo` for private repos
                """)
        
        st.markdown("---")
        
        # Quick stats and info
        st.markdown("### 📊 Quick Info")
        
        # Supported languages count
        st.info(f"**Languages Supported:** {len(SUPPORTED_LANGUAGES)}")
        
        # Feature status
        enabled_features = sum(1 for feature, enabled in FEATURES.items() if enabled)
        st.info(f"**Features Available:** {enabled_features}")
        
        # Quick language reference
        with st.expander("🔧 Supported Languages"):
            cols = st.columns(2)
            for i, lang in enumerate(SUPPORTED_LANGUAGES):
                with cols[i % 2]:
                    st.markdown(f"• {lang}")
        
        st.markdown("---")
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        
        # Clear session state
        if st.button("🗑️ Clear Session", use_container_width=True):
            # Clear all session state except navigation
            keys_to_clear = [k for k in st.session_state.keys() if not k.startswith('nav_')]
            for key in keys_to_clear:
                del st.session_state[key]
            st.success("Session cleared!")
            st.rerun()
        
        # Export session info
        if st.button("📋 Session Info", use_container_width=True):
            show_session_info()
        
        st.markdown("---")
        
        # Help and tips
        st.markdown("### 💡 Tips")
        
        # Rotating tips based on current page or random
        tips = [
            "💡 Use meaningful variable names for better code translation",
            "🔍 Enable all review categories for comprehensive analysis",
            "📚 Include comments in your code for better documentation",
            "🐙 Start with smaller repositories to test GitHub analysis",
            "⚡ Use file extension filters to focus analysis",
            "🚀 Check configuration status before starting analysis"
        ]
        
        # Show a random tip or based on session state
        import random
        tip_index = hash(str(st.session_state)) % len(tips)
        st.info(tips[tip_index])
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666; font-size: 0.8em;'>
        Powered by Groq LLM<br>
        Built with Streamlit
        </div>
        """, unsafe_allow_html=True)

def show_session_info():
    """
    Display session information in a modal-like expander
    """
    with st.sidebar.expander("📋 Session Information", expanded=True):
        st.markdown("**Current Session State:**")
        
        # Filter relevant session state info
        relevant_keys = [
            'current_page', 'last_analysis', 'files_processed', 
            'translation_count', 'review_count'
        ]
        
        session_info = {}
        for key in relevant_keys:
            if key in st.session_state:
                session_info[key] = st.session_state[key]
        
        if session_info:
            for key, value in session_info.items():
                st.text(f"{key}: {value}")
        else:
            st.text("No session data available")
        
        # Environment info
        st.markdown("**Environment:**")
        st.text(f"Groq API: {'✅' if os.getenv('GROQ_API_KEY') else '❌'}")
        st.text(f"GitHub Token: {'✅' if os.getenv('GITHUB_TOKEN') else '❌'}")

def render_feature_sidebar(feature_name: str, feature_specific_content: dict = None):
    """
    Render a feature-specific sidebar with additional controls
    
    Args:
        feature_name: Name of the current feature
        feature_specific_content: Additional content specific to the feature
    """
    
    # First render the main sidebar
    render_sidebar()
    
    # Add feature-specific content if provided
    if feature_specific_content:
        with st.sidebar:
            st.markdown("---")
            st.markdown(f"### 🔧 {feature_name} Options")
            
            # Render feature-specific controls
            for section_name, content in feature_specific_content.items():
                if isinstance(content, dict):
                    with st.expander(section_name):
                        for key, value in content.items():
                            st.markdown(f"**{key}:** {value}")
                else:
                    st.markdown(f"**{section_name}:** {content}")

def render_progress_sidebar(current_step: str, total_steps: int, current_step_num: int):
    """
    Render a progress indicator in the sidebar
    
    Args:
        current_step: Description of current step
        total_steps: Total number of steps
        current_step_num: Current step number (1-indexed)
    """
    
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📈 Progress")
        
        # Progress bar
        progress = current_step_num / total_steps
        st.progress(progress)
        
        # Step indicator
        st.markdown(f"**Step {current_step_num} of {total_steps}**")
        st.markdown(f"*{current_step}*")
        
        # Steps checklist
        with st.expander("📋 Steps Overview"):
            steps = [
                "Initialize Analysis",
                "Process Files", 
                "Generate Results",
                "Export Documentation"
            ]
            
            for i, step in enumerate(steps[:total_steps], 1):
                if i < current_step_num:
                    st.markdown(f"✅ {i}. {step}")
                elif i == current_step_num:
                    st.markdown(f"⏳ {i}. {step}")
                else:
                    st.markdown(f"⏸️ {i}. {step}")

def render_analysis_sidebar(analysis_results: dict = None):
    """
    Render sidebar with analysis-specific information
    
    Args:
        analysis_results: Results from code analysis
    """
    
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📊 Analysis Summary")
        
        if analysis_results:
            # Show key metrics
            metrics = analysis_results.get('metrics', {})
            
            if 'lines_of_code' in metrics:
                st.metric("Lines Analyzed", metrics['lines_of_code'])
            
            if 'function_count' in metrics:
                st.metric("Functions Found", metrics['function_count'])
            
            if 'class_count' in metrics:
                st.metric("Classes Found", metrics['class_count'])
            
            # Show findings summary
            findings = analysis_results.get('findings', [])
            if findings:
                st.markdown("**Issues Found:**")
                
                severity_counts = {}
                for finding in findings:
                    severity = finding.get('severity', 'Unknown')
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
                for severity, count in severity_counts.items():
                    emoji = {
                        'Critical': '🔴',
                        'High': '🟠',
                        'Medium': '🟡', 
                        'Low': '🟢'
                    }.get(severity, '⚪')
                    
                    st.markdown(f"{emoji} {severity}: {count}")
        else:
            st.info("No analysis results yet")
        
        # Analysis tips
        with st.expander("💡 Analysis Tips"):
            st.markdown("""
            - Review critical issues first
            - Focus on security vulnerabilities  
            - Consider performance optimizations
            - Improve code documentation
            """)

def get_sidebar_state():
    """
    Get current sidebar state information
    
    Returns:
        Dictionary with sidebar state
    """
    
    return {
        'groq_configured': bool(os.getenv("GROQ_API_KEY")),
        'github_configured': bool(os.getenv("GITHUB_TOKEN")),
        'supported_languages': len(SUPPORTED_LANGUAGES),
        'enabled_features': sum(1 for feature, enabled in FEATURES.items() if enabled),
        'current_page': st.session_state.get('current_page', 'Home')
    }

def update_sidebar_state(key: str, value):
    """
    Update sidebar state
    
    Args:
        key: State key to update
        value: New value
    """
    
    if f"sidebar_{key}" not in st.session_state:
        st.session_state[f"sidebar_{key}"] = value
    else:
        st.session_state[f"sidebar_{key}"] = value
