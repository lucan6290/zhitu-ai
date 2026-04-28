import asyncio
from langchain_mcp_adapters.client import MCPClient
from langchain_mcp_adapters.tools import get_mcp_tools


async def test_mcp_jobs():
    print("正在连接 mcp-jobs 服务...")

    # 创建 MCP 客户端
    client = MCPClient(
        command="npx",
        args=["-y", "mcp-jobs"]
    )

    await client.connect()
    print("✅ 服务连接成功！")

    try:
        # 获取工具列表
        tools = await get_mcp_tools(client)
        print(f"✅ 可用工具: {[tool.name for tool in tools]}")

        # 这里可以进一步调用具体工具测试
        # 例如：search_jobs 工具

    finally:
        await client.close()
        print("✅ 测试完成，连接已关闭")


if __name__ == "__main__":
    asyncio.run(test_mcp_jobs())