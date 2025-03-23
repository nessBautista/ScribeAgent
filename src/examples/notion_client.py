import os
from dotenv import load_dotenv

from scribeagent.infrastructure.notion.api_client import NotionAPIClient
from scribeagent.infrastructure.notion.repositories import NotionAPIPageRepository
from scribeagent.application.services.notion_services import NotionPageService
from scribeagent.utils.NotionAPIUrlParser import NotionAPIUrlParser
from scribeagent.domain.notion.entities import TextBlock


def example_usage():
    """Example usage of the Notion domain model."""
    # Load environment variables
    load_dotenv()
    
    # # Set up dependencies
    api_key = os.getenv("NOTION_API_KEY")    
    api_client = NotionAPIClient(api_key)
    page_repository = NotionAPIPageRepository(api_client)
    url_parser = NotionAPIUrlParser()
    
    # Create service
    page_service = NotionPageService(page_repository, url_parser)
    
    # Get page by URL
    page_url = "https://www.notion.so/Installing-Objectbox-with-an-xcode-project-19e10ad7d21e80eab058fa47a33eb1df?pvs=4"
    page, content = page_service.get_page_with_content(page_url)
    
    # Print page information
    print(f"Page Title: {page.get_title()}")
    print(f"URL: {page.url}")
    print(f"Created: {page.created_time}")
    print(f"Last Edited: {page.last_edited_time}")
    
    # Print page content
    print("\nPage Content:")
    for block in content:
        if isinstance(block, TextBlock):
            print(f"- {block.block_type.value}: {block.get_plain_text()}")
        else:
            print(f"- {block.block_type.value}")


if __name__ == "__main__":
    example_usage()
