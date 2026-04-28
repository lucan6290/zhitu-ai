"""
MCP服务器 - 提供工具服务
可被其他Agent调用
"""

from fastmcp import FastMCP
import requests
import pymysql
from django.conf import settings

# 创建MCP服务器实例
mcp_server = FastMCP(
    name="Face Recognition MCP Server",
    instructions="人脸识别智能系统的MCP工具服务"
)


@mcp_server.tool
def get_age(name: str) -> str:
    """工具：根据姓名查询年龄（模拟数据）"""
    data = [
        {"name": "张三", "age": 23},
        {"name": "李四", "age": 24},
        {"name": "王五", "age": 25},
        {"name": "赵六", "age": 26}
    ]
    for item in data:
        if name == item["name"]:
            return f"用户姓名是{name}，年龄是{item['age']}"
    return "没有该用户"


@mcp_server.tool
def get_weather(city: str) -> str:
    """工具：根据城市名称查询天气"""
    url = f"https://api.seniverse.com/v3/weather/now.json?key=SQODkj_zcH9MQkxju&location={city}&language=zh-Hans&unit=c"
    res = requests.get(url)
    return str(res.json())


@mcp_server.tool
def get_database(sql: str) -> str:
    """工具：根据SQL语句查询数据库"""
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
        return str(result)
    except Exception as e:
        return str(e)


if __name__ == "__main__":
    # 启动MCP服务器
    mcp_server.run(transport="streamable-http", port=8081)
