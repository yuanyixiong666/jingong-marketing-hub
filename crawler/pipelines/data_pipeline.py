"""
数据管道 - 爬取数据清洗后写入数据库
AI生成：连接后端API，将爬取数据通过HTTP接口写入
"""
import httpx
from typing import List, Dict, Any
from datetime import datetime


class DataPipeline:
    """将爬取的数据通过API写入后端"""

    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.client = httpx.AsyncClient(base_url=api_base_url, timeout=10.0)

    async def save_batch(self, data_list: List[Dict[str, Any]]) -> dict:
        """批量保存数据到后端"""
        success = 0
        failed = 0
        for item in data_list:
            try:
                resp = await self.client.post("/api/platform-data", json=item)
                if resp.status_code == 200:
                    success += 1
                else:
                    failed += 1
            except Exception as e:
                failed += 1
                print(f"保存失败: {e}")

        return {"success": success, "failed": failed, "total": len(data_list)}

    async def close(self):
        await self.client.aclose()
