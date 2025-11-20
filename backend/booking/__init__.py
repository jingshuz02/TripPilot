"""
Booking模块 - 预订服务层
处理航班和酒店的搜索、查询等预订相关功能

"""
from .amadeus_service import AmadeusService

__all__ = ['AmadeusService']
__version__ = '1.0.0'