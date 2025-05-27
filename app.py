import streamlit as st
import os
from components.sidebar import render_sidebar
from utils.constants import SUPPORTED_LANGUAGES, APP_TITLE, APP_DESCRIPTION

# Configure page
st.set_page_config(
    page_title="Developer Productivity Suite",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application entry point"""
    
    # Render sidebar
    render_sidebar()
    
    # Main page content
    st.title("🚀 Developer Productivity Suite")
    st.markdown("### Powered by Groq LLM for Intelligent Code Analysis")
    
    # Hero section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        Welcome to your comprehensive developer productivity toolkit. This suite provides:
        
        - **Code Translation**: Convert code between programming languages with intelligent syntax mapping
        - **Code Review**: Automated analysis for best practices, security, and complexity assessment  
        - **Documentation Generator**: Create comprehensive technical documentation from your codebase
        - **GitHub Analysis**: Direct repository analysis with efficient large file handling
        """)
        
        # Feature showcase
        st.markdown("#### 🔧 Supported Languages")
        
        # Display supported languages in a grid
        lang_cols = st.columns(4)
        for i, lang in enumerate(SUPPORTED_LANGUAGES):
            with lang_cols[i % 4]:
                st.markdown(f"• {lang}")
    
    with col2:
        st.image("https://pixabay.com/get/g86a72474536506144f546326a124599ccce0fcf8ff36189e62faaa0edf094443b6520eb7c4ca9bec5d87366bcb1c72ba357aefb6b956a44b3c30a6961079e367_1280.jpg", 
                caption="Developer Workspace", use_column_width=True)
    
    # Quick start section
    st.markdown("---")
    st.markdown("#### 🚀 Quick Start")
    
    feature_cols = st.columns(5)
    
    with feature_cols[0]:
        if st.button("🔄 Code Translation", use_container_width=True):
            st.switch_page("pages/1_Code_Translation.py")
        st.markdown("Convert code between languages")
    
    with feature_cols[1]:
        if st.button("🔍 Code Review", use_container_width=True):
            st.switch_page("pages/2_Code_Review.py")
        st.markdown("Automated code analysis")
    
    with feature_cols[2]:
        if st.button("📚 Documentation", use_container_width=True):
            st.switch_page("pages/3_Documentation_Generator.py")
        st.markdown("Generate technical docs")
    
    with feature_cols[3]:
        if st.button("🐙 GitHub Analysis", use_container_width=True):
            st.switch_page("pages/4_GitHub_Analysis.py")
        st.markdown("Repository analysis")
    
    with feature_cols[4]:
        if st.button("🤖 Multi-Agent AI", use_container_width=True):
            st.switch_page("pages/5_Multi_Agent_Analysis.py")
        st.markdown("Collaborative AI agents")
    
    # Configuration check
    st.markdown("---")
    st.markdown("#### ⚙️ Configuration Status")
    
    # Check API keys
    groq_key = st.session_state.get('groq_api_key') or os.getenv("GROQ_API_KEY")
    github_token = os.getenv("GITHUB_TOKEN")
    
    config_cols = st.columns(2)
    
    with config_cols[0]:
        if groq_key:
            st.success("✅ Groq API Key configured")
        else:
            st.error("❌ Groq API Key not found in environment variables")
            st.info("Please set GROQ_API_KEY environment variable")
    
    with config_cols[1]:
        if github_token:
            st.success("✅ GitHub Token configured")
        else:
            st.warning("⚠️ GitHub Token not configured (optional for public repos)")
            st.info("Set GITHUB_TOKEN for private repository access")

if __name__ == "__main__":
    main()
