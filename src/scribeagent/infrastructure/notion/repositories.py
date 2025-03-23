from typing import List, Dict, Any, Optional

from scribeagent.domain.notion.repositories import PageRepository, DatabaseRepository
from scribeagent.domain.notion.entities import Page, Database, Block
from .api_client import NotionAPIClient


class NotionAPIPageRepository(PageRepository):
    """Implementation of page repository using Notion API."""
    
    def __init__(self, api_client: NotionAPIClient):
        self.api_client = api_client
    
    def get_page(self, page_id: str) -> Page:
        """Get a page by ID."""
        data = self.api_client.get_page(page_id)
        return Page.from_api(data)
    
    def get_page_content(self, page_id: str) -> List[Block]:
        """Get the content of a page."""
        blocks = []
        start_cursor = None
        
        while True:
            response = self.api_client.get_block_children(page_id, start_cursor)
            
            for block_data in response.get("results", []):
                block = Block.from_api(block_data)
                blocks.append(block)
                
                # Recursively get children if needed
                if block.has_children:
                    child_blocks = self.get_page_content(block.id)
                    # In a real implementation, you'd associate these child blocks with their parent
            
            if response.get("has_more", False):
                start_cursor = response.get("next_cursor")
            else:
                break
        
        return blocks

class NotionAPIDatabaseRepository(DatabaseRepository):
    """Implementation of database repository using Notion API."""
    
    def __init__(self, api_client: NotionAPIClient):
        self.api_client = api_client
    
    def get_database(self, database_id: str) -> Database:
        """Get a database by ID."""
        data = self.api_client.get_database(database_id)
        return Database.from_api(data)
    
    def query_database(self, database_id: str, filter_params: Optional[Dict[str, Any]] = None) -> List[Page]:
        """Query a database."""
        pages = []
        start_cursor = None
        
        while True:
            response = self.api_client.query_database(database_id, filter_params, start_cursor)
            
            for page_data in response.get("results", []):
                page = Page.from_api(page_data)
                pages.append(page)
            
            if response.get("has_more", False):
                start_cursor = response.get("next_cursor")
            else:
                break
        
        return pages
