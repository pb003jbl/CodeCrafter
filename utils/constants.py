"""
Constants and configuration for the Developer Productivity Suite
"""

# Application metadata
APP_TITLE = "Developer Productivity Suite"
APP_DESCRIPTION = "A comprehensive toolkit for code analysis, translation, and documentation"
APP_VERSION = "1.0.0"

# Supported programming languages
SUPPORTED_LANGUAGES = [
    "Python",
    "JavaScript", 
    "TypeScript",
    "Java",
    "C++",
    "C",
    "Rust",
    "Go",
    "PHP",
    "Ruby",
    "React",
    "Angular",
    "R"
]

# File extensions mapping
FILE_EXTENSIONS = {
    "Python": [".py"],
    "JavaScript": [".js"],
    "TypeScript": [".ts"],
    "Java": [".java"],
    "C++": [".cpp", ".cc", ".cxx"],
    "C": [".c", ".h"],
    "Rust": [".rs"],
    "Go": [".go"],
    "PHP": [".php"],
    "Ruby": [".rb"],
    "React": [".jsx"],
    "Angular": [".ts", ".component.ts"],
    "R": [".r", ".R"]
}

# Color scheme (matching the design requirements)
COLORS = {
    "primary": "#2F80ED",      # Azure blue
    "secondary": "#333333",    # Charcoal
    "background": "#F6F8FA",   # Light grey
    "text": "#24292E",         # GitHub dark
    "success": "#28A745",      # Success green
    "warning": "#FCA130",      # Warning orange
    "danger": "#DC3545",       # Danger red
    "info": "#17A2B8"         # Info blue
}

# Code analysis severity levels
SEVERITY_LEVELS = [
    "Critical",
    "High", 
    "Medium",
    "Low"
]

# Documentation styles
DOCUMENTATION_STYLES = [
    "Comprehensive",
    "Concise",
    "API Reference",
    "Tutorial"
]

# Code review categories
REVIEW_CATEGORIES = [
    "Security",
    "Performance", 
    "Code Quality",
    "Best Practices",
    "Maintainability",
    "Documentation"
]

# GitHub API configuration
GITHUB_API_BASE = "https://api.github.com"
GITHUB_RAW_BASE = "https://raw.githubusercontent.com"

# Maximum file sizes and limits
MAX_FILE_SIZE_MB = 1  # 1MB limit for individual files
MAX_FILES_ANALYSIS = 100  # Maximum files to analyze in one session
MAX_LINES_PREVIEW = 100  # Maximum lines to show in preview

# Default ignore patterns for GitHub analysis
DEFAULT_IGNORE_PATTERNS = [
    "node_modules/",
    ".git/",
    "__pycache__/",
    "*.pyc",
    ".env",
    "venv/",
    "env/",
    "build/",
    "dist/",
    ".pytest_cache/",
    "coverage/",
    ".coverage",
    "*.log",
    ".DS_Store",
    "Thumbs.db"
]

# Groq API configuration
GROQ_API_BASE = "https://api.groq.com/openai/v1"
GROQ_DEFAULT_MODEL = "llama3-8b-8192"
GROQ_MAX_TOKENS = 4000
GROQ_DEFAULT_TEMPERATURE = 0.1

# Analysis timeouts (in seconds)
ANALYSIS_TIMEOUT = 120  # 2 minutes for code analysis
TRANSLATION_TIMEOUT = 90  # 1.5 minutes for code translation
DOCUMENTATION_TIMEOUT = 150  # 2.5 minutes for documentation generation

# UI Configuration
UI_CONFIG = {
    "sidebar_width": 300,
    "code_editor_height": 400,
    "preview_height": 300,
    "max_display_lines": 50,
    "items_per_page": 20
}

# Error messages
ERROR_MESSAGES = {
    "groq_api_key_missing": "Groq API key not found. Please set GROQ_API_KEY environment variable.",
    "github_token_missing": "GitHub token not configured. Set GITHUB_TOKEN for private repository access.",
    "file_too_large": "File is too large to process (max {max_size}MB).",
    "unsupported_language": "Programming language not supported.",
    "analysis_timeout": "Analysis timed out. Please try with smaller code samples.",
    "network_error": "Network error. Please check your internet connection.",
    "api_rate_limit": "API rate limit exceeded. Please wait and try again.",
    "invalid_repository": "Repository not found or not accessible.",
    "no_files_found": "No supported files found in the specified location."
}

# Success messages
SUCCESS_MESSAGES = {
    "analysis_complete": "Analysis completed successfully!",
    "translation_complete": "Code translation completed!",
    "documentation_generated": "Documentation generated successfully!",
    "files_uploaded": "Files uploaded and processed successfully!",
    "repository_analyzed": "Repository analysis completed!"
}

# Help text and tips
HELP_TEXT = {
    "code_translation": """
    **For best translation results:**
    - Provide clean, well-structured code
    - Include meaningful variable and function names
    - Add comments to explain complex logic
    - Ensure code is syntactically correct in the source language
    """,
    
    "code_review": """
    **For comprehensive analysis:**
    - Enable all relevant analysis categories
    - Use well-structured, complete code samples
    - Include context and comments in your code
    
    **Understanding severity levels:**
    - **Critical**: Issues that could cause system failures or security breaches
    - **High**: Significant problems affecting functionality or security
    - **Medium**: Moderate issues affecting code quality or performance
    - **Low**: Minor style or improvement suggestions
    """,
    
    "documentation": """
    **For best documentation:**
    - Use descriptive function and variable names
    - Include existing comments and docstrings
    - Provide complete, working code examples
    - Structure code with clear organization
    """,
    
    "github_analysis": """
    **For best results:**
    - Ensure repository is public or you have proper access tokens configured
    - Start with smaller repositories to test functionality
    - Use file extension filters to focus on relevant code
    - Consider file limits for large repositories
    """
}

# Feature flags
FEATURES = {
    "code_translation": True,
    "code_review": True, 
    "documentation_generation": True,
    "github_analysis": True,
    "dark_mode": False,  # Not implemented yet
    "export_reports": True,
    "batch_processing": True
}

# API retry configuration
API_RETRY_CONFIG = {
    "max_retries": 3,
    "retry_delay": 1,  # seconds
    "backoff_factor": 2
}
