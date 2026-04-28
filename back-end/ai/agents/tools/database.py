"""
数据库查询工具 - Agent工具定义
"""

from langchain_core.tools import tool
import pymysql
from django.conf import settings


@tool
def get_database_tool(sql: str) -> str:
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
        return f"数据库查询错误: {str(e)}"
    finally:
        if 'conn' in locals():
            conn.close()
