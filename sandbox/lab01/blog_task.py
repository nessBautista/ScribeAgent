import os
import re
import requests
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

class BlogTask:
    """Class to handle fetching and combining blog task information from Linear and Notion."""
    
    def __init__(self):
        """Initialize the BlogTask with environment variables."""
        load_dotenv()
        self._validate_env_vars()
        
    def _validate_env_vars(self) -> None:
        """Validate required environment variables are present."""
        required_vars = ['LINEAR_API_KEY', 'LINEAR_PROJECT_ID', 'NOTION_API_KEY']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    def _extract_notion_id_from_url(self, url: str) -> Optional[str]:
        """Extract Notion page ID from URL."""
        pattern = r'[a-f0-9]{8}-?[a-f0-9]{4}-?[a-f0-9]{4}-?[a-f0-9]{4}-?[a-f0-9]{12}'
        match = re.search(pattern, url)
        return match.group(0).replace('-', '') if match else None
    
    def _get_linear_tasks(self, state_filter: str = "Todo") -> List[Dict[str, Any]]:
        """Fetch tasks from Linear."""
        api_key = os.getenv('LINEAR_API_KEY')
        project_id = os.getenv('LINEAR_PROJECT_ID')
        
        query = """
        query Issues($projectId: ID!) {
          issues(filter: { 
            project: { id: { eq: $projectId } },
            state: { name: { eq: "Todo" } }
          }) {
            nodes {
              id
              title
              description
              state {
                name
              }
            }
          }
        }
        """
        
        response = requests.post(
            "https://api.linear.app/graphql",
            headers={
                "Authorization": api_key,
                "Content-Type": "application/json"
            },
            json={
                "query": query,
                "variables": {"projectId": project_id}
            }
        )
        
        if response.status_code != 200:
            raise requests.RequestException(f"Linear API error: {response.text}")
            
        data = response.json()
        if not (data.get("data", {}).get("issues", {}).get("nodes")):
            raise ValueError("No tasks found in Linear response")
            
        return data["data"]["issues"]["nodes"]
    
    def _get_notion_content(self, page_id: str) -> List[str]:
        """Fetch content from Notion page."""
        api_key = os.getenv('NOTION_API_KEY')
        
        response = requests.get(
            f"https://api.notion.com/v1/blocks/{page_id}/children",
            headers={
                'Authorization': f'Bearer {api_key}',
                'Notion-Version': '2022-06-28',
                'Content-Type': 'application/json'
            }
        )
        
        if response.status_code != 200:
            raise requests.RequestException(f"Notion API error: {response.text}")
            
        blocks = response.json().get("results", [])
        content = []
        
        for block in blocks:
            block_type = block.get("type")
            if not block_type:
                continue
                
            rich_text = block.get(block_type, {}).get("rich_text", [])
            text = " ".join(rt.get("text", {}).get("content", "") for rt in rich_text)
            if text:
                content.append(text)
                
        return content
    
    def get_task(self) -> str:
        """
        Main method to fetch a Linear task and its associated Notion content.
        
        Returns:
            str: Formatted string containing task title, description, and blog post draft
            
        Raises:
            ValueError: If no tasks found or missing required environment variables
            requests.RequestException: If API requests fail
        """
        # Get first Linear task
        tasks = self._get_linear_tasks()
        if not tasks:
            raise ValueError("No tasks found in Linear")
        
        task = tasks[0]
        
        # Extract Notion URL and ID
        notion_id = None
        if description := task.get('description'):
            urls = re.findall(r'https://(?:www\.)?notion\.so/[^\s\)]+', description)
            if urls:
                notion_id = self._extract_notion_id_from_url(urls[0])
        
        # Format the content
        content_parts = [
            f"# {task['title']}\n",
            f"## Task Description\n{task.get('description', 'No description')}\n",
            "## Blog Post Draft\n"
        ]
        
        # Add Notion content if available
        if notion_id:
            try:
                notion_content = self._get_notion_content(notion_id)
                content_parts.append('\n'.join(notion_content))
            except Exception as e:
                content_parts.append(f"Error fetching Notion content: {str(e)}")
        else:
            content_parts.append("No draft content available")
        
        return '\n'.join(content_parts) 