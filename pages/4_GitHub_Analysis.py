import streamlit as st
from utils.groq_client import GroqClient
from utils.github_client import GitHubClient
from utils.code_analyzer import CodeAnalyzer
from components.sidebar import render_sidebar
import time
import io
import zipfile

st.set_page_config(page_title="GitHub Analysis", page_icon="🐙", layout="wide")

def main():
    render_sidebar()
    
    st.title("🐙 GitHub Repository Analysis")
    st.markdown("Analyze GitHub repositories and generate comprehensive documentation")
    
    # Initialize clients
    try:
        groq_client = GroqClient()
        github_client = GitHubClient()
        code_analyzer = CodeAnalyzer(groq_client)
    except Exception as e:
        st.error(f"Failed to initialize services: {str(e)}")
        st.stop()
    
    # Repository input
    st.markdown("### 📍 Repository Information")
    
    input_method = st.radio(
        "Input Method",
        ["Repository URL", "Owner/Repository"],
        horizontal=True
    )
    
    repo_owner = ""
    repo_name = ""
    
    if input_method == "Repository URL":
        repo_url = st.text_input(
            "GitHub Repository URL",
            placeholder="https://github.com/owner/repository",
            help="Enter the full GitHub repository URL"
        )
        
        if repo_url:
            # Parse URL to extract owner and repo
            try:
                # Remove protocol and domain
                url_parts = repo_url.replace("https://github.com/", "").replace("http://github.com/", "")
                url_parts = url_parts.strip("/").split("/")
                
                if len(url_parts) >= 2:
                    repo_owner = url_parts[0]
                    repo_name = url_parts[1]
                    st.success(f"✅ Repository: {repo_owner}/{repo_name}")
                else:
                    st.error("❌ Invalid GitHub URL format")
            except Exception as e:
                st.error(f"❌ Error parsing URL: {str(e)}")
    
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            repo_owner = st.text_input(
                "Repository Owner",
                placeholder="username or organization",
                help="GitHub username or organization name"
            )
        
        with col2:
            repo_name = st.text_input(
                "Repository Name", 
                placeholder="repository-name",
                help="Repository name"
            )
    
    # Analysis options
    if repo_owner and repo_name:
        st.markdown("### ⚙️ Analysis Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            analysis_type = st.selectbox(
                "Analysis Type",
                ["Full Repository", "Specific Files", "Recent Changes"],
                help="Choose what to analyze"
            )
            
            include_docs = st.checkbox(
                "Generate Documentation", 
                value=True,
                help="Generate comprehensive documentation"
            )
            
            include_readme = st.checkbox(
                "Update README", 
                value=False,
                help="Generate enhanced README content"
            )
        
        with col2:
            max_files = st.number_input(
                "Maximum Files to Analyze",
                min_value=1,
                max_value=100,
                value=20,
                help="Limit the number of files to analyze"
            )
            
            file_extensions = st.multiselect(
                "File Extensions to Include",
                [".py", ".js", ".ts", ".java", ".cpp", ".c", ".rs", ".go", ".php", ".rb"],
                default=[".py", ".js", ".ts"],
                help="Select file types to analyze"
            )
        
        # Advanced options
        with st.expander("🔧 Advanced Options"):
            analyze_structure = st.checkbox(
                "Analyze Project Structure", 
                value=True,
                help="Analyze and document project architecture"
            )
            
            analyze_dependencies = st.checkbox(
                "Analyze Dependencies", 
                value=True,
                help="Extract and analyze project dependencies"
            )
            
            analyze_commits = st.checkbox(
                "Analyze Recent Commits", 
                value=False,
                help="Analyze recent commit history for insights"
            )
            
            ignore_patterns = st.text_area(
                "Ignore Patterns (one per line)",
                value="node_modules/\n.git/\n__pycache__/\n*.pyc\n.env",
                help="Files and directories to ignore"
            )
        
        # Repository info display
        with st.spinner("Fetching repository information..."):
            try:
                repo_info = github_client.get_repository_info(repo_owner, repo_name)
                
                if repo_info:
                    st.markdown("### 📊 Repository Overview")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Stars", repo_info.get('stargazers_count', 0))
                    
                    with col2:
                        st.metric("Forks", repo_info.get('forks_count', 0))
                    
                    with col3:
                        st.metric("Issues", repo_info.get('open_issues_count', 0))
                    
                    with col4:
                        size_mb = repo_info.get('size', 0) / 1024  # Convert KB to MB
                        st.metric("Size (MB)", f"{size_mb:.1f}")
                    
                    # Repository details
                    with st.expander("📋 Repository Details"):
                        st.markdown(f"**Description:** {repo_info.get('description', 'No description available')}")
                        st.markdown(f"**Language:** {repo_info.get('language', 'Not specified')}")
                        st.markdown(f"**Created:** {repo_info.get('created_at', 'Unknown')}")
                        st.markdown(f"**Updated:** {repo_info.get('updated_at', 'Unknown')}")
                        
                        if repo_info.get('homepage'):
                            st.markdown(f"**Homepage:** {repo_info['homepage']}")
                        
                        if repo_info.get('topics'):
                            st.markdown(f"**Topics:** {', '.join(repo_info['topics'])}")
                
            except Exception as e:
                st.warning(f"⚠️ Could not fetch repository info: {str(e)}")
        
        # Analysis button
        if st.button("🔍 Start Repository Analysis", type="primary", use_container_width=True):
            
            analysis_options = {
                'analysis_type': analysis_type.lower().replace(' ', '_'),
                'include_docs': include_docs,
                'include_readme': include_readme,
                'max_files': max_files,
                'file_extensions': file_extensions,
                'analyze_structure': analyze_structure,
                'analyze_dependencies': analyze_dependencies,
                'analyze_commits': analyze_commits,
                'ignore_patterns': [p.strip() for p in ignore_patterns.split('\n') if p.strip()]
            }
            
            with st.spinner("Analyzing repository... This may take several minutes"):
                try:
                    # Get repository files
                    files_data = github_client.get_repository_files(
                        repo_owner, 
                        repo_name,
                        max_files=max_files,
                        file_extensions=file_extensions,
                        ignore_patterns=analysis_options['ignore_patterns']
                    )
                    
                    if not files_data:
                        st.error("❌ No files found or repository is not accessible")
                        return
                    
                    st.success(f"✅ Found {len(files_data)} files to analyze")
                    
                    # Progress tracking
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    analysis_results = {}
                    
                    # Analyze each file
                    for i, (file_path, file_content) in enumerate(files_data.items()):
                        status_text.text(f"Analyzing {file_path}...")
                        progress_bar.progress((i + 1) / len(files_data))
                        
                        try:
                            # Generate documentation for each file
                            doc_result = code_analyzer.generate_documentation(
                                code=file_content,
                                filename=file_path,
                                options={
                                    'format': 'markdown',
                                    'style': 'comprehensive',
                                    'include_examples': True,
                                    'include_metadata': True
                                }
                            )
                            
                            if doc_result:
                                analysis_results[file_path] = doc_result
                        
                        except Exception as e:
                            st.warning(f"⚠️ Failed to analyze {file_path}: {str(e)}")
                    
                    progress_bar.progress(1.0)
                    status_text.text("Analysis complete!")
                    
                    if analysis_results:
                        st.success(f"✅ Successfully analyzed {len(analysis_results)} files!")
                        
                        # Display results
                        st.markdown("### 📈 Analysis Results")
                        
                        # Summary statistics
                        total_lines = sum(
                            result.get('metadata', {}).get('lines_of_code', 0) 
                            for result in analysis_results.values()
                        )
                        
                        total_functions = sum(
                            result.get('metadata', {}).get('function_count', 0) 
                            for result in analysis_results.values()
                        )
                        
                        total_classes = sum(
                            result.get('metadata', {}).get('class_count', 0) 
                            for result in analysis_results.values()
                        )
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Files Analyzed", len(analysis_results))
                        
                        with col2:
                            st.metric("Total Lines", total_lines)
                        
                        with col3:
                            st.metric("Functions", total_functions)
                        
                        with col4:
                            st.metric("Classes", total_classes)
                        
                        # File explorer
                        st.markdown("### 📁 Documentation Explorer")
                        
                        selected_file = st.selectbox(
                            "Select file to view documentation:",
                            list(analysis_results.keys()),
                            format_func=lambda x: x.split('/')[-1]  # Show only filename
                        )
                        
                        if selected_file:
                            result = analysis_results[selected_file]
                            
                            # File metadata
                            if result.get('metadata'):
                                with st.expander("📊 File Statistics"):
                                    metadata = result['metadata']
                                    col1, col2, col3 = st.columns(3)
                                    
                                    with col1:
                                        st.metric("Lines of Code", metadata.get('lines_of_code', 'N/A'))
                                    with col2:
                                        st.metric("Functions", metadata.get('function_count', 'N/A'))
                                    with col3:
                                        st.metric("Classes", metadata.get('class_count', 'N/A'))
                            
                            # Documentation content
                            st.markdown("#### 📝 Documentation")
                            documentation = result.get('documentation', 'No documentation generated')
                            st.markdown(documentation)
                        
                        # Repository structure analysis
                        if analyze_structure:
                            st.markdown("### 🏗️ Project Structure Analysis")
                            
                            # Generate project structure
                            structure_analysis = code_analyzer.analyze_project_structure(
                                files_data, 
                                repo_owner,
                                repo_name
                            )
                            
                            if structure_analysis:
                                st.markdown(structure_analysis)
                        
                        # Enhanced README generation
                        if include_readme:
                            st.markdown("### 📄 Enhanced README")
                            
                            with st.spinner("Generating enhanced README..."):
                                readme_content = code_analyzer.generate_enhanced_readme(
                                    repo_info=repo_info,
                                    analysis_results=analysis_results,
                                    files_data=files_data
                                )
                                
                                if readme_content:
                                    st.markdown(readme_content)
                                    
                                    st.download_button(
                                        label="📥 Download Enhanced README",
                                        data=readme_content,
                                        file_name="README_enhanced.md",
                                        mime="text/markdown"
                                    )
                        
                        # Download all documentation
                        st.markdown("### 📦 Export Documentation")
                        
                        # Create zip file with all documentation
                        zip_buffer = io.BytesIO()
                        
                        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                            # Add individual file documentation
                            for file_path, result in analysis_results.items():
                                # Clean file path for zip
                                clean_path = file_path.replace('/', '_').replace('\\', '_')
                                doc_filename = f"docs/{clean_path}_documentation.md"
                                
                                zip_file.writestr(
                                    doc_filename, 
                                    result.get('documentation', '')
                                )
                            
                            # Add summary report
                            summary_report = f"""# Repository Analysis Summary
Repository: {repo_owner}/{repo_name}
Analysis Date: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Statistics
- Files Analyzed: {len(analysis_results)}
- Total Lines of Code: {total_lines}
- Total Functions: {total_functions}
- Total Classes: {total_classes}

## Files Documented
"""
                            
                            for file_path in analysis_results.keys():
                                summary_report += f"- {file_path}\n"
                            
                            zip_file.writestr("ANALYSIS_SUMMARY.md", summary_report)
                            
                            # Add enhanced README if generated
                            if include_readme and 'readme_content' in locals():
                                zip_file.writestr("README_ENHANCED.md", readme_content)
                        
                        zip_buffer.seek(0)
                        
                        st.download_button(
                            label="📥 Download Complete Documentation (ZIP)",
                            data=zip_buffer.getvalue(),
                            file_name=f"{repo_owner}_{repo_name}_docs_{time.strftime('%Y%m%d_%H%M%S')}.zip",
                            mime="application/zip"
                        )
                    
                    else:
                        st.error("❌ No files could be analyzed successfully")
                
                except Exception as e:
                    st.error(f"❌ Analysis error: {str(e)}")
    
    # Tips section
    with st.expander("💡 GitHub Analysis Tips"):
        st.markdown("""
        **For best results:**
        - Ensure repository is public or you have proper access tokens configured
        - Start with smaller repositories to test functionality
        - Use file extension filters to focus on relevant code
        - Consider file limits for large repositories
        
        **Analysis types:**
        - **Full Repository**: Analyze all eligible files in the repository
        - **Specific Files**: Choose specific files or directories to analyze
        - **Recent Changes**: Focus on recently modified files
        
        **Access requirements:**
        - Public repositories: No authentication required
        - Private repositories: Requires GITHUB_TOKEN environment variable
        - Large repositories: May hit rate limits, consider using authentication
        """)

if __name__ == "__main__":
    main()
