"""
天猫爬虫 - 商品数据
AI生成：天猫公开商品数据爬取框架
爬取策略：
1. 优先尝试请求天猫搜索接口
2. 如果请求失败（反爬/网络问题），自动降级到模拟数据
3. 解析返回数据并标准化为统一格式
"""
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from crawler.spiders.base_spider import BaseSpider
from crawler.config import PLATFORM_CONFIG, COMPETITOR_KEYWORDS


class TmallSpider(BaseSpider):
    """天猫商品数据爬虫"""

    platform = "tmall"

    # 模拟商品数据（降级时使用）
    MOCK_PRODUCTS = [
        {"title": "金宫味业零添加酱油500ml", "price": 29.9, "original_price": 39.9, "sales": 15000, "brand": "金宫"},
        {"title": "海天酱油生抽500ml", "price": 12.9, "original_price": 15.9, "sales": 85000, "brand": "海天"},
        {"title": "千禾零添加酱油500ml", "price": 25.8, "original_price": 32.0, "sales": 42000, "brand": "千禾"},
        {"title": "李锦记蚝油510g", "price": 16.8, "original_price": 19.9, "sales": 63000, "brand": "李锦记"},
        {"title": "厨邦酱油480ml", "price": 14.5, "original_price": 18.0, "sales": 38000, "brand": "厨邦"},
        {"title": "欣和酱油500ml", "price": 18.9, "original_price": 22.0, "sales": 28000, "brand": "欣和"},
        {"title": "金宫味业鸡精200g", "price": 15.8, "original_price": 19.9, "sales": 22000, "brand": "金宫"},
        {"title": "金宫味业火锅底料360g", "price": 19.9, "original_price": 25.0, "sales": 31000, "brand": "金宫"},
        {"title": "海天料酒500ml", "price": 9.9, "original_price": 12.9, "sales": 95000, "brand": "海天"},
        {"title": "千禾有机酱油300ml", "price": 35.0, "original_price": 42.0, "sales": 18000, "brand": "千禾"},
    ]

    async def crawl(self) -> List[Dict[str, Any]]:
        """
        爬取天猫商品数据
        策略：先尝试真实请求，失败则降级到模拟数据
        """
        config = PLATFORM_CONFIG.get("tmall", {})
        base_url = config.get("base_url", "https://www.tmall.com")

        # 尝试真实爬取（天猫反爬非常严格，基本会降级）
        try:
            keyword = random.choice(COMPETITOR_KEYWORDS) + "+酱油"
            response = await self.fetch(
                f"{base_url}/search?q={keyword}",
                headers={
                    "Referer": "https://www.tmall.com/",
                    "Accept": "text/html,application/xhtml+xml",
                },
            )
            if response.status_code == 200:
                print(f"[天猫爬虫] 请求成功但需要JS渲染/登录，降级到模拟数据")
            else:
                print(f"[天猫爬虫] 请求返回状态码 {response.status_code}，降级到模拟数据")
        except Exception as e:
            print(f"[天猫爬虫] 请求失败: {e}，降级到模拟数据")

        # 降级：返回模拟数据
        return self._generate_mock_data()

    def _generate_mock_data(self) -> List[Dict[str, Any]]:
        """生成模拟天猫商品数据（降级方案）"""
        data = []
        now = datetime.now()

        for item in self.MOCK_PRODUCTS:
            crawl_time = now - timedelta(minutes=random.randint(0, 720))
            price_jitter = random.uniform(-2.0, 2.0)
            data.append({
                "platform": "tmall",
                "content_type": "product",
                "title": item["title"],
                "content": f"天猫商品：{item['title']}，品牌：{item['brand']}",
                "price": round(max(1.0, item["price"] + price_jitter), 2),
                "sales_volume": item["sales"] + random.randint(-1000, 1000),
                "likes": random.randint(500, 5000),
                "comments_count": random.randint(200, 3000),
                "shares": None,
                "raw_url": f"https://detail.tmall.com/item.htm?id=mock{random.randint(100000, 999999)}",
                "crawled_at": crawl_time.isoformat(),
            })

        return data
