"""
数据管道 - 爬取数据清洗后写入数据库
AI生成：连接后端API，将爬取数据通过HTTP接口写入
人工修改：使用统一配置地址，支持批量写入
"""
import httpx
from typing import List, Dict, Any
from datetime import datetime

# 统一从配置读取API地址，避免硬编码
try:
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from backend.app.config import settings
    DEFAULT_API_URL = settings.API_BASE_URL
except Exception:
    DEFAULT_API_URL = "http://localhost:8000"


class DataPipeline:
    """将爬取的数据通过API写入后端"""

    def __init__(self, api_base_url: str = None):
        url = api_base_url or DEFAULT_API_URL
        self.api_base_url = url
        self.client = httpx.AsyncClient(base_url=url, timeout=10.0)

    async def save_batch(self, data_list: List[Dict[str, Any]]) -> dict:
        """批量保存数据到后端（优先使用批量接口，失败则逐条写入）"""
        # 优先使用批量接口
        try:
            resp = await self.client.post("/api/platform-data/batch", json=data_list)
            if resp.status_code == 200:
                result = resp.json()
                count = result.get("data", {}).get("count", len(data_list))
                return {"success": count, "failed": 0, "total": len(data_list)}
        except Exception:
            pass

        # 降级：逐条写入
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
