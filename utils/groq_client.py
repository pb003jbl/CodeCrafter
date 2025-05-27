import os
import requests
import json
from typing import Dict, Any, Optional

class GroqClient:
    """Client for interacting with Groq LLM API"""
    
    def __init__(self):
        # Check session state first, then environment variable
        import streamlit as st
        self.api_key = None
        
        # Try to get from session state first
        if hasattr(st, 'session_state') and 'groq_api_key' in st.session_state:
            self.api_key = st.session_state['groq_api_key']
        
        # Fallback to environment variable
        if not self.api_key:
            self.api_key = os.getenv("GROQ_API_KEY")
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in session state or environment variables")
        
        self.base_url = "https://api.groq.com/openai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Default model - using Groq's fastest model for code analysis
        self.default_model = "llama3-8b-8192"
    
    def generate_completion(
        self, 
        prompt: str, 
        model: Optional[str] = None,
        max_tokens: int = 4000,
        temperature: float = 0.1,
        system_prompt: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate completion using Groq API
        
        Args:
            prompt: The user prompt
            model: Model to use (defaults to default_model)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            system_prompt: Optional system prompt
        
        Returns:
            Generated text or None if failed
        """
        try:
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user", 
                "content": prompt
            })
            
            payload = {
                "model": model or self.default_model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=120  # 2 minute timeout for large requests
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                print(f"Groq API error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            print("Groq API request timed out")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Groq API request failed: {str(e)}")
            return None
        except Exception as e:
            print(f"Unexpected error in Groq client: {str(e)}")
            return None
    
    def analyze_code(
        self, 
        code: str, 
        language: str, 
        analysis_type: str = "general"
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze code using Groq LLM
        
        Args:
            code: Code to analyze
            language: Programming language
            analysis_type: Type of analysis (general, security, performance, etc.)
        
        Returns:
            Analysis results as dictionary
        """
        
        system_prompt = f"""You are an expert code analyst specializing in {language}. 
        Provide detailed, actionable analysis in JSON format."""
        
        if analysis_type == "security":
            user_prompt = f"""Analyze this {language} code for security vulnerabilities:

```{language.lower()}
{code}
```

Provide a detailed JSON response with the following structure:
{{
    "vulnerabilities": [
        {{
            "title": "vulnerability name",
            "description": "detailed description",
            "severity": "Critical|High|Medium|Low",
            "line": line_number,
            "fix": "suggested fix"
        }}
    ],
    "security_score": score_out_of_100
}}"""
        
        elif analysis_type == "performance":
            user_prompt = f"""Analyze this {language} code for performance issues:

```{language.lower()}
{code}
```

Provide a detailed JSON response with the following structure:
{{
    "performance_issues": [
        {{
            "title": "performance issue",
            "description": "detailed description",
            "severity": "Critical|High|Medium|Low",
            "line": line_number,
            "optimization": "suggested optimization"
        }}
    ],
    "performance_score": score_out_of_100
}}"""

        else:  # general analysis
            user_prompt = f"""Analyze this {language} code for overall quality:

```{language.lower()}
{code}
```

Provide a detailed JSON response with the following structure:
{{
    "issues": [
        {{
            "title": "issue title",
            "description": "detailed description",
            "severity": "Critical|High|Medium|Low",
            "line": line_number,
            "suggestion": "improvement suggestion"
        }}
    ],
    "code_quality": score_out_of_100,
    "complexity_score": complexity_rating
}}"""
        
        try:
            response = self.generate_completion(
                prompt=user_prompt,
                system_prompt=system_prompt,
                max_tokens=3000,
                temperature=0.1
            )
            
            if response:
                # Try to parse JSON response
                import json
                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    # If JSON parsing fails, return a simplified structure
                    return {
                        "analysis": response,
                        "error": "Could not parse JSON response"
                    }
            
            return None
            
        except Exception as e:
            print(f"Code analysis error: {str(e)}")
            return None
    
    def translate_code(
        self, 
        code: str, 
        source_language: str, 
        target_language: str, 
        preserve_comments: bool = True,
        add_type_hints: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Translate code between programming languages
        
        Args:
            code: Source code to translate
            source_language: Source programming language
            target_language: Target programming language
            preserve_comments: Whether to preserve comments
            add_type_hints: Whether to add type hints
        
        Returns:
            Translation result dictionary
        """
        
        system_prompt = f"""You are an expert programmer proficient in {source_language} and {target_language}.
        Translate code accurately while maintaining functionality and readability."""
        
        options_text = []
        if preserve_comments:
            options_text.append("preserve existing comments")
        if add_type_hints:
            options_text.append("add appropriate type hints")
        
        options_str = " and ".join(options_text) if options_text else "maintain clean code style"
        
        user_prompt = f"""Translate this {source_language} code to {target_language}:

```{source_language.lower()}
{code}
```

Requirements:
- Maintain the same functionality
- Use {target_language} best practices and idioms
- {options_str}
- Ensure the translated code is syntactically correct

Provide a JSON response with this structure:
{{
    "translated_code": "complete translated code",
    "notes": "translation notes and explanations",
    "confidence": confidence_score_out_of_100
}}"""
        
        try:
            response = self.generate_completion(
                prompt=user_prompt,
                system_prompt=system_prompt,
                max_tokens=4000,
                temperature=0.1
            )
            
            if response:
                import json
                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    # Fallback if JSON parsing fails
                    return {
                        "translated_code": response,
                        "notes": "Translation completed but could not parse structured response",
                        "confidence": 85
                    }
            
            return None
            
        except Exception as e:
            print(f"Code translation error: {str(e)}")
            return None
