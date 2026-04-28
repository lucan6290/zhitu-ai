"""
数据库查询工具模块
==================

本模块提供Agent可调用的数据库查询工具。
通过LangChain的@tool装饰器将数据库查询功能封装为工具，
供AI Agent在对话中动态调用。

主要功能：
- 执行SQL查询并返回结果
- 自动管理数据库连接的创建和关闭
- 提供错误处理和异常捕获

使用示例：
    from ai.agents.tools.database import get_database_tool
    
    # 作为LangChain工具使用
    result = get_database_tool.invoke("SELECT * FROM users LIMIT 10")

依赖说明：
- langchain_core.tools: LangChain工具装饰器
- pymysql: MySQL数据库驱动
- django.conf.settings: Django配置读取
"""

from langchain_core.tools import tool
import pymysql
from django.conf import settings


@tool
def get_database_tool(sql: str) -> str:
    """
    数据库查询工具（LangChain Tool）
    
    执行SQL查询语句并返回结果。该工具会自动管理数据库连接，
    确保连接在使用后正确关闭。
    
    Args:
        sql: SQL查询语句字符串
            - 支持任意SELECT查询
            - 建议添加LIMIT限制返回数据量
    
    Returns:
        str: 查询结果的字符串表示
            - 成功时返回元组列表的字符串形式
            - 失败时返回错误信息字符串
    
    Raises:
        不会抛出异常，所有异常都会被捕获并转换为错误消息返回
    
    Example:
        >>> result = get_database_tool.invoke("SELECT name FROM users WHERE id = 1")
        >>> print(result)
        "(('张三',),)"
    
    Note:
        - 数据库配置从Django settings.DATABASE_CONFIG读取
        - 使用pymysql作为MySQL驱动
        - 连接字符集为utf8
        - 建议在SQL中添加LIMIT避免返回过多数据
    
    Performance:
        - 每次调用都会创建新连接，适合低频查询场景
        - 高频查询场景建议使用连接池优化
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
        return str(result)
    except Exception as e:
        return f"数据库查询错误: {str(e)}"
    finally:
        if 'conn' in locals():
            conn.close()
