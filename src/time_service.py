from fastmcp import FastMCP
from datetime import datetime

# Create an MCP server
mcp = FastMCP("TimeService")

@mcp.tool()
def get_current_time() -> str:
    """Returns the current system time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if __name__ == "__main__":
    mcp.run()
