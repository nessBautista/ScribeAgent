from mcp.server.fastmcp import FastMCP
import os
import logging
from dotenv import load_dotenv
from typing import List, Optional, Dict, Any

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
        
        # Format the response
        formatted_content = []
        for block in content:
            if isinstance(block, CodeBlock):
                formatted_block = {
                    "type": block.block_type.value,
                    "language": block.language,
                    "content": block.get_plain_text(),
                }
                if block.caption:
                    formatted_block["caption"] = ''.join(caption.plain_text for caption in block.caption)
                formatted_content.append(formatted_block)
            elif isinstance(block, TextBlock):
                formatted_content.append({
                    "type": block.block_type.value,
                    "content": block.get_plain_text()
                })
            else:
                formatted_content.append({
                    "type": block.block_type.value
                })
        
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
        
        query = query.lower()
        for block in content:
            if isinstance(block, (TextBlock, CodeBlock)):
                block_text = block.get_plain_text().lower()
                if query in block_text:
                    block_info = {
                        "type": block.block_type.value,
                        "content": block.get_plain_text()
                    }
                    if isinstance(block, CodeBlock):
                        block_info["language"] = block.language
                    matching_blocks.append(block_info)
        
        return matching_blocks
    except Exception as e:
        logger.error(f"Error searching Notion page: {e}")
        return [{"error": f"Could not search page - {str(e)}"}]

def main():
    mcp.run()

if __name__ == "__main__":
    main()
