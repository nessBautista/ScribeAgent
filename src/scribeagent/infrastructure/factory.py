# src/scribeagent/infrastructure/factory.py

from scribeagent.infrastructure.notion.api_client import NotionAPIClient
from scribeagent.infrastructure.notion.repositories import NotionAPIPageRepository
from scribeagent.application.services.notion_services import NotionPageService
from scribeagent.utils.NotionAPIUrlParser import NotionAPIUrlParser


def create_notion_page_service(api_key, debug=False, max_depth=3):
    """
    Factory function to create and wire a NotionPageService with all its dependencies.
    
    Args:
        api_key: The Notion API key to use
        debug: Enable debug mode to see API responses
        max_depth: Maximum recursion depth for fetching nested blocks
        
    Returns:
        A fully configured NotionPageService
    """
    # Create infrastructure components
    api_client = NotionAPIClient(api_key=api_key, debug=debug)
    page_repository = NotionAPIPageRepository(api_client=api_client, max_depth=max_depth)
    url_parser = NotionAPIUrlParser()
    
    # Create and return the service
    return NotionPageService(page_repository=page_repository, url_parser=url_parser)