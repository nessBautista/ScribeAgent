from mcp.server.fastmcp import FastMCP
import os
import logging
from dotenv import load_dotenv
from typing import List, Optional, Dict, Any
from scribeagent.utils.notion_formatters import NotionBlockFormatter


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scribeagent.mcp")

# Initialize the MCP server
mcp = FastMCP("ScribeAgent")

# Load environment variables
load_dotenv()

# Set up required services
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
if NOTION_API_KEY is None:
    raise RuntimeError("NOTION_API_KEY not set. Please configure your environment.")

# Create Notion service instance
from scribeagent.infrastructure.factory import create_notion_page_service
from scribeagent.domain.notion.entities import TextBlock, CodeBlock

notion_service = create_notion_page_service(NOTION_API_KEY)

@mcp.tool()
def hello_scribe(name: str) -> str:
    """Send a greeting to the user."""
    logger.info("ScribeAgent received hello request")
    return f"Hello {name}, welcome to ScribeAgent! what you want to write?"

@mcp.tool()
def get_notion_page(page_url: str) -> Dict[str, Any]:
    """Fetch a Notion page and its content based on the provided URL."""
    logger.info(f"Fetching Notion page: {page_url}")
    try:
        page, content = notion_service.get_page_with_content(page_url)
                
        # Format all blocks
        formatted_content = [NotionBlockFormatter.format_as_dict(block) for block in content]
        
        return {
            "title": page.get_title(),
            "url": page.url,
            "created_time": page.created_time.isoformat(),
            "last_edited_time": page.last_edited_time.isoformat(),
            "content": formatted_content
        }
    except Exception as e:
        logger.error(f"Error fetching Notion page: {e}")
        return {"error": f"Could not fetch page - {str(e)}"}

@mcp.tool()
def search_notion_blocks(page_url: str, query: str) -> List[Dict[str, Any]]:
    """Search for specific blocks within a Notion page that match the query."""
    logger.info(f"Searching in page {page_url} for: {query}")
    try:
        page, content = notion_service.get_page_with_content(page_url)
        matching_blocks = []
        
        def search_block(block) -> None:
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
        for block in content:
            search_block(block)
        
        return matching_blocks
    except Exception as e:
        logger.error(f"Error searching Notion page: {e}")
        return [{"error": f"Could not search page - {str(e)}"}]

def main():
    mcp.run()

if __name__ == "__main__":
    main()
