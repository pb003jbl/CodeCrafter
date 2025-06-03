import streamlit as st
from utils.groq_client import GroqClient
from utils.code_analyzer import CodeAnalyzer
from utils.constants import SUPPORTED_LANGUAGES
from components.sidebar import render_sidebar
import time

st.set_page_config(page_title="Code Review", page_icon="🔍", layout="wide")

def main():
    render_sidebar()
    
    st.title("🔍 Automated Code Review")
    st.markdown("Get comprehensive code analysis including best practices, security, and complexity assessment")
    
    # Initialize clients
    try:
        groq_client = GroqClient()
        code_analyzer = CodeAnalyzer(groq_client)
    except Exception as e:
        st.error(f"Failed to initialize services: {str(e)}")
        st.stop()
    
    # Language selection
    language = st.selectbox(
        "Programming Language",
        SUPPORTED_LANGUAGES,
        help="Select the programming language of your code"
    )
    
    # Code input methods
    input_method = st.radio(
        "Input Method",
        ["File Upload", "Direct Input"],
        horizontal=True
    )
    
    code_input = ""
    
    if input_method == "File Upload":
        uploaded_file = st.file_uploader(
            "Upload your code file",
            type=['py', 'js', 'java', 'cpp', 'c', 'rs', 'go', 'php', 'rb', 'ts', 'jsx', 'tsx','r'],
            help="Upload a code file for review"
        )
        
        if uploaded_file is not None:
            try:
                code_input = uploaded_file.read().decode('utf-8')
                st.success(f"✅ Loaded {uploaded_file.name} ({len(code_input)} characters)")
                
                # Show file preview
                with st.expander("📄 File Preview"):
                    st.code(code_input[:1000] + ("..." if len(code_input) > 1000 else ""), language=language.lower())
                    
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
    else:
        code_input = st.text_area(
            "Enter your code here:",
            height=400,
            placeholder=f"Paste your {language} code here for review..."
        )
    
    # Review options
    with st.expander("🔧 Review Options"):
        col1, col2 = st.columns(2)
        
        with col1:
            check_security = st.checkbox("Security Analysis", value=True, help="Check for security vulnerabilities")
            check_performance = st.checkbox("Performance Analysis", value=True, help="Analyze performance bottlenecks")
            check_style = st.checkbox("Code Style", value=True, help="Check coding standards and style")
        
        with col2:
            check_complexity = st.checkbox("Complexity Analysis", value=True, help="Assess code complexity")
            check_maintainability = st.checkbox("Maintainability", value=True, help="Evaluate code maintainability")
            check_documentation = st.checkbox("Documentation", value=True, help="Check documentation quality")
        
        severity_filter = st.selectbox(
            "Minimum Severity Level",
            ["All Issues", "Low", "Medium", "High", "Critical"],
            index=0,
            help="Filter issues by severity level"
        )
    
    # Review button
    if st.button("🔍 Start Code Review", type="primary", use_container_width=True):
        if not code_input.strip():
            st.error("❌ Please provide code to review")
            return
        
        # Create analysis options
        analysis_options = {
            'security': check_security,
            'performance': check_performance,
            'style': check_style,
            'complexity': check_complexity,
            'maintainability': check_maintainability,
            'documentation': check_documentation,
            'severity_filter': severity_filter
        }
        
        with st.spinner("Analyzing code... This may take a moment"):
            try:
                # Perform code review
                review_result = code_analyzer.review_code(
                    code=code_input,
                    language=language,
                    options=analysis_options
                )
                
                if review_result:
                    st.success("✅ Code review completed!")
                    
                    # Display overall score
                    if 'overall_score' in review_result:
                        score = review_result['overall_score']
                        col1, col2, col3 = st.columns([1, 2, 1])
                        
                        with col2:
                            # Score display with color coding
                            if score >= 80:
                                st.success(f"🎯 Overall Score: {score}/100 (Excellent)")
                            elif score >= 60:
                                st.warning(f"⚠️ Overall Score: {score}/100 (Good)")
                            else:
                                st.error(f"❌ Overall Score: {score}/100 (Needs Improvement)")
                    
                    # Metrics dashboard
                    st.markdown("### 📊 Analysis Summary")
                    
                    metrics = review_result.get('metrics', {})
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(
                            "Critical Issues",
                            metrics.get('critical_issues', 0),
                            delta=None
                        )
                    
                    with col2:
                        st.metric(
                            "Security Issues", 
                            metrics.get('security_issues', 0),
                            delta=None
                        )
                    
                    with col3:
                        st.metric(
                            "Code Complexity",
                            metrics.get('complexity_score', 'N/A'),
                            delta=None
                        )
                    
                    with col4:
                        st.metric(
                            "Lines of Code",
                            len(code_input.splitlines()),
                            delta=None
                        )
                    
                    # Detailed findings
                    if 'findings' in review_result:
                        st.markdown("### 🔍 Detailed Findings")
                        
                        findings = review_result['findings']
                        
                        # Group findings by category
                        categories = {}
                        for finding in findings:
                            category = finding.get('category', 'General')
                            if category not in categories:
                                categories[category] = []
                            categories[category].append(finding)
                        
                        # Display findings by category
                        for category, category_findings in categories.items():
                            with st.expander(f"📂 {category} ({len(category_findings)} issues)"):
                                for i, finding in enumerate(category_findings):
                                    severity = finding.get('severity', 'Unknown')
                                    
                                    # Severity badge
                                    severity_color = {
                                        'Critical': '🔴',
                                        'High': '🟠', 
                                        'Medium': '🟡',
                                        'Low': '🟢'
                                    }.get(severity, '⚪')
                                    
                                    st.markdown(f"**{severity_color} {finding.get('title', 'Issue')}** ({severity})")
                                    st.markdown(f"📝 {finding.get('description', 'No description available')}")
                                    
                                    if finding.get('suggestion'):
                                        st.info(f"💡 **Suggestion:** {finding['suggestion']}")
                                    
                                    if finding.get('line_number'):
                                        st.caption(f"📍 Line {finding['line_number']}")
                                    
                                    st.markdown("---")
                    
                    # Recommendations
                    if 'recommendations' in review_result:
                        st.markdown("### 💡 Recommendations")
                        for i, rec in enumerate(review_result['recommendations'], 1):
                            st.markdown(f"{i}. {rec}")
                    
                    # Export report
                    st.markdown("### 📄 Export Report")
                    
                    # Generate report text
                    report_text = f"""
# Code Review Report

## Summary
- Overall Score: {review_result.get('overall_score', 'N/A')}/100
- Language: {language}
- Lines of Code: {len(code_input.splitlines())}
- Analysis Date: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Metrics
- Critical Issues: {metrics.get('critical_issues', 0)}
- Security Issues: {metrics.get('security_issues', 0)}
- Complexity Score: {metrics.get('complexity_score', 'N/A')}

## Findings
"""
                    
                    if 'findings' in review_result:
                        for finding in review_result['findings']:
                            report_text += f"""
### {finding.get('title', 'Issue')} ({finding.get('severity', 'Unknown')})
- **Description:** {finding.get('description', 'No description')}
- **Suggestion:** {finding.get('suggestion', 'No suggestion provided')}
- **Line:** {finding.get('line_number', 'N/A')}
"""
                    
                    st.download_button(
                        label="📥 Download Report",
                        data=report_text,
                        file_name=f"code_review_report_{time.strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown"
                    )
                    
                else:
                    st.error("❌ Code review failed. Please try again.")
                    
            except Exception as e:
                st.error(f"❌ Review error: {str(e)}")
    
    # Tips section
    with st.expander("💡 Review Tips"):
        st.markdown("""
        **For comprehensive analysis:**
        - Enable all relevant analysis categories
        - Use well-structured, complete code samples
        - Include context and comments in your code
        
        **Understanding severity levels:**
        - **Critical**: Issues that could cause system failures or security breaches
        - **High**: Significant problems affecting functionality or security
        - **Medium**: Moderate issues affecting code quality or performance
        - **Low**: Minor style or improvement suggestions
        
        **Best practices:**
        - Review code regularly during development
        - Address critical and high severity issues first
        - Use suggestions to improve code quality
        - Consider maintainability for long-term projects
        """)

if __name__ == "__main__":
    main()
