#!/usr/bin/env python
import os
import argparse
from dotenv import load_dotenv

from scribeagent.domain.notion.entities import TextBlock
from scribeagent.infrastructure.factory import create_notion_page_service


def notion_get_page(url, api_key=None, debug=False, max_depth=5):
    """
    Get a Notion page by URL and print its content.
    
    Args:
        url: The Notion page URL
        api_key: Optional Notion API key (will use environment variable if not provided)
        debug: Enable debug mode to see API responses
        max_depth: Maximum recursion depth for fetching nested blocks
    """
    # Get API key from environment if not provided
    if not api_key:
        api_key = os.getenv("NOTION_API_KEY")
        if not api_key:
            raise ValueError("No Notion API key provided. Set NOTION_API_KEY environment variable or use --api-key option.")
    
    # Use a factory to create the service with all its dependencies
    # Pass debug flag and max_depth to the factory
    page_service = create_notion_page_service(api_key, debug=debug, max_depth=max_depth)
    
    # Get page by URL
    page, content = page_service.get_page_with_content(url)
    
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


def main():
    """Command line interface for Notion page viewer."""
    # Load environment variables
    load_dotenv()
    
    # Create argument parser
    parser = argparse.ArgumentParser(description="Retrieve and display Notion page content")
    parser.add_argument("url", help="URL of the Notion page to retrieve")
    parser.add_argument("--api-key", help="Notion API key (defaults to NOTION_API_KEY environment variable)")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode to see API responses")
    parser.add_argument("--max-depth", type=int, default=3, help="Maximum recursion depth for fetching nested blocks")
    
    # Parse arguments
    args = parser.parse_args()
    
    try:
        notion_get_page(args.url, args.api_key, args.debug, args.max_depth)
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())