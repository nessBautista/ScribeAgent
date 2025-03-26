import os
from dotenv import load_dotenv

# Only import the domain entities needed for the example
from scribeagent.domain.notion.entities import TextBlock, CodeBlock

# Add the factory to create and wire dependencies
from scribeagent.infrastructure.factory import create_notion_page_service


def example_usage():
    """Example usage of the Notion domain model."""
    # Load environment variables
    load_dotenv()
    
    # Get API key from environment
    api_key = os.getenv("NOTION_API_KEY")
    
    # Use a factory to create the service with all its dependencies
    page_service = create_notion_page_service(api_key)
    
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
        if isinstance(block, CodeBlock):
            print(f"- {block.block_type.value} ({block.language}):")
            print(f"```{block.language}")
            print(block.get_plain_text())
            print("```")
            
            if block.caption:
                caption_text = ''.join(caption.plain_text for caption in block.caption)
                if caption_text:
                    print(f"Caption: {caption_text}")
        elif isinstance(block, TextBlock):
            print(f"- {block.block_type.value}: {block.get_plain_text()}")
        else:
            print(f"- {block.block_type.value}")


if __name__ == "__main__":
    example_usage()
