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
            type=['py', 'js', 'java', 'cpp', 'c', 'rs', 'go', 'php', 'rb', 'ts', 'jsx', 'tsx'],
            help="Upload a code file to translate"
        )
    elif input_method == "🐙 GitHub URL":
        st.markdown("#### Fetch Code from GitHub Repository")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            github_url = st.text_input(
                "GitHub file URL",
                placeholder="https://github.com/owner/repo/blob/main/file.py",
                help="Paste the direct URL to a code file on GitHub"
            )
        
        with col2:
            fetch_button = st.button("🔄 Fetch", use_container_width=True)
        
        # GitHub URL examples
        with st.expander("📋 GitHub URL Examples"):
            st.markdown("""
            **Supported formats:**
            - `https://github.com/owner/repo/blob/main/file.py`
            - `https://github.com/owner/repo/blob/branch/path/to/file.js`
            - `https://raw.githubusercontent.com/owner/repo/main/file.py`
            
            **Popular examples:**
            - Python: `https://github.com/python/cpython/blob/main/Lib/os.py`
            - JavaScript: `https://github.com/facebook/react/blob/main/packages/react/index.js`
            - Java: `https://github.com/spring-projects/spring-boot/blob/main/spring-boot-project/spring-boot/src/main/java/org/springframework/boot/SpringApplication.java`
            """)
    else:
        uploaded_file = None
        github_url = None
        fetch_button = False
    
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
                'rs': 'Rust', 'go': 'Go', 'php': 'PHP', 'rb': 'Ruby', 'ts': 'TypeScript'
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
        try:
            with st.spinner("🔄 Fetching code from GitHub..."):
                # Convert GitHub URL to raw format
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
                            'rs': 'Rust', 'go': 'Go', 'php': 'PHP', 'rb': 'Ruby', 'ts': 'TypeScript'
                        }
                        
                        detected_lang = ext_to_lang.get(file_ext, 'Unknown')
                        
                        st.success(f"✅ Fetched {filename} from GitHub")
                        if detected_lang != 'Unknown':
                            st.info(f"🔍 Detected language: {detected_lang}")
                        
                        # Show file info
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

if __name__ == "__main__":
    main()
