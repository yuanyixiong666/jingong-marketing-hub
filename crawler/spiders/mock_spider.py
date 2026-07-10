"""
Mock数据爬虫 - 模拟各平台数据
AI生成：用于开发和演示的模拟数据，真实场景中替换为实际爬虫
人工修改：添加了金宫味业业务场景相关的模拟数据
"""
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from crawler.spiders.base_spider import BaseSpider


class MockSpider(BaseSpider):
    """模拟爬虫 - 生成金宫味业相关的模拟数据"""

    platform = "mock"

    # 调味品相关模拟数据
    PRODUCT_NAMES = [
        "金宫香辣酱 280g", "金宫鸡精 100g", "金宫麻辣调料 45g",
        "海天酱油 500ml", "海天蚝油 680g", "千禾零添加酱油 500ml",
        "李锦记蚝油 510g", "厨邦酱油 500ml",
    ]

    REVIEW_TEMPLATES = [
        "味道不错，做菜放一点很提味，{positive}",
        "一般般吧，性价比还行，{neutral}",
        "太难吃了，味道很奇怪，{negative}",
        "回购好多次了，家人都喜欢吃，{positive}",
        "包装破损，但味道还可以，{neutral}",
    ]

    async def crawl(self) -> List[Dict[str, Any]]:
        """生成模拟数据"""
        data = []
        platforms = ["douyin", "xiaohongshu", "tmall", "jd"]

        for _ in range(20):
            platform = random.choice(platforms)
            product = random.choice(self.PRODUCT_NAMES)
            now = datetime.now() - timedelta(hours=random.randint(0, 72))

            record = {
                "platform": platform,
                "content_type": random.choice(["product", "review", "post"]),
                "title": product,
                "content": random.choice(self.REVIEW_TEMPLATES).format(
                    positive="推荐购买！",
                    neutral="习惯性好评。",
                    negative="不会再买了。",
                ),
                "price": round(random.uniform(5.9, 89.9), 2),
                "sales_volume": random.randint(10, 50000),
                "likes": random.randint(0, 10000),
                "comments_count": random.randint(0, 2000),
                "shares": random.randint(0, 500),
                "raw_url": f"https://{platform}.com/mock/{random.randint(1000, 9999)}",
                "crawled_at": now.isoformat(),
            }
            data.append(record)

        return data


class MockHotListSpider(BaseSpider):
    """模拟抖音热榜爬虫"""

    platform = "douyin"

    async def crawl(self) -> List[Dict[str, Any]]:
        hot_items = [
            {"title": "零添加酱油真的健康吗？", "likes": 52000, "comments_count": 3200},
            {"title": "火锅底料横评，哪个最香？", "likes": 38000, "comments_count": 2100},
            {"title": "厨房调料收纳神器", "likes": 21000, "comments_count": 800},
            {"title": "家常菜30分钟搞定", "likes": 67000, "comments_count": 5400},
            {"title": "调味品工厂探秘", "likes": 45000, "comments_count": 1900},
        ]
        data = []
        for item in hot_items:
            data.append({
                "platform": "douyin",
                "content_type": "hot_list",
                "title": item["title"],
                "likes": item["likes"],
                "comments_count": item["comments_count"],
                "crawled_at": datetime.now().isoformat(),
            })
        return data
