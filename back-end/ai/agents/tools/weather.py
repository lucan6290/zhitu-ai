"""
天气查询工具 - Agent工具定义
"""

from langchain_core.tools import tool
import requests


@tool
def get_weather_tool(city: str) -> str:
    """工具：根据城市名称查询天气信息"""
    url = f"https://api.seniverse.com/v3/weather/now.json?key=SQODkj_zcH9MQkxju&location={city}&language=zh-Hans&unit=c"
    try:
        res = requests.get(url, timeout=10)
        return str(res.json())
    except Exception as e:
        return f"天气查询失败: {str(e)}"
