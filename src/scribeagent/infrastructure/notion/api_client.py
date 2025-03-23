import requests
import json
from typing import Dict, Any, Optional


class NotionAPIClient:
    """Client for the Notion API."""
    
    def __init__(self, api_key: str, api_version: str = "2022-06-28", debug: bool = True):
        self.api_key = api_key
        self.api_version = api_version
        self.base_url = "https://api.notion.com/v1"
        self.debug = debug
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Notion-Version": api_version,
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, 
                     data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a request to the Notion API."""
        url = f"{self.base_url}{endpoint}"
        
        response = requests.request(
            method=method,
            url=url,
            headers=self.headers,
            params=params,
            json=data
        )
        
        response.raise_for_status()
        response_json = response.json()
        
        # Log the response if debug is enabled
        if self.debug:
            print(f"\n--- Notion API Response for {endpoint} ---")
            print(json.dumps(response_json, indent=2))
            print("-------------------------------------------\n")
        
        return response_json
    
    def get_page(self, page_id: str) -> Dict[str, Any]:
        """Get a page from the Notion API."""
        return self._make_request("GET", f"/pages/{page_id}")
    
    def get_block_children(self, block_id: str, start_cursor: Optional[str] = None, 
                          page_size: int = 100) -> Dict[str, Any]:
        """Get the children of a block from the Notion API."""
        params = {"page_size": page_size}
        if start_cursor:
            params["start_cursor"] = start_cursor
            
        return self._make_request("GET", f"/blocks/{block_id}/children", params=params)
    
    def get_database(self, database_id: str) -> Dict[str, Any]:
        """Get a database from the Notion API."""
        return self._make_request("GET", f"/databases/{database_id}")
    
    def query_database(self, database_id: str, filter_params: Optional[Dict[str, Any]] = None, 
                      start_cursor: Optional[str] = None, page_size: int = 100) -> Dict[str, Any]:
        """Query a database from the Notion API."""
        data = {"page_size": page_size}
        if filter_params:
            data.update(filter_params)
        if start_cursor:
            data["start_cursor"] = start_cursor
            
        return self._make_request("POST", f"/databases/{database_id}/query", data=data)
