import os
import requests
import json
from typing import Dict, Any, Optional

class GroqClient:
    """Client for interacting with Groq LLM API"""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
        
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
