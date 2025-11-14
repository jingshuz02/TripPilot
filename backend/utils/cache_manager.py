import time
from typing import Any, Optional


class CacheManager:
    """简单的缓存管理"""

    def __init__(self, ttl: int = 300):  # 默认5分钟
        self.cache = {}
        self.ttl = ttl

    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return data
            else:
                del self.cache[key]
        return None

    def set(self, key: str, value: Any):
        """设置缓存值"""
        self.cache[key] = (value, time.time())

    def clear(self):
        """清空缓存"""
        self.cache.clear()