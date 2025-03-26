from typing import List, Tuple, Dict, Any

from scribeagent.domain.notion.repositories import PageRepository, DatabaseRepository
from scribeagent.domain.notion.entities import Page, Block, TextBlock, CodeBlock
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
    
    def search_blocks(self, query: str, url: str) -> List[Dict[str, Any]]:
        """Search for blocks in a page that match the query."""
        # Get the page content
        blocks = self.get_page_content_by_url(url)
        matching_blocks = []
        
        def search_block(block: Block) -> None:
            """Helper function to search through a block and its children."""
            if isinstance(block, (TextBlock, CodeBlock)):
                block_text = block.get_plain_text().lower()
                if query.lower() in block_text:
                    block_info = {
                        "type": block.block_type.value,
                        "content": block.get_plain_text()
                    }
                    if isinstance(block, CodeBlock):
                        block_info["language"] = block.language
                    
                    # Add children if they exist
                    if block.has_children and block.children:
                        block_info["children"] = []
                        for child in block.children:
                            if isinstance(child, (TextBlock, CodeBlock)):
                                child_info = {
                                    "type": child.block_type.value,
                                    "content": child.get_plain_text()
                                }
                                if isinstance(child, CodeBlock):
                                    child_info["language"] = child.language
                                block_info["children"].append(child_info)
                    
                    matching_blocks.append(block_info)
            
            # Recursively search through children
            if block.has_children and block.children:
                for child in block.children:
                    search_block(child)
        
        # Search through all blocks
        for block in blocks:
            search_block(block)
        
        return matching_blocks
