import streamlit as st
from utils.groq_client import GroqClient
from utils.code_analyzer import CodeAnalyzer
from utils.constants import SUPPORTED_LANGUAGES
from components.sidebar import render_sidebar
import time
import zipfile
import io

st.set_page_config(page_title="Documentation Generator", page_icon="📚", layout="wide")

def main():
    render_sidebar()
    
    st.title("📚 Documentation Generator")
    st.markdown("Generate comprehensive technical documentation for your codebase")
    
    # Initialize clients
    try:
        groq_client = GroqClient()
        code_analyzer = CodeAnalyzer(groq_client)
    except Exception as e:
        st.error(f"Failed to initialize services: {str(e)}")
        st.stop()
    
    # Input method selection
    input_method = st.radio(
        "Documentation Source",
        ["Single File", "Multiple Files", "Code Snippet"],
        horizontal=True,
        help="Choose how you want to provide code for documentation"
    )
    
    files_content = {}
    
    if input_method == "Single File":
        uploaded_file = st.file_uploader(
            "Upload a code file",
            type=['py', 'js', 'java', 'cpp', 'c', 'rs', 'go', 'php', 'rb', 'ts', 'jsx', 'tsx','r'],
            help="Upload a single code file to document"
        )
        
        if uploaded_file is not None:
            try:
                content = uploaded_file.read().decode('utf-8')
                files_content[uploaded_file.name] = content
                st.success(f"✅ Loaded {uploaded_file.name}")
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
    
    elif input_method == "Multiple Files":
        uploaded_files = st.file_uploader(
            "Upload multiple code files",
            type=['py', 'js', 'java', 'cpp', 'c', 'rs', 'go', 'php', 'rb', 'ts', 'jsx', 'tsx','r'],
            accept_multiple_files=True,
            help="Upload multiple files to generate comprehensive documentation"
        )
        
        if uploaded_files:
            for uploaded_file in uploaded_files:
                try:
                    content = uploaded_file.read().decode('utf-8')
                    files_content[uploaded_file.name] = content
                except Exception as e:
                    st.error(f"Error reading {uploaded_file.name}: {str(e)}")
            
            if files_content:
                st.success(f"✅ Loaded {len(files_content)} files")
    
    else:  # Code Snippet
        language = st.selectbox(
            "Programming Language",
            SUPPORTED_LANGUAGES,
            help="Select the language of your code snippet"
        )
        
        code_snippet = st.text_area(
            "Enter your code snippet:",
            height=300,
            placeholder=f"Enter your {language} code here..."
        )
        
        if code_snippet.strip():
            files_content["code_snippet"] = code_snippet
    
    # Documentation options
    st.markdown("### 📝 Documentation Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        doc_format = st.selectbox(
            "Output Format",
            ["Markdown", "HTML", "Plain Text"],
            help="Choose the documentation format"
        )
        
        include_examples = st.checkbox(
            "Include Usage Examples", 
            value=True,
            help="Generate code usage examples"
        )
        
        include_diagrams = st.checkbox(
            "Include Flow Diagrams", 
            value=False,
            help="Generate ASCII flow diagrams where applicable"
        )
    
    with col2:
        doc_style = st.selectbox(
            "Documentation Style",
            ["Comprehensive", "Concise", "API Reference", "Tutorial"],
            help="Choose documentation style and depth"
        )
        
        include_toc = st.checkbox(
            "Include Table of Contents", 
            value=True,
            help="Generate a table of contents"
        )
        
        include_metadata = st.checkbox(
            "Include Metadata", 
            value=True,
            help="Include file information and statistics"
        )
    
    # Advanced options
    with st.expander("🔧 Advanced Options"):
        auto_detect_language = st.checkbox(
            "Auto-detect Language", 
            value=True,
            help="Automatically detect programming language from file content"
        )
        
        group_by_type = st.checkbox(
            "Group by Element Type", 
            value=True,
            help="Group documentation by functions, classes, modules, etc."
        )
        
        generate_index = st.checkbox(
            "Generate Index File", 
            value=len(files_content) > 1,
            help="Generate an index file linking all documentation"
        )
        
        custom_template = st.text_area(
            "Custom Template (optional)",
            placeholder="Enter custom documentation template...",
            help="Provide a custom template for documentation generation"
        )
    
    # Generate documentation
    if st.button("📚 Generate Documentation", type="primary", use_container_width=True):
        if not files_content:
            st.error("❌ Please provide code files or snippets to document")
            return
        
        documentation_options = {
            'format': doc_format.lower(),
            'style': doc_style.lower(),
            'include_examples': include_examples,
            'include_diagrams': include_diagrams,
            'include_toc': include_toc,
            'include_metadata': include_metadata,
            'auto_detect_language': auto_detect_language,
            'group_by_type': group_by_type,
            'custom_template': custom_template if custom_template.strip() else None
        }
        
        with st.spinner("Generating documentation... This may take a moment"):
            try:
                # Generate documentation for each file
                documentation_results = {}
                
                for filename, content in files_content.items():
                    result = code_analyzer.generate_documentation(
                        code=content,
                        filename=filename,
                        options=documentation_options
                    )
                    
                    if result:
                        documentation_results[filename] = result
                
                if documentation_results:
                    st.success("✅ Documentation generated successfully!")
                    
                    # Display results
                    if len(documentation_results) == 1:
                        # Single file documentation
                        filename, doc_result = next(iter(documentation_results.items()))
                        
                        st.markdown(f"### 📄 Documentation for {filename}")
                        
                        # Show metadata if available
                        if doc_result.get('metadata') and include_metadata:
                            with st.expander("📊 File Metadata"):
                                metadata = doc_result['metadata']
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    st.metric("Lines of Code", metadata.get('lines_of_code', 'N/A'))
                                
                                with col2:
                                    st.metric("Functions", metadata.get('function_count', 'N/A'))
                                
                                with col3:
                                    st.metric("Classes", metadata.get('class_count', 'N/A'))
                        
                        # Display documentation
                        documentation = doc_result.get('documentation', '')
                        
                        if doc_format == "Markdown":
                            st.markdown(documentation)
                        elif doc_format == "HTML":
                            st.components.v1.html(documentation, height=600, scrolling=True)
                        else:
                            st.text(documentation)
                        
                        # Download button
                        file_extension = {'Markdown': 'md', 'HTML': 'html', 'Plain Text': 'txt'}[doc_format]
                        
                        st.download_button(
                            label=f"📥 Download Documentation",
                            data=documentation,
                            file_name=f"{filename.split('.')[0]}_docs.{file_extension}",
                            mime="text/plain"
                        )
                    
                    else:
                        # Multiple files documentation
                        st.markdown("### 📁 Generated Documentation")
                        
                        # Create tabs for each file
                        file_tabs = st.tabs([f"📄 {filename}" for filename in documentation_results.keys()])
                        
                        for i, (filename, doc_result) in enumerate(documentation_results.items()):
                            with file_tabs[i]:
                                documentation = doc_result.get('documentation', '')
                                
                                # Show metadata
                                if doc_result.get('metadata') and include_metadata:
                                    with st.expander("📊 File Statistics"):
                                        metadata = doc_result['metadata']
                                        col1, col2, col3 = st.columns(3)
                                        
                                        with col1:
                                            st.metric("Lines", metadata.get('lines_of_code', 'N/A'))
                                        with col2:
                                            st.metric("Functions", metadata.get('function_count', 'N/A'))
                                        with col3:
                                            st.metric("Classes", metadata.get('class_count', 'N/A'))
                                
                                # Display documentation
                                if doc_format == "Markdown":
                                    st.markdown(documentation)
                                elif doc_format == "HTML":
                                    st.components.v1.html(documentation, height=400, scrolling=True)
                                else:
                                    st.text(documentation)
                        
                        # Generate and offer zip download
                        if len(documentation_results) > 1:
                            st.markdown("### 📦 Download All Documentation")
                            
                            # Create zip file
                            zip_buffer = io.BytesIO()
                            
                            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                                for filename, doc_result in documentation_results.items():
                                    file_extension = {'Markdown': 'md', 'HTML': 'html', 'Plain Text': 'txt'}[doc_format]
                                    doc_filename = f"{filename.split('.')[0]}_docs.{file_extension}"
                                    zip_file.writestr(doc_filename, doc_result.get('documentation', ''))
                                
                                # Add index file if requested
                                if generate_index:
                                    index_content = f"# Documentation Index\n\nGenerated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                                    index_content += "## Files Documented:\n\n"
                                    
                                    for filename in documentation_results.keys():
                                        doc_filename = f"{filename.split('.')[0]}_docs.{file_extension}"
                                        index_content += f"- [{filename}]({doc_filename})\n"
                                    
                                    zip_file.writestr(f"index.{file_extension}", index_content)
                            
                            zip_buffer.seek(0)
                            
                            st.download_button(
                                label="📥 Download All Documentation (ZIP)",
                                data=zip_buffer.getvalue(),
                                file_name=f"documentation_{time.strftime('%Y%m%d_%H%M%S')}.zip",
                                mime="application/zip"
                            )
                    
                else:
                    st.error("❌ Documentation generation failed. Please try again.")
                    
            except Exception as e:
                st.error(f"❌ Documentation error: {str(e)}")
    
    # Preview section
    if files_content:
        st.markdown("### 👀 Code Preview")
        
        if len(files_content) == 1:
            filename, content = next(iter(files_content.items()))
            
            with st.expander(f"📄 {filename}"):
                # Detect language for syntax highlighting
                language_map = {
                    '.py': 'python',
                    '.js': 'javascript', 
                    '.ts': 'typescript',
                    '.java': 'java',
                    '.cpp': 'cpp',
                    '.c': 'c',
                    '.rs': 'rust',
                    '.go': 'go',
                    '.php': 'php',
                    '.rb': 'ruby',
                    '.r': 'r'
                }
                
                file_ext = '.' + filename.split('.')[-1] if '.' in filename else ''
                highlight_lang = language_map.get(file_ext, 'text')
                
                st.code(content[:2000] + ("..." if len(content) > 2000 else ""), language=highlight_lang)
        else:
            selected_file = st.selectbox("Select file to preview:", list(files_content.keys()))
            
            if selected_file:
                content = files_content[selected_file]
                
                # Detect language for syntax highlighting
                language_map = {
                    '.py': 'python',
                    '.js': 'javascript',
                    '.ts': 'typescript', 
                    '.java': 'java',
                    '.cpp': 'cpp',
                    '.c': 'c',
                    '.rs': 'rust',
                    '.go': 'go',
                    '.php': 'php',
                    '.rb': 'ruby',
                    '.r': 'r'
                }
                
                file_ext = '.' + selected_file.split('.')[-1] if '.' in selected_file else ''
                highlight_lang = language_map.get(file_ext, 'text')
                
                st.code(content[:2000] + ("..." if len(content) > 2000 else ""), language=highlight_lang)
    
    # Tips section
    with st.expander("💡 Documentation Tips"):
        st.markdown("""
        **For best documentation:**
        - Use descriptive function and variable names
        - Include existing comments and docstrings
        - Provide complete, working code examples
        - Structure code with clear organization
        
        **Documentation styles:**
        - **Comprehensive**: Detailed explanations with examples and context
        - **Concise**: Brief, focused documentation for quick reference
        - **API Reference**: Technical reference with parameters and return values
        - **Tutorial**: Step-by-step guides with learning context
        
        **Multiple files:**
        - Upload related files together for better cross-references
        - Use consistent naming conventions
        - Consider generating an index for navigation
        """)

if __name__ == "__main__":
    main()
