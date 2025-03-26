from mcp.server.fastmcp import FastMCP

# Create an MCP server instance for ScribeAgent
mcp = FastMCP("ScribeAgent")

@mcp.tool()
def hello_scribe(name: str) -> str:
    """Send a greeting to the user."""
    print("ScribeAgent received hello request")
    return f"Hello {name}, welcome to ScribeAgent! what you want to write?"

def main():
    mcp.run()

if __name__ == "__main__":
    main()
