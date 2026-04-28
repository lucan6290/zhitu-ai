"""
MCP客户端 - 连接外部MCP工具服务器
"""

from langchain_mcp_adapters.client import MultiServerMCPClient
from django.conf import settings

# MCP客户端实例 - 连接到配置的MCP服务器
mcp_client = MultiServerMCPClient({
    "my_mcp_server": {
        "url": settings.MCP_SERVER_URL,
        "transport": "http"
    }
})
