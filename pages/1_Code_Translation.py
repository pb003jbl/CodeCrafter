import streamlit as st
from utils.groq_client import GroqClient
from utils.code_analyzer import CodeAnalyzer
from utils.constants import SUPPORTED_LANGUAGES
from components.code_editor import render_code_editor
from components.sidebar import render_sidebar

st.set_page_config(page_title="Code Translation", page_icon="🔄", layout="wide")

def main():
    render_sidebar()
    
    st.title("🔄 Code Translation")
    st.markdown("Translate code between programming languages with intelligent syntax mapping")
    
    # Initialize clients
    try:
        groq_client = GroqClient()
        code_analyzer = CodeAnalyzer(groq_client)
    except Exception as e:
        st.error(f"Failed to initialize services: {str(e)}")
        st.stop()
    
    # Language selection
    col1, col2 = st.columns(2)
    
    with col1:
        source_lang = st.selectbox(
            "Source Language",
            SUPPORTED_LANGUAGES,
            index=0
        )
    
    with col2:
        target_lang = st.selectbox(
            "Target Language", 
            SUPPORTED_LANGUAGES,
            index=1
        )
    
    if source_lang == target_lang:
        st.warning("⚠️ Source and target languages are the same")
        return
    
    # Code input section
    st.markdown("### Input Code")
    
    # Input method selection
    input_method = st.radio(
        "Choose input method:",
        ["✍️ Manual Entry", "📁 Upload File", "🐙 GitHub URL"],
        horizontal=True
    )
    
    if input_method == "📁 Upload File":
        uploaded_file = st.file_uploader(
            "Upload a code file",
            type=['py', 'js', 'java', 'cpp', 'c', 'rs', 'go', 'php', 'rb', 'ts', 'jsx', 'tsx','r'],
            help="Upload a code file to translate"
        )
    elif input_method == "🐙 GitHub URL":
        st.markdown("#### Fetch Code from GitHub Repository")
        
        # Repository or single file selection
        repo_mode = st.radio(
            "What would you like to fetch?",
            ["📄 Single File", "📦 Entire Repository"],
            horizontal=True
        )
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if repo_mode == "📄 Single File":
                github_url = st.text_input(
                    "GitHub file URL",
                    placeholder="https://github.com/owner/repo/blob/main/file.py",
                    help="Paste the direct URL to a code file on GitHub"
                )
            else:
                github_url = st.text_input(
                    "GitHub repository URL",
                    placeholder="https://github.com/owner/repo",
                    help="Paste the URL to a GitHub repository"
                )
        
        with col2:
            if repo_mode == "📄 Single File":
                fetch_button = st.button("🔄 Fetch File", use_container_width=True)
            else:
                fetch_button = st.button("📦 Fetch Repo", use_container_width=True)
        
        # Repository options
        if repo_mode == "📦 Entire Repository":
            with st.expander("⚙️ Repository Options", expanded=True):
                col_a, col_b = st.columns(2)
                with col_a:
                    max_files = st.number_input("Max files to process", min_value=1, max_value=100, value=20)
                    file_size_limit = st.number_input("Max file size (KB)", min_value=1, max_value=1000, value=100)
                with col_b:
                    exclude_dirs = st.multiselect(
                        "Exclude directories",
                        ["node_modules", ".git", "__pycache__", "build", "dist", "target", "bin"],
                        default=["node_modules", ".git", "__pycache__"]
                    )
                    include_extensions = st.multiselect(
                        "Include file types",
                        [".py", ".js", ".java", ".cpp", ".c", ".rs", ".go", ".php", ".rb", ".ts",'.r'],
                        default=[".py", ".js", ".java"]
                    )
        
        # GitHub URL examples
        with st.expander("📋 GitHub URL Examples"):
            if repo_mode == "📄 Single File":
                st.markdown("""
                **Single file formats:**
                - `https://github.com/owner/repo/blob/main/file.py`
                - `https://github.com/owner/repo/blob/branch/path/to/file.js`
                - `https://raw.githubusercontent.com/owner/repo/main/file.py`
                
                **Popular examples:**
                - Python: `https://github.com/python/cpython/blob/main/Lib/os.py`
                - JavaScript: `https://github.com/facebook/react/blob/main/packages/react/index.js`
                """)
            else:
                st.markdown("""
                **Repository formats:**
                - `https://github.com/owner/repo`
                - `https://github.com/owner/repo/tree/branch`
                
                **Popular examples:**
                - Small Python project: `https://github.com/pallets/flask`
                - JavaScript library: `https://github.com/lodash/lodash`
                - Java project: `https://github.com/spring-projects/spring-petclinic`
                """)
    else:
        uploaded_file = None
        github_url = None
        fetch_button = False
        repo_mode = "📄 Single File"
    
    input_code = ""
    
    # Handle different input methods
    if input_method == "📁 Upload File" and uploaded_file is not None:
        try:
            input_code = uploaded_file.read().decode('utf-8')
            filename = uploaded_file.name
            file_ext = filename.split('.')[-1].lower()
            
            # Auto-detect source language
            ext_to_lang = {
                'py': 'Python', 'js': 'JavaScript', 'java': 'Java', 'cpp': 'C++', 'c': 'C',
                'rs': 'Rust', 'go': 'Go', 'php': 'PHP', 'rb': 'Ruby', 'ts': 'TypeScript','r': 'R'

            }
            
            if file_ext in ext_to_lang:
                detected_lang = ext_to_lang[file_ext]
                st.success(f"✅ Loaded {filename} - Detected: {detected_lang}")
                if detected_lang != source_lang:
                    st.info(f"💡 Consider changing source language to {detected_lang}")
            else:
                st.success(f"✅ Loaded {filename}")
                
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
    
    elif input_method == "🐙 GitHub URL" and github_url and fetch_button:
        if repo_mode == "📄 Single File":
            # Single file fetching (existing logic)
            try:
                with st.spinner("🔄 Fetching code from GitHub..."):
                    raw_url = convert_github_url_to_raw(github_url)
                    
                    if raw_url:
                        import requests
                        response = requests.get(raw_url, timeout=10)
                        
                        if response.status_code == 200:
                            input_code = response.text
                            filename = github_url.split('/')[-1]
                            file_ext = filename.split('.')[-1].lower() if '.' in filename else ''
                            
                            # Auto-detect language
                            ext_to_lang = {
                                'py': 'Python', 'js': 'JavaScript', 'java': 'Java', 'cpp': 'C++', 'c': 'C',
                                'rs': 'Rust', 'go': 'Go', 'php': 'PHP', 'rb': 'Ruby', 'ts': 'TypeScript', 'r': 'R'

                            }
                            
                            detected_lang = ext_to_lang.get(file_ext, 'Unknown')
                            
                            st.success(f"✅ Fetched {filename} from GitHub")
                            if detected_lang != 'Unknown':
                                st.info(f"🔍 Detected language: {detected_lang}")
                            
                            lines = len(input_code.split('\n'))
                            st.metric("File size", f"{lines} lines")
                            
                        elif response.status_code == 404:
                            st.error("❌ File not found. Please check the URL.")
                            input_code = ""
                        else:
                            st.error(f"❌ Failed to fetch file (HTTP {response.status_code})")
                            input_code = ""
                    else:
                        st.error("❌ Invalid GitHub URL format")
                        input_code = ""
                        
            except Exception as e:
                st.error(f"❌ Error fetching file: {str(e)}")
                input_code = ""
        
        else:
            # Repository fetching - new functionality
            try:
                with st.spinner("📦 Fetching repository from GitHub..."):
                    repo_files = fetch_github_repository(
                        github_url, 
                        max_files=max_files,
                        file_size_limit=file_size_limit * 1024,  # Convert to bytes
                        exclude_dirs=exclude_dirs,
                        include_extensions=include_extensions
                    )
                    
                    if repo_files:
                        st.success(f"✅ Fetched {len(repo_files)} files from repository")
                        
                        # Show repository summary
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("Files Found", len(repo_files))
                        with col_b:
                            total_lines = sum(len(content.split('\n')) for content in repo_files.values())
                            st.metric("Total Lines", total_lines)
                        with col_c:
                            languages = set()
                            for filepath in repo_files.keys():
                                ext = filepath.split('.')[-1].lower()
                                ext_to_lang = {
                                    'py': 'Python', 'js': 'JavaScript', 'java': 'Java', 'cpp': 'C++', 'c': 'C',
                                    'rs': 'Rust', 'go': 'Go', 'php': 'PHP', 'rb': 'Ruby', 'ts': 'TypeScript', 'r': 'R'

                                }
                                if ext in ext_to_lang:
                                    languages.add(ext_to_lang[ext])
                            st.metric("Languages", len(languages))
                        
                        # Store repository files in session state
                        st.session_state.repo_files = repo_files
                        st.session_state.repo_url = github_url
                        
                        # Show file list
                        with st.expander("📋 Repository Files", expanded=True):
                            for filepath, content in list(repo_files.items())[:10]:  # Show first 10
                                lines = len(content.split('\n'))
                                st.markdown(f"📄 `{filepath}` ({lines} lines)")
                            
                            if len(repo_files) > 10:
                                st.info(f"... and {len(repo_files) - 10} more files")
                        
                        # Skip individual code input for repository mode
                        input_code = ""
                        
                    else:
                        st.error("❌ No compatible files found in repository")
                        input_code = ""
                        
            except Exception as e:
                st.error(f"❌ Error fetching repository: {str(e)}")
                input_code = ""
    
    # Code editor for manual input or editing fetched code
    if input_method == "✍️ Manual Entry" or not input_code:
        code_input = st.text_area(
            "Enter your code here:" if input_method == "✍️ Manual Entry" else "Edit code:",
            value=input_code,
            height=300,
            placeholder=f"Enter your {source_lang} code here..."
        )
    else:
        # Show preview of fetched code with option to edit
        st.markdown("#### 📋 Code Preview")
        code_input = st.text_area(
            "Code content (you can edit before translation):",
            value=input_code,
            height=300,
            help="Edit the fetched code before translation if needed"
        )
    
    # Translation options
    with st.expander("🔧 Translation Options"):
        preserve_comments = st.checkbox("Preserve comments", value=True)
        add_type_hints = st.checkbox("Add type hints (when applicable)", value=True)
        optimize_code = st.checkbox("Apply basic optimizations", value=False)
        include_examples = st.checkbox("Include usage examples", value=False)
    
    # Translation button
    # Check if we have repository files or single file
    has_repo_files = hasattr(st.session_state, 'repo_files') and st.session_state.repo_files
    
    if has_repo_files:
        st.markdown("### 📦 Repository Translation")
        st.info(f"Ready to translate {len(st.session_state.repo_files)} files from repository")
        
        if st.button("🔄 Translate Entire Repository", type="primary", use_container_width=True):
            translate_repository(st.session_state.repo_files, source_lang, target_lang, {
                'preserve_comments': preserve_comments,
                'add_type_hints': add_type_hints,
                'optimize_code': optimize_code,
                'include_examples': include_examples
            })
    
    elif code_input.strip():
        if st.button("🔄 Translate Code", type="primary", use_container_width=True):
            if not code_input.strip():
                st.error("❌ Please provide code to translate")
                return
        
        with st.spinner(f"Translating from {source_lang} to {target_lang}..."):
            try:
                # Perform translation
                translation_result = code_analyzer.translate_code(
                    code=code_input,
                    source_language=source_lang,
                    target_language=target_lang,
                    preserve_comments=preserve_comments,
                    add_type_hints=add_type_hints,
                    optimize_code=optimize_code,
                    include_examples=include_examples
                )
                
                if translation_result:
                    st.success("✅ Translation completed successfully!")
                    
                    # Display results
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"### Original ({source_lang})")
                        st.code(code_input, language=source_lang.lower())
                    
                    with col2:
                        st.markdown(f"### Translated ({target_lang})")
                        st.code(translation_result['translated_code'], language=target_lang.lower())
                    
                    # Translation notes
                    if translation_result.get('notes'):
                        st.markdown("### 📝 Translation Notes")
                        st.info(translation_result['notes'])
                    
                    # Download button
                    file_extension = {
                        'Python': 'py',
                        'JavaScript': 'js',
                        'TypeScript': 'ts',
                        'Java': 'java',
                        'C++': 'cpp',
                        'C': 'c',
                        'Rust': 'rs',
                        'Go': 'go',
                        'PHP': 'php',
                        'Ruby': 'rb',
                        'React': 'jsx',
                        'Angular': 'ts'
                    }.get(target_lang, 'txt')
                    
                    st.download_button(
                        label=f"📥 Download {target_lang} Code",
                        data=translation_result['translated_code'],
                        file_name=f"translated_code.{file_extension}",
                        mime="text/plain"
                    )
                else:
                    st.error("❌ Translation failed. Please try again.")
                    
            except Exception as e:
                st.error(f"❌ Translation error: {str(e)}")
    
    # Usage tips
    with st.expander("💡 Translation Tips"):
        st.markdown("""
        **For best results:**
        - Provide clean, well-structured code
        - Include meaningful variable and function names
        - Add comments to explain complex logic
        - Ensure code is syntactically correct in the source language
        
        **Supported features:**
        - Syntax conversion and language-specific patterns
        - Library and framework mappings
        - Code style adaptation
        - Error handling patterns
        - Documentation preservation
        """)

def convert_github_url_to_raw(github_url: str) -> str:
    """Convert GitHub URL to raw content URL"""
    try:
        # Handle different GitHub URL formats
        if 'raw.githubusercontent.com' in github_url:
            return github_url
        elif 'github.com' in github_url and '/blob/' in github_url:
            # Convert from blob URL to raw URL
            raw_url = github_url.replace('github.com', 'raw.githubusercontent.com')
            raw_url = raw_url.replace('/blob/', '/')
            return raw_url
        else:
            return ""
    except Exception:
        return ""

def fetch_github_repository(repo_url: str, max_files: int = 20, file_size_limit: int = 102400, 
                           exclude_dirs: list = None, include_extensions: list = None) -> dict:
    """Fetch all code files from a GitHub repository"""
    import requests
    import base64
    
    if exclude_dirs is None:
        exclude_dirs = ["node_modules", ".git", "__pycache__"]
    if include_extensions is None:
        include_extensions = [".py", ".js", ".java", ".cpp", ".c", ".rs", ".go", ".php", ".rb", ".ts",".r"]
    
    try:
        # Parse repository URL
        if repo_url.endswith('/'):
            repo_url = repo_url[:-1]
        
        # Extract owner and repo name
        parts = repo_url.replace('https://github.com/', '').split('/')
        if len(parts) < 2:
            return {}
        
        owner, repo = parts[0], parts[1]
        
        # Get repository tree using GitHub API
        api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1"
        response = requests.get(api_url, timeout=15)
        
        if response.status_code != 200:
            # Try with 'master' branch
            api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/master?recursive=1"
            response = requests.get(api_url, timeout=15)
        
        if response.status_code != 200:
            return {}
        
        tree_data = response.json()
        repo_files = {}
        file_count = 0
        
        for item in tree_data.get('tree', []):
            if file_count >= max_files:
                break
                
            if item['type'] != 'blob':  # Skip directories
                continue
                
            filepath = item['path']
            
            # Check if file should be excluded
            if any(exclude_dir in filepath for exclude_dir in exclude_dirs):
                continue
            
            # Check file extension
            if not any(filepath.endswith(ext) for ext in include_extensions):
                continue
            
            # Check file size
            if item.get('size', 0) > file_size_limit:
                continue
            
            try:
                # Fetch file content
                file_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{filepath}"
                file_response = requests.get(file_url, timeout=10)
                
                if file_response.status_code == 200:
                    file_data = file_response.json()
                    
                    # Decode base64 content
                    if file_data.get('encoding') == 'base64':
                        content = base64.b64decode(file_data['content']).decode('utf-8')
                        repo_files[filepath] = content
                        file_count += 1
                        
            except Exception as e:
                # Skip files that can't be processed
                continue
        
        return repo_files
        
    except Exception as e:
        return {}

def translate_repository(repo_files: dict, source_lang: str, target_lang: str, options: dict):
    """Translate all files in a repository and provide download"""
    import zipfile
    import io
    from datetime import datetime
    
    if not repo_files:
        st.error("No files to translate")
        return
    
    # Initialize progress tracking
    total_files = len(repo_files)
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    translated_files = {}
    successful_translations = 0
    
    # Get groq client
    try:
        from utils.groq_client import GroqClient
        from utils.code_analyzer import CodeAnalyzer
        
        groq_client = GroqClient()
        analyzer = CodeAnalyzer(groq_client)
        
        for i, (filepath, content) in enumerate(repo_files.items()):
            progress = (i + 1) / total_files
            progress_bar.progress(progress)
            status_text.text(f"Translating {filepath} ({i+1}/{total_files})")
            
            try:
                # Translate the file
                result = analyzer.translate_code(
                    content, source_lang, target_lang,
                    preserve_comments=options.get('preserve_comments', True),
                    add_type_hints=options.get('add_type_hints', False),
                    optimize_code=options.get('optimize_code', False),
                    include_examples=options.get('include_examples', False)
                )
                
                if result and 'translated_code' in result:
                    # Determine new file extension
                    new_ext = get_file_extension(target_lang)
                    
                    # Create new filepath with target language extension
                    base_path = filepath.rsplit('.', 1)[0] if '.' in filepath else filepath
                    new_filepath = f"{base_path}{new_ext}"
                    
                    translated_files[new_filepath] = result['translated_code']
                    successful_translations += 1
                else:
                    # Keep original file if translation fails
                    translated_files[filepath] = content
                    
            except Exception as e:
                # Keep original file if translation fails
                translated_files[filepath] = content
        
        progress_bar.progress(1.0)
        status_text.text(f"✅ Translation complete! {successful_translations}/{total_files} files translated")
        
        # Create downloadable zip file
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for filepath, content in translated_files.items():
                zip_file.writestr(filepath, content)
        
        zip_buffer.seek(0)
        
        # Provide download button
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"translated_repository_{source_lang}_to_{target_lang}_{timestamp}.zip"
        
        st.success(f"🎉 Repository translation complete!")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Files Processed", total_files)
        with col2:
            st.metric("Successfully Translated", successful_translations)
        with col3:
            st.metric("Success Rate", f"{(successful_translations/total_files)*100:.1f}%")
        
        st.download_button(
            label="📦 Download Translated Repository",
            data=zip_buffer.getvalue(),
            file_name=filename,
            mime="application/zip",
            use_container_width=True
        )
        
        # Show translation summary
        with st.expander("📋 Translation Summary", expanded=True):
            for filepath in list(translated_files.keys())[:10]:
                st.markdown(f"✅ {filepath}")
            if len(translated_files) > 10:
                st.info(f"... and {len(translated_files) - 10} more files")
        
    except Exception as e:
        st.error(f"❌ Translation failed: {str(e)}")

def get_file_extension(language: str) -> str:
    """Get file extension for target language"""
    extensions = {
        'Python': '.py',
        'JavaScript': '.js', 
        'Java': '.java',
        'C++': '.cpp',
        'C': '.c',
        'Rust': '.rs',
        'Go': '.go',
        'PHP': '.php',
        'Ruby': '.rb',
        'TypeScript': '.ts',
        'C#': '.cs',
        'Swift': '.swift',
        'Kotlin': '.kt',
        'R': '.r'
    }
    return extensions.get(language, '.txt')

if __name__ == "__main__":
    main()
