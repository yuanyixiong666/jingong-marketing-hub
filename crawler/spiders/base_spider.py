"""
爬虫基类
AI生成：统一的爬虫接口，各平台spider继承此类
"""
import httpx
import asyncio
from datetime import datetime
from typing import List, Dict, Any
from crawler.config import USER_AGENTS
import random


class BaseSpider:
    """爬虫基类 - 所有平台爬虫继承此类"""

    platform: str = ""

    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
        )

    def _get_headers(self) -> dict:
        """随机选择User-Agent"""
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "application/json, text/plain, */*",
        }

    async def fetch(self, url: str, **kwargs) -> httpx.Response:
        """发送HTTP请求"""
        headers = self._get_headers()
        headers.update(kwargs.pop("headers", {}))
        return await self.client.get(url, headers=headers, **kwargs)

    async def crawl(self) -> List[Dict[str, Any]]:
        """
        核心爬取方法 - 子类必须实现
        返回数据列表，每条记录包含: title, content, price, likes等
        """
        raise NotImplementedError

    async def close(self):
        await self.client.aclose()
