from typing import List, Tuple

from scribeagent.domain.notion.repositories import PageRepository, DatabaseRepository
from scribeagent.domain.notion.entities import Page, Block
from scribeagent.utils.NotionAPIUrlParser import NotionAPIUrlParser


class NotionPageService:
    """Service for working with Notion pages."""
    
    def __init__(self, page_repository: PageRepository, url_parser: NotionAPIUrlParser):
        self.page_repository = page_repository
        self.url_parser = url_parser
    
    def get_page_by_url(self, url: str) -> Page:
        """Get a page by URL."""
        page_id = self.url_parser.extract_id_from_url(url)
        return self.page_repository.get_page(page_id)
    
    def get_page_content_by_url(self, url: str) -> List[Block]:
        """Get the content of a page by URL."""
        page_id = self.url_parser.extract_id_from_url(url)
        return self.page_repository.get_page_content(page_id)
    
    def get_page_with_content(self, url_or_id: str) -> Tuple[Page, List[Block]]:
        """Get a page with its content."""
        if "notion.so" in url_or_id:
            page_id = self.url_parser.extract_id_from_url(url_or_id)
        else:
            page_id = url_or_id
            
        page = self.page_repository.get_page(page_id)
        content = self.page_repository.get_page_content(page_id)
        
        return page, content
