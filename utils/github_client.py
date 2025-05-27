import os
import requests
import base64
from typing import Dict, List, Optional, Any
import time

class GitHubClient:
    """Client for interacting with GitHub API"""
    
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"
        
        # Set up headers
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Developer-Productivity-Suite/1.0"
        }
        
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
    
    def get_repository_info(self, owner: str, repo: str) -> Optional[Dict[str, Any]]:
        """
        Get repository information
        
        Args:
            owner: Repository owner (username or organization)
            repo: Repository name
        
        Returns:
            Repository information dictionary
        """
        try:
            url = f"{self.base_url}/repos/{owner}/{repo}"
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                raise Exception("Repository not found or not accessible")
            elif response.status_code == 403:
                raise Exception("Access forbidden - check your GitHub token permissions")
            else:
                raise Exception(f"GitHub API error: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error accessing GitHub: {str(e)}")
    
    def get_repository_contents(
        self, 
        owner: str, 
        repo: str, 
        path: str = ""
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get repository contents for a specific path
        
        Args:
            owner: Repository owner
            repo: Repository name
            path: Path within repository (empty for root)
        
        Returns:
            List of file/directory information
        """
        try:
            url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                raise Exception(f"GitHub API error: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error: {str(e)}")
    
    def get_file_content(self, owner: str, repo: str, file_path: str) -> Optional[str]:
        """
        Get content of a specific file
        
        Args:
            owner: Repository owner
            repo: Repository name
            file_path: Path to the file
        
        Returns:
            File content as string
        """
        try:
            url = f"{self.base_url}/repos/{owner}/{repo}/contents/{file_path}"
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                file_data = response.json()
                
                # Handle file size limit (GitHub API limit is 1MB)
                if file_data.get('size', 0) > 1024 * 1024:  # 1MB
                    raise Exception(f"File {file_path} is too large (>{1}MB)")
                
                # Decode base64 content
                if file_data.get('content'):
                    content = base64.b64decode(file_data['content']).decode('utf-8', errors='ignore')
                    return content
                else:
                    # Handle large files or binary files
                    download_url = file_data.get('download_url')
                    if download_url:
                        file_response = requests.get(download_url, timeout=30)
                        if file_response.status_code == 200:
                            return file_response.text
                
            return None
            
        except UnicodeDecodeError:
            # Skip binary files
            return None
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error fetching file {file_path}: {str(e)}")
    
    def get_repository_files(
        self, 
        owner: str, 
        repo: str,
        max_files: int = 50,
        file_extensions: List[str] = None,
        ignore_patterns: List[str] = None
    ) -> Dict[str, str]:
        """
        Get multiple files from repository with filtering
        
        Args:
            owner: Repository owner
            repo: Repository name
            max_files: Maximum number of files to retrieve
            file_extensions: List of file extensions to include (e.g., ['.py', '.js'])
            ignore_patterns: List of patterns to ignore (e.g., ['node_modules/', '.git/'])
        
        Returns:
            Dictionary mapping file paths to their contents
        """
        if file_extensions is None:
            file_extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.rs', '.go']
        
        if ignore_patterns is None:
            ignore_patterns = [
                'node_modules/', '.git/', '__pycache__/', '.env', 
                'venv/', 'env/', 'build/', 'dist/', '.pytest_cache/'
            ]
        
        files_content = {}
        files_found = 0
        
        def should_ignore_path(path: str) -> bool:
            """Check if path should be ignored based on patterns"""
            for pattern in ignore_patterns:
                if pattern in path:
                    return True
            return False
        
        def has_valid_extension(path: str) -> bool:
            """Check if file has a valid extension"""
            return any(path.endswith(ext) for ext in file_extensions)
        
        def explore_directory(path: str = ""):
            """Recursively explore directory contents"""
            nonlocal files_found
            
            if files_found >= max_files:
                return
            
            try:
                contents = self.get_repository_contents(owner, repo, path)
                
                if not contents:
                    return
                
                for item in contents:
                    if files_found >= max_files:
                        break
                    
                    item_path = item['path']
                    
                    # Skip ignored paths
                    if should_ignore_path(item_path):
                        continue
                    
                    if item['type'] == 'file':
                        # Check if file has valid extension
                        if has_valid_extension(item_path):
                            try:
                                content = self.get_file_content(owner, repo, item_path)
                                if content:
                                    files_content[item_path] = content
                                    files_found += 1
                            except Exception as e:
                                print(f"Warning: Could not fetch {item_path}: {str(e)}")
                    
                    elif item['type'] == 'dir' and files_found < max_files:
                        # Recursively explore subdirectory
                        explore_directory(item_path)
                
            except Exception as e:
                print(f"Warning: Could not explore directory {path}: {str(e)}")
        
        try:
            explore_directory()
            return files_content
            
        except Exception as e:
            raise Exception(f"Error retrieving repository files: {str(e)}")
    
    def get_recent_commits(
        self, 
        owner: str, 
        repo: str, 
        limit: int = 10
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get recent commits from repository
        
        Args:
            owner: Repository owner
            repo: Repository name
            limit: Number of commits to retrieve
        
        Returns:
            List of commit information
        """
        try:
            url = f"{self.base_url}/repos/{owner}/{repo}/commits"
            params = {"per_page": limit}
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"GitHub API error: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error fetching commits: {str(e)}")
    
    def get_repository_languages(self, owner: str, repo: str) -> Optional[Dict[str, int]]:
        """
        Get programming languages used in repository
        
        Args:
            owner: Repository owner
            repo: Repository name
        
        Returns:
            Dictionary of languages and their byte counts
        """
        try:
            url = f"{self.base_url}/repos/{owner}/{repo}/languages"
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except requests.exceptions.RequestException:
            return None
    
    def search_repositories(
        self, 
        query: str, 
        sort: str = "stars", 
        limit: int = 10
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Search for repositories
        
        Args:
            query: Search query
            sort: Sort criteria (stars, forks, updated)
            limit: Number of results to return
        
        Returns:
            List of repository information
        """
        try:
            url = f"{self.base_url}/search/repositories"
            params = {
                "q": query,
                "sort": sort,
                "order": "desc",
                "per_page": limit
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('items', [])
            else:
                raise Exception(f"GitHub API error: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error searching repositories: {str(e)}")
    
    def check_rate_limit(self) -> Dict[str, Any]:
        """
        Check current rate limit status
        
        Returns:
            Rate limit information
        """
        try:
            url = f"{self.base_url}/rate_limit"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API error: {response.status_code}"}
                
        except requests.exceptions.RequestException as e:
            return {"error": f"Network error: {str(e)}"}
    
    def is_repository_accessible(self, owner: str, repo: str) -> bool:
        """
        Check if repository is accessible
        
        Args:
            owner: Repository owner
            repo: Repository name
        
        Returns:
            True if accessible, False otherwise
        """
        try:
            self.get_repository_info(owner, repo)
            return True
        except:
            return False
