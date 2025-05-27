import re
import ast
import json
from typing import Dict, List, Any, Optional
from utils.groq_client import GroqClient
import time

class CodeAnalyzer:
    """Advanced code analysis utilities using Groq LLM"""
    
    def __init__(self, groq_client: GroqClient):
        self.groq_client = groq_client
        
        # Language file extension mappings
        self.language_extensions = {
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
    
    def detect_language(self, code: str, filename: str = "") -> str:
        """
        Detect programming language from code and filename
        
        Args:
            code: Source code
            filename: Optional filename for extension detection
        
        Returns:
            Detected programming language
        """
        # First try file extension
        if filename:
            for ext, lang in self.language_extensions.items():
                if filename.endswith(ext):
                    return lang
        
        # Fallback to pattern matching
        if re.search(r'def\s+\w+\s*\(|import\s+\w+|from\s+\w+\s+import', code):
            return 'Python'
        elif re.search(r'function\s+\w+|const\s+\w+\s*=|let\s+\w+\s*=', code):
            return 'JavaScript'
        elif re.search(r'interface\s+\w+|type\s+\w+\s*=', code):
            return 'TypeScript'
        elif re.search(r'public\s+class\s+\w+|import\s+java\.', code):
            return 'Java'
        elif re.search(r'#include\s*<|int\s+main\s*\(', code):
            return 'C++'
        elif re.search(r'fn\s+\w+|use\s+std::', code):
            return 'Rust'
        elif re.search(r'func\s+\w+|package\s+main', code):
            return 'Go'
        elif re.search(r'<\?php|\$\w+\s*=', code):
            return 'PHP'
        elif re.search(r'def\s+\w+|class\s+\w+|require\s+', code):
            return 'Ruby'
        
        return 'Unknown'
    
    def extract_code_metadata(self, code: str, language: str) -> Dict[str, Any]:
        """
        Extract metadata from code (functions, classes, complexity, etc.)
        
        Args:
            code: Source code
            language: Programming language
        
        Returns:
            Dictionary with code metadata
        """
        metadata = {
            'lines_of_code': len(code.splitlines()),
            'character_count': len(code),
            'function_count': 0,
            'class_count': 0,
            'comment_lines': 0,
            'blank_lines': 0,
            'imports': [],
            'functions': [],
            'classes': []
        }
        
        lines = code.splitlines()
        
        # Count blank lines and comments
        for line in lines:
            stripped = line.strip()
            if not stripped:
                metadata['blank_lines'] += 1
            elif stripped.startswith('#') or stripped.startswith('//') or stripped.startswith('/*'):
                metadata['comment_lines'] += 1
        
        # Language-specific parsing
        if language == 'Python':
            metadata.update(self._parse_python_code(code))
        elif language in ['JavaScript', 'TypeScript']:
            metadata.update(self._parse_javascript_code(code))
        elif language == 'Java':
            metadata.update(self._parse_java_code(code))
        else:
            # Generic parsing for other languages
            metadata.update(self._parse_generic_code(code))
        
        return metadata
    
    def _parse_python_code(self, code: str) -> Dict[str, Any]:
        """Parse Python code for detailed metadata"""
        metadata = {
            'function_count': 0,
            'class_count': 0,
            'imports': [],
            'functions': [],
            'classes': []
        }
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    metadata['function_count'] += 1
                    metadata['functions'].append({
                        'name': node.name,
                        'line': node.lineno,
                        'args': [arg.arg for arg in node.args.args],
                        'has_docstring': (
                            len(node.body) > 0 and 
                            isinstance(node.body[0], ast.Expr) and 
                            isinstance(node.body[0].value, ast.Str)
                        )
                    })
                
                elif isinstance(node, ast.ClassDef):
                    metadata['class_count'] += 1
                    metadata['classes'].append({
                        'name': node.name,
                        'line': node.lineno,
                        'bases': [base.id if hasattr(base, 'id') else str(base) for base in node.bases]
                    })
                
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            metadata['imports'].append(alias.name)
                    else:
                        module = node.module or ''
                        for alias in node.names:
                            metadata['imports'].append(f"{module}.{alias.name}")
        
        except SyntaxError:
            # If AST parsing fails, fall back to regex
            metadata.update(self._parse_generic_code(code))
        
        return metadata
    
    def _parse_javascript_code(self, code: str) -> Dict[str, Any]:
        """Parse JavaScript/TypeScript code for metadata"""
        metadata = {
            'function_count': 0,
            'class_count': 0,
            'imports': [],
            'functions': [],
            'classes': []
        }
        
        lines = code.splitlines()
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Function declarations
            func_match = re.search(r'function\s+(\w+)|const\s+(\w+)\s*=\s*.*?=>|(\w+)\s*:\s*function', stripped)
            if func_match:
                func_name = func_match.group(1) or func_match.group(2) or func_match.group(3)
                metadata['function_count'] += 1
                metadata['functions'].append({
                    'name': func_name,
                    'line': i,
                    'type': 'function'
                })
            
            # Class declarations
            class_match = re.search(r'class\s+(\w+)', stripped)
            if class_match:
                metadata['class_count'] += 1
                metadata['classes'].append({
                    'name': class_match.group(1),
                    'line': i
                })
            
            # Import statements
            import_match = re.search(r'import\s+.*?\s+from\s+[\'"](.+?)[\'"]|import\s+[\'"](.+?)[\'"]', stripped)
            if import_match:
                module = import_match.group(1) or import_match.group(2)
                metadata['imports'].append(module)
        
        return metadata
    
    def _parse_java_code(self, code: str) -> Dict[str, Any]:
        """Parse Java code for metadata"""
        metadata = {
            'function_count': 0,
            'class_count': 0,
            'imports': [],
            'functions': [],
            'classes': []
        }
        
        lines = code.splitlines()
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Method declarations
            method_match = re.search(r'(public|private|protected)?\s*(static)?\s*\w+\s+(\w+)\s*\(', stripped)
            if method_match and not re.search(r'class\s+', stripped):
                metadata['function_count'] += 1
                metadata['functions'].append({
                    'name': method_match.group(3),
                    'line': i,
                    'visibility': method_match.group(1) or 'package'
                })
            
            # Class declarations
            class_match = re.search(r'(public|private)?\s*class\s+(\w+)', stripped)
            if class_match:
                metadata['class_count'] += 1
                metadata['classes'].append({
                    'name': class_match.group(2),
                    'line': i,
                    'visibility': class_match.group(1) or 'package'
                })
            
            # Import statements
            import_match = re.search(r'import\s+([\w\.]+)', stripped)
            if import_match:
                metadata['imports'].append(import_match.group(1))
        
        return metadata
    
    def _parse_generic_code(self, code: str) -> Dict[str, Any]:
        """Generic code parsing for unsupported languages"""
        metadata = {
            'function_count': 0,
            'class_count': 0,
            'imports': [],
            'functions': [],
            'classes': []
        }
        
        # Generic function patterns
        func_patterns = [
            r'def\s+(\w+)',      # Python
            r'function\s+(\w+)', # JavaScript
            r'fn\s+(\w+)',       # Rust
            r'func\s+(\w+)',     # Go
        ]
        
        # Generic class patterns
        class_patterns = [
            r'class\s+(\w+)',    # Most languages
            r'struct\s+(\w+)',   # C++, Rust, Go
        ]
        
        lines = code.splitlines()
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Check for functions
            for pattern in func_patterns:
                match = re.search(pattern, stripped)
                if match:
                    metadata['function_count'] += 1
                    metadata['functions'].append({
                        'name': match.group(1),
                        'line': i
                    })
                    break
            
            # Check for classes
            for pattern in class_patterns:
                match = re.search(pattern, stripped)
                if match:
                    metadata['class_count'] += 1
                    metadata['classes'].append({
                        'name': match.group(1),
                        'line': i
                    })
                    break
        
        return metadata
    
    def translate_code(
        self, 
        code: str, 
        source_language: str, 
        target_language: str,
        preserve_comments: bool = True,
        add_type_hints: bool = False,
        optimize_code: bool = False,
        include_examples: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Translate code between programming languages
        
        Args:
            code: Source code
            source_language: Source programming language
            target_language: Target programming language
            preserve_comments: Whether to preserve comments
            add_type_hints: Whether to add type hints
            optimize_code: Whether to apply optimizations
            include_examples: Whether to include usage examples
        
        Returns:
            Translation result dictionary
        """
        return self.groq_client.translate_code(
            code=code,
            source_language=source_language,
            target_language=target_language,
            preserve_comments=preserve_comments,
            add_type_hints=add_type_hints
        )
    
    def review_code(
        self, 
        code: str, 
        language: str, 
        options: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Perform comprehensive code review
        
        Args:
            code: Code to review
            language: Programming language
            options: Review options
        
        Returns:
            Review results dictionary
        """
        try:
            # Extract code metadata
            metadata = self.extract_code_metadata(code, language)
            
            # Perform different types of analysis based on options
            findings = []
            metrics = {}
            
            # Security analysis
            if options.get('security', True):
                security_result = self.groq_client.analyze_code(code, language, "security")
                if security_result and 'vulnerabilities' in security_result:
                    for vuln in security_result['vulnerabilities']:
                        findings.append({
                            'category': 'Security',
                            'severity': vuln.get('severity', 'Medium'),
                            'title': vuln.get('title', 'Security Issue'),
                            'description': vuln.get('description', ''),
                            'suggestion': vuln.get('fix', ''),
                            'line_number': vuln.get('line', None)
                        })
                    metrics['security_issues'] = len(security_result['vulnerabilities'])
            
            # Performance analysis
            if options.get('performance', True):
                perf_result = self.groq_client.analyze_code(code, language, "performance")
                if perf_result and 'performance_issues' in perf_result:
                    for issue in perf_result['performance_issues']:
                        findings.append({
                            'category': 'Performance',
                            'severity': issue.get('severity', 'Medium'),
                            'title': issue.get('title', 'Performance Issue'),
                            'description': issue.get('description', ''),
                            'suggestion': issue.get('optimization', ''),
                            'line_number': issue.get('line', None)
                        })
            
            # General code quality analysis
            general_result = self.groq_client.analyze_code(code, language, "general")
            if general_result:
                if 'issues' in general_result:
                    for issue in general_result['issues']:
                        # Filter by severity if specified
                        severity = issue.get('severity', 'Medium')
                        if self._should_include_severity(severity, options.get('severity_filter', 'All Issues')):
                            findings.append({
                                'category': 'Code Quality',
                                'severity': severity,
                                'title': issue.get('title', 'Code Issue'),
                                'description': issue.get('description', ''),
                                'suggestion': issue.get('suggestion', ''),
                                'line_number': issue.get('line', None)
                            })
                
                # Overall metrics
                metrics.update({
                    'overall_score': general_result.get('code_quality', 0),
                    'complexity_score': general_result.get('complexity_score', 'N/A'),
                    'critical_issues': len([f for f in findings if f.get('severity') == 'Critical'])
                })
            
            # Calculate additional metrics from metadata
            metrics.update({
                'lines_of_code': metadata['lines_of_code'],
                'function_count': metadata['function_count'],
                'class_count': metadata['class_count'],
                'comment_ratio': metadata['comment_lines'] / max(metadata['lines_of_code'], 1) * 100
            })
            
            # Generate recommendations
            recommendations = self._generate_recommendations(findings, metadata, language)
            
            return {
                'overall_score': metrics.get('overall_score', 50),
                'metrics': metrics,
                'findings': findings,
                'recommendations': recommendations,
                'metadata': metadata
            }
            
        except Exception as e:
            print(f"Code review error: {str(e)}")
            return None
    
    def _should_include_severity(self, severity: str, filter_level: str) -> bool:
        """Check if issue should be included based on severity filter"""
        severity_order = ['Low', 'Medium', 'High', 'Critical']
        
        if filter_level == 'All Issues':
            return True
        
        try:
            severity_idx = severity_order.index(severity)
            filter_idx = severity_order.index(filter_level)
            return severity_idx >= filter_idx
        except ValueError:
            return True
    
    def _generate_recommendations(
        self, 
        findings: List[Dict], 
        metadata: Dict, 
        language: str
    ) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        # High priority recommendations based on findings
        critical_issues = [f for f in findings if f.get('severity') == 'Critical']
        if critical_issues:
            recommendations.append(f"Address {len(critical_issues)} critical issues immediately")
        
        security_issues = [f for f in findings if f.get('category') == 'Security']
        if security_issues:
            recommendations.append(f"Review and fix {len(security_issues)} security vulnerabilities")
        
        # Code structure recommendations
        if metadata.get('function_count', 0) == 0:
            recommendations.append("Consider breaking code into functions for better modularity")
        
        if metadata.get('comment_lines', 0) / max(metadata.get('lines_of_code', 1), 1) < 0.1:
            recommendations.append("Add more comments and documentation to improve code readability")
        
        # Language-specific recommendations
        if language == 'Python':
            if not any('docstring' in str(f) for f in metadata.get('functions', [])):
                recommendations.append("Add docstrings to functions and classes")
        
        elif language in ['JavaScript', 'TypeScript']:
            recommendations.append("Consider using TypeScript for better type safety")
        
        # General best practices
        if metadata.get('lines_of_code', 0) > 500:
            recommendations.append("Consider splitting large files into smaller, focused modules")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def generate_documentation(
        self, 
        code: str, 
        filename: str, 
        options: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Generate comprehensive documentation for code
        
        Args:
            code: Source code
            filename: File name
            options: Documentation options
        
        Returns:
            Documentation result dictionary
        """
        try:
            # Detect language
            language = self.detect_language(code, filename)
            
            # Extract metadata
            metadata = self.extract_code_metadata(code, language)
            
            # Generate documentation using Groq
            documentation = self.groq_client.generate_documentation(
                code=code,
                language=language,
                doc_style=options.get('style', 'comprehensive'),
                include_examples=options.get('include_examples', True)
            )
            
            if documentation:
                # Enhance documentation with metadata if requested
                if options.get('include_metadata', True):
                    enhanced_doc = self._enhance_documentation_with_metadata(
                        documentation, metadata, filename, language
                    )
                    documentation = enhanced_doc
                
                return {
                    'documentation': documentation,
                    'metadata': metadata,
                    'language': language,
                    'filename': filename
                }
            
            return None
            
        except Exception as e:
            print(f"Documentation generation error: {str(e)}")
            return None
    
    def _enhance_documentation_with_metadata(
        self, 
        documentation: str, 
        metadata: Dict, 
        filename: str, 
        language: str
    ) -> str:
        """Enhance documentation with file metadata"""
        
        metadata_section = f"""
# {filename}

## File Information
- **Language**: {language}
- **Lines of Code**: {metadata.get('lines_of_code', 'N/A')}
- **Functions**: {metadata.get('function_count', 0)}
- **Classes**: {metadata.get('class_count', 0)}
- **Comment Lines**: {metadata.get('comment_lines', 0)}

"""
        
        # Add imports section if available
        if metadata.get('imports'):
            metadata_section += "## Dependencies\n"
            for imp in metadata.get('imports', [])[:10]:  # Limit to first 10
                metadata_section += f"- `{imp}`\n"
            metadata_section += "\n"
        
        # Add function overview if available
        if metadata.get('functions'):
            metadata_section += "## Functions Overview\n"
            for func in metadata.get('functions', [])[:10]:  # Limit to first 10
                metadata_section += f"- **{func.get('name', 'Unknown')}** (Line {func.get('line', 'N/A')})\n"
            metadata_section += "\n"
        
        return metadata_section + documentation
    
    def analyze_project_structure(
        self, 
        files_data: Dict[str, str], 
        repo_owner: str, 
        repo_name: str
    ) -> Optional[str]:
        """
        Analyze project structure and generate architectural overview
        
        Args:
            files_data: Dictionary of file paths to contents
            repo_owner: Repository owner
            repo_name: Repository name
        
        Returns:
            Project structure analysis as markdown
        """
        try:
            # Organize files by directory and type
            structure = {}
            languages_used = {}
            
            for file_path, content in files_data.items():
                # Get directory
                dir_path = '/'.join(file_path.split('/')[:-1]) or 'root'
                
                if dir_path not in structure:
                    structure[dir_path] = {
                        'files': [],
                        'total_lines': 0,
                        'languages': set()
                    }
                
                # Detect language and add metadata
                language = self.detect_language(content, file_path)
                metadata = self.extract_code_metadata(content, language)
                
                structure[dir_path]['files'].append({
                    'name': file_path.split('/')[-1],
                    'path': file_path,
                    'language': language,
                    'lines': metadata.get('lines_of_code', 0),
                    'functions': metadata.get('function_count', 0),
                    'classes': metadata.get('class_count', 0)
                })
                
                structure[dir_path]['total_lines'] += metadata.get('lines_of_code', 0)
                structure[dir_path]['languages'].add(language)
                
                # Track overall language usage
                if language not in languages_used:
                    languages_used[language] = 0
                languages_used[language] += metadata.get('lines_of_code', 0)
            
            # Generate analysis
            analysis = f"""# Project Structure Analysis: {repo_owner}/{repo_name}

## Overview
This project contains {len(files_data)} analyzed files across {len(structure)} directories.

## Language Distribution
"""
            
            # Sort languages by usage
            sorted_languages = sorted(languages_used.items(), key=lambda x: x[1], reverse=True)
            for lang, lines in sorted_languages:
                if lang != 'Unknown':
                    percentage = (lines / sum(languages_used.values())) * 100
                    analysis += f"- **{lang}**: {lines} lines ({percentage:.1f}%)\n"
            
            analysis += "\n## Directory Structure\n"
            
            # Analyze each directory
            for dir_path, dir_info in sorted(structure.items()):
                analysis += f"\n### {dir_path}/\n"
                analysis += f"- **Files**: {len(dir_info['files'])}\n"
                analysis += f"- **Total Lines**: {dir_info['total_lines']}\n"
                analysis += f"- **Languages**: {', '.join(dir_info['languages'])}\n"
                
                # List important files
                important_files = sorted(dir_info['files'], key=lambda x: x['lines'], reverse=True)[:5]
                if important_files:
                    analysis += "\n**Key Files:**\n"
                    for file_info in important_files:
                        analysis += f"- `{file_info['name']}` ({file_info['language']}, {file_info['lines']} lines"
                        if file_info['functions'] > 0:
                            analysis += f", {file_info['functions']} functions"
                        if file_info['classes'] > 0:
                            analysis += f", {file_info['classes']} classes"
                        analysis += ")\n"
            
            return analysis
            
        except Exception as e:
            print(f"Project structure analysis error: {str(e)}")
            return None
    
    def generate_enhanced_readme(
        self, 
        repo_info: Dict, 
        analysis_results: Dict, 
        files_data: Dict[str, str]
    ) -> Optional[str]:
        """
        Generate an enhanced README based on repository analysis
        
        Args:
            repo_info: Repository information from GitHub
            analysis_results: Results from code analysis
            files_data: Repository files content
        
        Returns:
            Enhanced README content as markdown
        """
        try:
            # Extract key information
            total_lines = sum(
                result.get('metadata', {}).get('lines_of_code', 0)
                for result in analysis_results.values()
            )
            
            total_functions = sum(
                result.get('metadata', {}).get('function_count', 0)
                for result in analysis_results.values()
            )
            
            # Detect main language and frameworks
            languages = {}
            for file_path, content in files_data.items():
                lang = self.detect_language(content, file_path)
                if lang != 'Unknown':
                    languages[lang] = languages.get(lang, 0) + 1
            
            main_language = max(languages.items(), key=lambda x: x[1])[0] if languages else 'Unknown'
            
            # Generate README content
            readme = f"""# {repo_info.get('name', 'Repository')}

{repo_info.get('description', 'A software project')}

## 📊 Project Statistics
- **Lines of Code**: {total_lines:,}
- **Files Analyzed**: {len(analysis_results)}
- **Functions**: {total_functions}
- **Primary Language**: {main_language}
- **Repository Size**: {repo_info.get('size', 0) / 1024:.1f} MB

## 🚀 Languages & Technologies
"""
            
            # List languages used
            sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)
            for lang, count in sorted_langs[:5]:  # Top 5 languages
                readme += f"- {lang}\n"
            
            readme += f"""
## 📁 Project Structure

This project is organized into {len(set(f.split('/')[0] for f in files_data.keys() if '/' in f))} main directories:

"""
            
            # Add directory overview
            directories = {}
            for file_path in files_data.keys():
                if '/' in file_path:
                    dir_name = file_path.split('/')[0]
                    directories[dir_name] = directories.get(dir_name, 0) + 1
            
            for dir_name, file_count in sorted(directories.items()):
                readme += f"- `{dir_name}/` - {file_count} files\n"
            
            # Add setup and usage sections
            readme += f"""
## 🛠️ Installation

```bash
git clone https://github.com/{repo_info.get('owner', {}).get('login', 'owner')}/{repo_info.get('name', 'repo')}.git
cd {repo_info.get('name', 'repo')}
