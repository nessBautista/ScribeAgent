#!/usr/bin/env python
import os
import argparse
import json
from dotenv import load_dotenv
from rich.console import Console
from rich.syntax import Syntax

from scribeagent.domain.notion.entities import TextBlock
from scribeagent.infrastructure.factory import create_notion_page_service
from scribeagent.infrastructure.notion.api_client import NotionAPIClient


class VerboseNotionAPIClient(NotionAPIClient):
    """Extension of NotionAPIClient that captures API responses for verbose output."""
    
    def __init__(self, api_key: str, api_version: str = "2022-06-28", debug: bool = True, console: Console = None):
        super().__init__(api_key, api_version, debug)
        self.console = console or Console()
        self.last_response = None
    
    def _make_request(self, method, endpoint, params=None, data=None):
        """Override _make_request to capture the response for verbose output."""
        response = super()._make_request(method, endpoint, params, data)
        self.last_response = response
        return response


def notion_get_page(url, api_key=None, debug=False, max_depth=None, verbose=False):
    """
    Get a Notion page by URL and print its content.
    
    Args:
        url: The Notion page URL
        api_key: Optional Notion API key (will use environment variable if not provided)
        debug: Enable debug mode to see API responses
        max_depth: Maximum recursion depth for fetching nested blocks
        verbose: Enable verbose output with rich formatting
    """
    # Get API key from environment if not provided
    if not api_key:
        api_key = os.getenv("NOTION_API_KEY")
        if not api_key:
            raise ValueError("No Notion API key provided. Set NOTION_API_KEY environment variable or use --api-key option.")
    
    # Create console for rich output
    console = Console()
    
    # Create a verbose API client if verbose mode is enabled
    if verbose:
        api_client = VerboseNotionAPIClient(api_key=api_key, debug=debug, console=console)
        # Create a custom page service with our verbose client
        from scribeagent.utils.NotionAPIUrlParser import NotionAPIUrlParser
        from scribeagent.infrastructure.notion.repositories import NotionAPIPageRepository
        from scribeagent.application.services.notion_services import NotionPageService
        
        page_repository = NotionAPIPageRepository(api_client=api_client, max_depth=max_depth)
        url_parser = NotionAPIUrlParser()
        page_service = NotionPageService(page_repository=page_repository, url_parser=url_parser)
    else:
        # Use the factory for non-verbose mode
        page_service = create_notion_page_service(api_key, debug=debug, max_depth=max_depth)
    
    # Get page by URL
    page, content = page_service.get_page_with_content(url)
    
    # Print page information
    if verbose:
        console.print(f"[bold cyan]Page Title:[/bold cyan] {page.get_title()}")
        console.print(f"[bold cyan]URL:[/bold cyan] {page.url}")
        console.print(f"[bold cyan]Created:[/bold cyan] {page.created_time}")
        console.print(f"[bold cyan]Last Edited:[/bold cyan] {page.last_edited_time}")
        
        # Display the raw API response if verbose mode is enabled
        if hasattr(page_service.page_repository.api_client, 'last_response') and page_service.page_repository.api_client.last_response:
            console.print("\n[bold green]API Response:[/bold green]")
            json_str = json.dumps(page_service.page_repository.api_client.last_response, indent=2)
            syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
            console.print(syntax)
        
        # Print page content with rich formatting
        console.print("\n[bold green]Page Content:[/bold green]")
        for block in content:
            if isinstance(block, TextBlock):
                block_type = f"[bold blue]{block.block_type.value}[/bold blue]"
                text = block.get_plain_text()
                console.print(f"- {block_type}: {text}")
            else:
                console.print(f"- [bold yellow]{block.block_type.value}[/bold yellow]")
    else:
        # Standard output format
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
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output with rich formatting")
    
    # Parse arguments
    args = parser.parse_args()
    
    try:
        notion_get_page(args.url, args.api_key, args.debug, args.max_depth, args.verbose)
    except Exception as e:
        console = Console()
        console.print(f"[bold red]Error:[/bold red] {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())