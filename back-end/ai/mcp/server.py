"""
MCP服务器模块
=============

本模块定义本地MCP (Model Context Protocol) 服务器，
提供数据库查询等本地工具供AI Agent调用。

主要功能：
- 创建FastMCP服务器实例
- 注册数据库查询工具
- 支持作为独立MCP服务器运行

工具列表：
- query_database: 执行SQL查询，返回数据库结果

使用示例：
    # 作为模块导入使用
    from ai.mcp.server import query_database
    result = query_database("SELECT * FROM users LIMIT 10")
    
    # 作为独立MCP服务器运行
    python -m ai.mcp.server

依赖说明：
- mcp.server.fastmcp: FastMCP框架，简化MCP服务器开发
- pymysql: MySQL数据库驱动
- django.conf.settings: Django配置读取

架构说明：
- 招聘相关工具由外部MCP-Jobs服务提供（npx @zizaiwork/mcp）
- 本模块仅提供本地数据库查询工具
"""

import pymysql
from django.conf import settings
from mcp.server.fastmcp import FastMCP

mcp_server = FastMCP("face-pro-local-tools")


@mcp_server.tool()
def query_database(sql: str) -> str:
    """
    数据库查询工具（MCP Tool）
    
    执行SQL查询语句并返回结果。该工具注册到MCP服务器，
    可被支持MCP协议的AI模型调用。
    
    Args:
        sql: SQL查询语句字符串
            - 仅支持SELECT查询
            - 不支持INSERT、UPDATE、DELETE等修改操作
            - MySQL版本：8.0.37
    
    Returns:
        str: 查询结果的字符串表示
            - 成功时返回元组列表的字符串形式
            - 失败时返回错误信息字符串
    
    Example:
        >>> result = query_database("SELECT name, email FROM users WHERE id = 1")
        >>> print(result)
        "(('张三', 'zhangsan@example.com'),)"
    
    Security:
        - 该工具不进行SQL注入过滤，调用方需确保SQL语句安全
        - 建议在Agent层面添加SQL安全检查
    
    Note:
        - 每次调用创建新连接，适合低频查询
        - 数据库配置从Django settings.DATABASE_CONFIG读取
    """
    try:
        config = settings.DATABASE_CONFIG
        conn = pymysql.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database=config['name'],
            charset=config['charset']
        )
        cursor = conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        conn.close()
        return str(result)
    except Exception as e:
        return str(e)


if __name__ == "__main__":
    mcp_server.run()
