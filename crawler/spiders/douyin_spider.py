"""
抖音爬虫 - 热榜和搜索结果
AI生成：抖音公开数据爬取框架
人工修改：实现了真实请求框架 + 自动降级到模拟数据

爬取策略：
1. 优先尝试请求抖音公开热榜API
2. 如果请求失败（反爬/网络问题），自动降级到模拟数据
3. 解析返回数据并标准化为统一格式
"""
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from crawler.spiders.base_spider import BaseSpider
from crawler.config import PLATFORM_CONFIG


class DouyinSpider(BaseSpider):
    """抖音热榜/搜索爬虫"""

    platform = "douyin"

    # 模拟热榜数据（降级时使用）
    MOCK_HOT_ITEMS = [
        {"title": "零添加酱油真的健康吗？专家解读", "likes": 52000, "comments_count": 3200},
        {"title": "火锅底料横评，哪个最香？", "likes": 38000, "comments_count": 2100},
        {"title": "厨房调料收纳神器推荐", "likes": 21000, "comments_count": 800},
        {"title": "家常菜30分钟搞定，上班族必备", "likes": 67000, "comments_count": 5400},
        {"title": "调味品工厂探秘：一瓶酱油的诞生", "likes": 45000, "comments_count": 1900},
        {"title": "金宫味业新品上市，香辣酱测评", "likes": 33000, "comments_count": 1500},
        {"title": "川菜灵魂调料大盘点", "likes": 28000, "comments_count": 1200},
        {"title": "鸡精和味精到底有什么区别？", "likes": 41000, "comments_count": 2800},
    ]

    async def crawl(self) -> List[Dict[str, Any]]:
        """
        爬取抖音热榜数据
        策略：先尝试真实API，失败则降级到模拟数据
        """
        config = PLATFORM_CONFIG["douyin"]

        # 尝试真实爬取
        try:
            response = await self.fetch(
                config["hot_list_url"],
                headers={
                    "Referer": "https://www.douyin.com/",
                    "Accept": "application/json",
                },
            )
            if response.status_code == 200:
                raw_data = response.json()
                parsed = self._parse(raw_data)
                if parsed:
                    print(f"[抖音爬虫] 真实爬取成功，获取 {len(parsed)} 条数据")
                    return parsed
                print("[抖音爬虫] 真实API返回数据为空，降级到模拟数据")
            else:
                print(f"[抖音爬虫] 真实API返回状态码 {response.status_code}，降级到模拟数据")
        except Exception as e:
            print(f"[抖音爬虫] 真实爬取失败: {e}，降级到模拟数据")

        # 降级：返回模拟数据
        return self._generate_mock_data()

    def _parse(self, raw_data: dict) -> List[Dict[str, Any]]:
        """
        解析抖音接口返回数据
        抖音热榜API返回格式（参考）：
        {
            "data": {
                "word_list": [
                    {"word": "关键词", "hot_value": 12345, "video_count": 100},
                    ...
                ]
            }
        }
        """
        results = []
        try:
            word_list = raw_data.get("data", {}).get("word_list", [])
            now = datetime.now()

            for item in word_list[:10]:  # 最多取10条
                hot_value = item.get("hot_value", 0)
                results.append({
                    "platform": "douyin",
                    "content_type": "hot_list",
                    "title": item.get("word", ""),
                    "content": f"抖音热搜：{item.get('word', '')}",
                    "price": None,
                    "sales_volume": None,
                    "likes": int(hot_value * 0.3),  # 估算点赞数
                    "comments_count": int(hot_value * 0.05),  # 估算评论数
                    "shares": int(hot_value * 0.02),  # 估算分享数
                    "raw_url": f"https://www.douyin.com/hot/{item.get('sentence_id', '')}",
                    "crawled_at": now.isoformat(),
                })
        except (KeyError, TypeError) as e:
            print(f"[抖音爬虫] 数据解析异常: {e}")
            return []

        return results

    def _generate_mock_data(self) -> List[Dict[str, Any]]:
        """生成模拟抖音数据（降级方案）"""
        data = []
        now = datetime.now()

        for item in self.MOCK_HOT_ITEMS:
            crawl_time = now - timedelta(minutes=random.randint(0, 120))
            data.append({
                "platform": "douyin",
                "content_type": "hot_list",
                "title": item["title"],
                "content": f"抖音热搜：{item['title']}",
                "price": None,
                "sales_volume": None,
                "likes": item["likes"] + random.randint(-2000, 2000),
                "comments_count": item["comments_count"] + random.randint(-100, 100),
                "shares": random.randint(100, 3000),
                "raw_url": f"https://www.douyin.com/hot/mock/{random.randint(1000, 9999)}",
                "crawled_at": crawl_time.isoformat(),
            })

        return data
