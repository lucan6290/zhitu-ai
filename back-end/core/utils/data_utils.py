"""
数据处理工具 - JSON文件读写操作
"""

import json
import os
from pathlib import Path
from typing import Optional, List, Any, Dict


class DataService:
    """数据服务 - JSON文件读写"""

    def __init__(self, filename: str = 'data.json'):
        self.filename = Path(filename)

    def save_json(self, new_data: Dict[str, Any]) -> None:
        """保存数据到JSON文件"""
        file_exists = self.filename.is_file()
        if file_exists:
            with open(self.filename, 'r', encoding='utf-8') as file:
                data = json.load(file)
        else:
            data = []
        data.append(new_data)
        with open(self.filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def read_json(self) -> Optional[List[Dict[str, Any]]]:
        """从JSON文件读取数据"""
        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"错误：文件 '{self.filename}' 不存在。")
            return None
        except json.JSONDecodeError:
            print(f"错误：文件 '{self.filename}' 不包含有效的 JSON 数据。")
            return None

    def get_data_name(self, num: int) -> Optional[str]:
        """根据编号获取名称"""
        data = self.read_json()
        if data:
            result = [user for user in data if user.get("num") == num]
            if result:
                return result[0].get("name")
        return None


def save_json(new_data: Dict[str, Any], filename: str = 'data.json') -> None:
    """便捷函数：保存JSON数据"""
    service = DataService(filename)
    service.save_json(new_data)


def read_json(filename: str = 'data.json') -> Optional[List[Dict[str, Any]]]:
    """便捷函数：读取JSON数据"""
    service = DataService(filename)
    return service.read_json()


def get_data_name(num: int, filename: str = 'data.json') -> Optional[str]:
    """便捷函数：根据编号获取名称"""
    service = DataService(filename)
    return service.get_data_name(num)
