"""
随机数工具 - 生成唯一随机数
"""

import random
import json
from pathlib import Path
from typing import Set


class RandomGenerator:
    """随机数生成器 - 确保生成的数字唯一"""

    def __init__(self, file_path: str = 'generated_numbers.json'):
        self.file_path = Path(file_path)

    def load_generated_numbers(self) -> Set[int]:
        """加载已生成的数字集合"""
        if self.file_path.exists():
            with open(self.file_path, 'r') as f:
                return set(json.load(f))
        return set()

    def save_generated_numbers(self, numbers: Set[int]) -> None:
        """保存已生成的数字集合"""
        with open(self.file_path, 'w') as f:
            json.dump(list(numbers), f)

    def generate_unique_random(self, min_num: int, max_num: int) -> int:
        """生成指定范围内的唯一随机数"""
        generated = self.load_generated_numbers()
        available = set(range(min_num, max_num + 1)) - generated
        if not available:
            raise ValueError("所有可能的数字都已经生成过了。")
        number = random.choice(list(available))
        generated.add(number)
        self.save_generated_numbers(generated)
        return number


def generate_unique_random(min_num: int, max_num: int) -> int:
    """便捷函数：生成唯一随机数"""
    generator = RandomGenerator()
    return generator.generate_unique_random(min_num, max_num)
