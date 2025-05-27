import streamlit as st
import asyncio
import time
from utils.multi_agent_system import AgentOrchestrator
from utils.parallel_processor import ParallelProcessor
from utils.constants import SUPPORTED_LANGUAGES
from components.sidebar import render_sidebar

st.set_page_config(page_title="Multi-Agent Analysis", page_icon="🤖", layout="wide")

def main():
    render_sidebar()

    st.title("🤖 Multi-Agent AI Analysis")
    st.markdown("Leverage collaborative AI agents for advanced code analysis and enhancement")

    # Initialize the agent orchestrator and parallel processor
    try:
        orchestrator = AgentOrchestrator()
        parallel_processor = ParallelProcessor()
    except Exception as e:
        st.error(f"Failed to initialize multi-agent system: {str(e)}")
        st.info("Please ensure you have OpenAI or Groq API keys configured for multi-agent features")
        return

    # Feature overview
    with st.expander("🌟 Multi-Agent Features"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            **Specialized AI Agents:**
            - 🔒 Security Expert - Vulnerability analysis
            - ⚡ Performance Optimizer - Bottleneck detection
            - ✨ Quality Assurance - Best practices review
            - 📚 Documentation Specialist - Auto-documentation
            """)

        with col2:
            st.markdown("""
            **Advanced Capabilities:**
            - 🏗️ Architecture Analyst - System design review
            - 🔄 Translation Expert - Multi-language conversion
            - 📊 Large File Handling - Intelligent chunking
            - 🤝 Collaborative Analysis - Agent teamwork
            - ⚡ Parallel Processing - True multi-threaded analysis
            - 🛡️ Rate Limit Management - Smart API usage
            """)

    # Analysis type selection
    st.markdown("### 🎯 Analysis Type")

    analysis_mode = st.selectbox(
        "Choose Analysis Mode",
        [
            "Comprehensive Code Review",
            "Security-Focused Analysis", 
            "Performance Optimization",
            "Architecture Assessment",
            "Documentation Generation",
            "Multi-Language Translation"
        ],
        help="Select the type of multi-agent analysis to perform"
    )

    # File input section
    st.markdown("### 📁 Code Input")

    input_method = st.radio(
        "Input Method",
        ["File Upload", "Direct Input", "GitHub Repository"],
        horizontal=True
    )

    code_content = ""
    filename = ""
    language = "Python"

    if input_method == "File Upload":
        uploaded_file = st.file_uploader(
            "Upload your code file",
            type=['py', 'js', 'ts', 'java', 'cpp', 'c', 'rs', 'go', 'php', 'rb', 'jsx', 'tsx'],
            help="Upload code files up to 10MB for multi-agent analysis"
        )

        if uploaded_file is not None:
            try:
                code_content = uploaded_file.read().decode('utf-8')
                filename = uploaded_file.name
                st.success(f"✅ Loaded {filename} ({len(code_content)} characters)")

                # Auto-detect language from file extension
                ext_to_lang = {
                    '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript',
                    '.java': 'Java', '.cpp': 'C++', '.c': 'C', '.rs': 'Rust',
                    '.go': 'Go', '.php': 'PHP', '.rb': 'Ruby'
                }

                file_ext = '.' + filename.split('.')[-1] if '.' in filename else ''
                language = ext_to_lang.get(file_ext, 'Python')

                # Show file preview for large files
                if len(code_content) > 3000:
                    st.info(f"🚀 Large file detected ({len(code_content)} chars) - Parallel processing will be used for optimal performance")
                    with st.expander("📄 File Preview (first 1000 characters)"):
                        st.code(code_content[:1000] + "...", language=language.lower())
                elif len(code_content) > 1000:
                    st.success(f"📊 Medium file ({len(code_content)} chars) - Multi-agent analysis with smart chunking")
                else:
                    st.info(f"📄 Small file ({len(code_content)} chars) - Direct analysis")

            except Exception as e:
                st.error(f"Error reading file: {str(e)}")

    elif input_method == "Direct Input":
        language = st.selectbox("Programming Language", SUPPORTED_LANGUAGES)

        code_content = st.text_area(
            "Enter your code:",
            height=400,
            placeholder=f"Paste your {language} code here for multi-agent analysis..."
        )

        filename = f"input_code.{language.lower()}"

    else:  # GitHub Repository
        st.info("🚧 GitHub repository analysis with multi-agents coming soon!")
        st.markdown("For now, please use file upload or direct input methods.")
        return

    # Analysis options
    with st.expander("⚙️ Advanced Options"):
        col1, col2 = st.columns(2)

        with col1:
            use_parallel = st.checkbox(
                "Parallel Agent Processing", 
                value=True,
                help="Run multiple agents simultaneously for faster analysis"
            )

            comprehensive_mode = st.checkbox(
                "Comprehensive Analysis",
                value=len(code_content) > 1000,
                help="Enable detailed analysis with all specialist agents"
            )

            chunk_large_files = st.checkbox(
                "Smart File Chunking",
                value=True,
                help="Automatically split large files for better analysis"
            )

        with col2:
            max_agents = st.slider(
                "Maximum Agents",
                min_value=2,
                max_value=6,
                value=4,
                help="Number of agents to use in collaborative analysis"
            )

            analysis_depth = st.selectbox(
                "Analysis Depth",
                ["Standard", "Detailed", "Expert-Level"],
                index=1,
                help="Depth of analysis to perform"
            )

    # Translation options (if translation mode selected)
    if "Translation" in analysis_mode:
        st.markdown("### 🔄 Translation Settings")

        col1, col2 = st.columns(2)
        with col1:
            source_lang = st.selectbox("Source Language", SUPPORTED_LANGUAGES, index=0)
        with col2:
            target_lang = st.selectbox("Target Language", SUPPORTED_LANGUAGES, index=1)

        if source_lang == target_lang:
            st.warning("⚠️ Source and target languages must be different")
            return

    # Analysis button
    if st.button("🚀 Start Multi-Agent Analysis", type="primary", use_container_width=True):
        if not code_content.strip():
            st.error("❌ Please provide code to analyze")
            return

        # Prepare analysis options
        analysis_options = {
            'filename': filename,
            'use_multi_agent': True,
            'comprehensive_analysis': comprehensive_mode,
            'parallel_processing': use_parallel,
            'max_agents': max_agents,
            'analysis_depth': analysis_depth,
            'chunk_large_files': chunk_large_files
        }

        # Show progress and perform analysis
        with st.spinner("🤖 Multi-agent analysis in progress..."):
            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                # Determine if we should use parallel processing
                use_parallel = len(code_content) > 3000 or use_parallel

                if use_parallel:
                    # Use parallel processing for large files
                    status_text.text("🚀 Initializing parallel processing system...")
                    progress_bar.progress(10)

                    # Create processing tasks
                    if "Translation" in analysis_mode:
                        # Translation doesn't need chunking currently
                        status_text.text("🔄 Processing translation with specialized agents...")
                        progress_bar.progress(60)

                        result = asyncio.run(orchestrator.enhanced_translation(
                            code_content, source_lang, target_lang
                        ))
                    else:
                        # Create parallel analysis tasks
                        status_text.text("📊 Creating analysis tasks for parallel processing...")
                        progress_bar.progress(20)

                        analysis_type = analysis_mode.lower().replace(' ', '_').replace('-', '_')
                        if 'security' in analysis_type:
                            task_type = "security"
                        elif 'performance' in analysis_type:
                            task_type = "performance"
                        else:
                            task_type = "comprehensive"

                        tasks = parallel_processor.create_processing_tasks(
                            code_content, language, task_type
                        )

                        status_text.text(f"⚡ Processing {len(tasks)} tasks in parallel...")
                        progress_bar.progress(40)

                        # Define progress callback
                        def update_progress(completed, total, latest_result):
                            progress = 40 + int((completed / total) * 40)
                            progress_bar.progress(progress)
                            status_text.text(f"⚡ Completed {completed}/{total} parallel tasks...")

                        # Run parallel processing
                        parallel_results = asyncio.run(parallel_processor.process_parallel(
                            tasks, progress_callback=update_progress
                        ))

                        status_text.text("🔗 Combining results from parallel analysis...")
                        progress_bar.progress(85)

                        # Combine results
                        result = parallel_processor.combine_chunk_results(parallel_results)
                        result['used_parallel_processing'] = True
                        result['processing_metrics'] = parallel_processor.get_processing_metrics()

                else:
                    # Standard processing for smaller files
                    status_text.text("Initializing agent team...")
                    progress_bar.progress(20)
                    time.sleep(0.5)

                    status_text.text("Distributing analysis tasks...")
                    progress_bar.progress(40)
                    time.sleep(0.5)

                    if "Translation" in analysis_mode:
                        status_text.text("Agents collaborating on translation...")
                        progress_bar.progress(60)

                        result = asyncio.run(orchestrator.enhanced_translation(
                            code_content, source_lang, target_lang
                        ))
                    else:
                        status_text.text("Agents analyzing code collaboratively...")
                        progress_bar.progress(60)

                        result = asyncio.run(orchestrator.enhanced_code_review(
                            code_content, language, analysis_options
                        ))

                status_text.text("✨ Analysis complete - Preparing results...")
                progress_bar.progress(100)
                time.sleep(0.5)

                # Display results
                if result and not result.get('error')):
                    st.success("✅ Multi-agent analysis completed successfully!")

                    # Show analysis results
                    display_multi_agent_results(result, analysis_mode)

                else:
                    st.error(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")

                    # Show fallback message
                    if 'API keys' in str(result.get('error', '')):
                        st.info("""
                        💡 **To enable multi-agent analysis, please configure API keys:**

                        **Option 1: OpenAI (Recommended)**
                        - Get API key from [OpenAI Platform](https://platform.openai.com)
                        - Set environment variable: `OPENAI_API_KEY`

                        **Option 2: Groq (Alternative)**
                        - Get API key from [Groq Console](https://console.groq.com)
                        - Set environment variable: `GROQ_API_KEY`
                        """)

            except Exception as e:
                st.error(f"❌ Multi-agent analysis error: {str(e)}")

    # Enhancement suggestions
    st.markdown("---")
    st.markdown("### 🚀 Suggested Enhancements")

    enhancements = orchestrator.get_enhancement_suggestions()

    for enhancement in enhancements[:4]:  # Show top 4 suggestions
        with st.expander(f"💡 {enhancement['title']} ({enhancement['priority']} Priority)"):
            st.markdown(enhancement['description'])

def display_multi_agent_results(result: dict, analysis_mode: str):
    """Display results from multi-agent analysis"""

    if "Translation" in analysis_mode:
        # Translation results
        st.markdown("### 🔄 Translation Results")

        if result.get('translated_code'):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### Original Code")
                st.code(result.get('original_code', 'Original code not available'))

            with col2:
                st.markdown("#### Translated Code")
                st.code(result.get('translated_code', 'Translation not available'))

        if result.get('translation_notes'):
            st.markdown("#### 📝 Translation Notes")
            st.info(result['translation_notes'])

        if result.get('agent_collaboration'):
            st.success("✨ Enhanced with multi-agent collaboration")

    else:
        # Code analysis results
        st.markdown("### 📊 Analysis Results")

        # Overall metrics
        if result.get('overall_score'):
            col1, col2, col3 = st.columns(3)

            with col1:
                score = result['overall_score']
                if score >= 80:
                    st.success(f"🎯 Quality Score: {score}/100")
                elif score >= 60:
                    st.warning(f"⚠️ Quality Score: {score}/100")
                else:
                    st.error(f"❌ Quality Score: {score}/100")

            with col2:
                if result.get('chunks_analyzed'):
                    st.metric("File Chunks", result['chunks_analyzed'])
                else:
                    st.metric("Analysis Type", "Complete File")

            with col3:
                st.metric("Agent Enhanced", "Yes" if result.get('enhanced_with_agents') else "No")

        # Recommendations
        if result.get('recommendations'):
            st.markdown("#### 💡 Multi-Agent Recommendations")
            for i, rec in enumerate(result['recommendations'], 1):
                st.markdown(f"{i}. {rec}")

        # Issues found
        if result.get('combined_issues'):
            st.markdown("#### 🔍 Issues Identified by Agents")

            for issue in result['combined_issues']:
                severity_color = {
                    'critical': '🔴',
                    'high': '🟠',
                    'medium': '🟡',
                    'low': '🟢'
                }.get(issue.get('severity', 'medium').lower(), '⚪')

                st.markdown(f"{severity_color} **{issue.get('type', 'General')}** - {issue.get('description', 'No description')}")
                if issue.get('agent'):
                    st.caption(f"Identified by: {issue['agent']}")

        # Parallel processing metrics
        if result.get('used_parallel_processing'):
            st.success("🚀 Enhanced with true parallel processing for optimal performance!")

            metrics = result.get('processing_metrics', {})
            if metrics:
                st.markdown("#### ⚡ Parallel Processing Performance")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Tasks Processed", metrics.get('total_tasks', 0))

                with col2:
                    st.metric("Success Rate", f"{metrics.get('success_rate', 0)}%")

                with col3:
                    st.metric("Avg Task Time", f"{metrics.get('average_processing_time', 0):.2f}s")

                with col4:
                    efficiency = metrics.get('parallel_efficiency', 1.0)
                    st.metric("Parallel Efficiency", f"{efficiency:.1f}x")

                # Show efficiency explanation
                if efficiency > 1.5:
                    st.success(f"🎯 Excellent parallel efficiency! {efficiency:.1f}x faster than sequential processing")
                elif efficiency > 1.0:
                    st.info(f"✅ Good parallel performance - {efficiency:.1f}x speedup achieved")

        # Agent collaboration info
        elif result.get('enhanced_with_agents'):
            st.success("✨ Analysis enhanced with specialized AI agents working together")

        # Chunk analysis details (for large files)
        if result.get('chunk_details'):
            with st.expander("📄 Detailed Chunk Analysis"):
                for chunk in result['chunk_details']:
                    chunk_id = chunk.get('chunk_id', 'Unknown')
                    processing_time = chunk.get('processing_time', 0)
                    issues_count = chunk.get('issues_found', 0)

                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{chunk_id}** - {issues_count} issues found")
                    with col2:
                        st.caption(f"{processing_time:.2f}s")

                    if chunk.get('success'):
                        st.success(f"✅ {chunk_id} processed successfully")
                    else:
                        st.error(f"❌ {chunk_id} failed to process")

if __name__ == "__main__":
    main()