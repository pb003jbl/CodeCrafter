import streamlit as st
from typing import Optional, Dict, Any

def render_code_editor(
    content: str = "",
    language: str = "python",
    height: int = 400,
    key: Optional[str] = None,
    theme: str = "github",
    read_only: bool = False,
    wrap: bool = False,
    auto_update: bool = True
) -> str:
    """
    Render a code editor component using Streamlit's text_area with syntax highlighting
    
    Args:
        content: Initial content for the editor
        language: Programming language for syntax highlighting
        height: Height of the editor in pixels
        key: Unique key for the component
        theme: Editor theme (not used with text_area)
        read_only: Whether the editor is read-only
        wrap: Whether to wrap long lines
        auto_update: Whether to auto-update content
    
    Returns:
        Current content of the editor
    """
    
    # Map language names to highlighting languages
    language_map = {
        "Python": "python",
        "JavaScript": "javascript", 
        "TypeScript": "typescript",
        "Java": "java",
        "C++": "cpp",
        "C": "c",
        "Rust": "rust",
        "Go": "go",
        "PHP": "php",
        "Ruby": "ruby",
        "React": "jsx",
        "Angular": "typescript"
    }
    
    highlight_lang = language_map.get(language, language.lower())
    
    if read_only:
        # Display as code block if read-only
        st.code(content, language=highlight_lang)
        return content
    else:
        # Use text_area for editable content
        return st.text_area(
            label="",
            value=content,
            height=height,
            key=key,
            placeholder=f"Enter your {language} code here...",
            label_visibility="collapsed"
        )

def render_code_comparison(
    original_code: str,
    modified_code: str,
    original_language: str = "python",
    modified_language: str = "python",
    labels: tuple = ("Original", "Modified")
) -> None:
    """
    Render a side-by-side code comparison
    
    Args:
        original_code: Original code content
        modified_code: Modified code content
        original_language: Language of original code
        modified_language: Language of modified code
        labels: Labels for the code sections
    """
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### {labels[0]}")
        render_code_editor(
            content=original_code,
            language=original_language,
            read_only=True,
            height=400
        )
    
    with col2:
        st.markdown(f"### {labels[1]}")
        render_code_editor(
            content=modified_code,
            language=modified_language,
            read_only=True,
            height=400
        )

def render_code_preview(
    content: str,
    language: str = "python",
    max_lines: int = 50,
    show_line_numbers: bool = True
) -> None:
    """
    Render a code preview with optional line limits
    
    Args:
        content: Code content to preview
        language: Programming language
        max_lines: Maximum lines to display
        show_line_numbers: Whether to show line numbers
    """
    
    lines = content.splitlines()
    
    if len(lines) > max_lines:
        preview_content = '\n'.join(lines[:max_lines])
        preview_content += f"\n\n... ({len(lines) - max_lines} more lines)"
        st.info(f"Showing first {max_lines} lines of {len(lines)} total lines")
    else:
        preview_content = content
    
    # Map language names
    language_map = {
        "Python": "python",
        "JavaScript": "javascript",
        "TypeScript": "typescript", 
        "Java": "java",
        "C++": "cpp",
        "C": "c",
        "Rust": "rust",
        "Go": "go",
        "PHP": "php",
        "Ruby": "ruby",
        "React": "jsx",
        "Angular": "typescript"
    }
    
    highlight_lang = language_map.get(language, language.lower())
    
    st.code(preview_content, language=highlight_lang)

def render_file_explorer(
    files: Dict[str, str],
    selected_file: Optional[str] = None,
    show_preview: bool = True,
    preview_lines: int = 30
) -> Optional[str]:
    """
    Render a file explorer with preview capability
    
    Args:
        files: Dictionary mapping file paths to content
        selected_file: Currently selected file
        show_preview: Whether to show file preview
        preview_lines: Number of lines to show in preview
    
    Returns:
        Selected file path
    """
    
    if not files:
        st.info("No files to display")
        return None
    
    # File selection
    file_options = list(files.keys())
    
    # Default to first file if no selection
    if selected_file not in file_options:
        selected_file = file_options[0]
    
    selected = st.selectbox(
        "Select a file:",
        file_options,
        index=file_options.index(selected_file) if selected_file in file_options else 0,
        format_func=lambda x: x.split('/')[-1]  # Show only filename in dropdown
    )
    
    if show_preview and selected:
        st.markdown(f"**File:** `{selected}`")
        
        # Detect language from file extension
        file_ext = '.' + selected.split('.')[-1] if '.' in selected else ''
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java', 
            '.cpp': 'C++',
            '.c': 'C',
            '.rs': 'Rust',
            '.go': 'Go',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.jsx': 'React',
            '.tsx': 'TypeScript'
        }
        
        language = language_map.get(file_ext, 'text')
        
        # Show file stats
        content = files[selected]
        lines_count = len(content.splitlines())
        char_count = len(content)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Lines", lines_count)
        with col2:
            st.metric("Characters", char_count)
        with col3:
            st.metric("Language", language)
        
        # Show preview
        render_code_preview(
            content=content,
            language=language,
            max_lines=preview_lines
        )
    
    return selected

def render_diff_viewer(
    original: str,
    modified: str,
    language: str = "python"
) -> None:
    """
    Render a simple diff viewer showing changes between two code versions
    
    Args:
        original: Original code
        modified: Modified code  
        language: Programming language
    """
    
    st.markdown("### Code Changes")
    
    # Simple line-by-line comparison
    original_lines = original.splitlines()
    modified_lines = modified.splitlines()
    
    max_lines = max(len(original_lines), len(modified_lines))
    
    # Show statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Original Lines", len(original_lines))
    with col2:
        st.metric("Modified Lines", len(modified_lines)) 
    with col3:
        lines_diff = len(modified_lines) - len(original_lines)
        st.metric("Lines Changed", f"+{lines_diff}" if lines_diff > 0 else str(lines_diff))
    
    # Side-by-side comparison
    render_code_comparison(
        original_code=original,
        modified_code=modified,
        original_language=language,
        modified_language=language,
        labels=("Before", "After")
    )

def render_syntax_highlighter(
    code: str,
    language: str,
    theme: str = "github",
    show_line_numbers: bool = True
) -> None:
    """
    Render code with syntax highlighting
    
    Args:
        code: Code to highlight
        language: Programming language
        theme: Color theme (not used with st.code)
        show_line_numbers: Whether to show line numbers
    """
    
    # Map language names for highlighting
    language_map = {
        "Python": "python",
        "JavaScript": "javascript",
        "TypeScript": "typescript",
        "Java": "java", 
        "C++": "cpp",
        "C": "c",
        "Rust": "rust",
        "Go": "go",
        "PHP": "php",
        "Ruby": "ruby",
        "React": "jsx",
        "Angular": "typescript"
    }
    
    highlight_lang = language_map.get(language, language.lower())
    
    # Add line numbers if requested (simple implementation)
    if show_line_numbers and code.strip():
        lines = code.splitlines()
        numbered_code = ""
        for i, line in enumerate(lines, 1):
            numbered_code += f"{i:3d} | {line}\n"
        
        st.code(numbered_code, language=highlight_lang)
    else:
        st.code(code, language=highlight_lang)

def create_download_link(
    content: str,
    filename: str,
    mime_type: str = "text/plain",
    label: str = "Download"
) -> None:
    """
    Create a download button for code content
    
    Args:
        content: Content to download
        filename: Name of the file
        mime_type: MIME type of the content
        label: Label for the download button
    """
    
    st.download_button(
        label=label,
        data=content,
        file_name=filename,
        mime=mime_type
    )

def render_code_metrics(
    code: str,
    language: str = "python"
) -> Dict[str, Any]:
    """
    Render basic code metrics
    
    Args:
        code: Code to analyze
        language: Programming language
    
    Returns:
        Dictionary of calculated metrics
    """
    
    lines = code.splitlines()
    
    # Basic metrics
    metrics = {
        'total_lines': len(lines),
        'blank_lines': len([line for line in lines if not line.strip()]),
        'comment_lines': 0,
        'code_lines': 0,
        'character_count': len(code),
        'word_count': len(code.split())
    }
    
    # Language-specific comment detection
    comment_patterns = {
        'Python': ['#'],
        'JavaScript': ['//', '/*'],
        'TypeScript': ['//', '/*'],
        'Java': ['//', '/*'],
        'C++': ['//', '/*'],
        'C': ['//', '/*'],
        'Rust': ['//'],
        'Go': ['//'],
        'PHP': ['//', '#'],
        'Ruby': ['#']
    }
    
    patterns = comment_patterns.get(language, ['#', '//'])
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        elif any(stripped.startswith(pattern) for pattern in patterns):
            metrics['comment_lines'] += 1
        else:
            metrics['code_lines'] += 1
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Lines", metrics['total_lines'])
    
    with col2:
        st.metric("Code Lines", metrics['code_lines'])
    
    with col3:
        st.metric("Comments", metrics['comment_lines'])
    
    with col4:
        comment_ratio = (metrics['comment_lines'] / max(metrics['total_lines'], 1)) * 100
        st.metric("Comment %", f"{comment_ratio:.1f}%")
    
    return metrics
