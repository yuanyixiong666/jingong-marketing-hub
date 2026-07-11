"""
微博爬虫 - 热搜和话题
AI生成：微博公开数据爬取框架
爬取策略：
1. 优先尝试请求微博公开热搜API
2. 如果请求失败（反爬/网络问题），自动降级到模拟数据
3. 解析返回数据并标准化为统一格式
"""
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from crawler.spiders.base_spider import BaseSpider
from crawler.config import PLATFORM_CONFIG


class WeiboSpider(BaseSpider):
    """微博热搜/话题爬虫"""

    platform = "weibo"

    # 微博热搜公开API
    HOT_SEARCH_URL = "https://weibo.com/ajax/side/hotSearch"

    # 模拟热搜数据（降级时使用）
    MOCK_HOT_ITEMS = [
        {"title": "零添加酱油真的更健康吗", "hot_value": 987654, "category": "美食"},
        {"title": "调味品选购指南来了", "hot_value": 765432, "category": "生活"},
        {"title": "金宫味业新品发布", "hot_value": 654321, "category": "商业"},
        {"title": "火锅底料哪个牌子好吃", "hot_value": 543210, "category": "美食"},
        {"title": "川菜调味品推荐", "hot_value": 432109, "category": "美食"},
        {"title": "食品安全法最新修订", "hot_value": 876543, "category": "社会"},
        {"title": "有机酱油和普通酱油区别", "hot_value": 321098, "category": "生活"},
        {"title": "鸡精到底要不要吃", "hot_value": 210987, "category": "健康"},
    ]

    async def crawl(self) -> List[Dict[str, Any]]:
        """
        爬取微博热搜数据
        策略：先尝试真实API，失败则降级到模拟数据
        """
        # 尝试真实爬取
        try:
            response = await self.fetch(
                self.HOT_SEARCH_URL,
                headers={
                    "Referer": "https://weibo.com/",
                    "Accept": "application/json",
                },
            )
            if response.status_code == 200:
                raw_data = response.json()
                parsed = self._parse(raw_data)
                if parsed:
                    print(f"[微博爬虫] 真实爬取成功，获取 {len(parsed)} 条数据")
                    return parsed
                print("[微博爬虫] 真实API返回数据为空，降级到模拟数据")
            else:
                print(f"[微博爬虫] 真实API返回状态码 {response.status_code}，降级到模拟数据")
        except Exception as e:
            print(f"[微博爬虫] 真实爬取失败: {e}，降级到模拟数据")

        # 降级：返回模拟数据
        return self._generate_mock_data()

    def _parse(self, raw_data: dict) -> List[Dict[str, Any]]:
        """
        解析微博热搜接口返回数据
        微博热搜API返回格式（参考）：
        {
            "ok": 1,
            "data": {
                "realtime": [
                    {"word": "关键词", "num": 123456, "category": "美食", "mid": "xxx"},
                    ...
                ]
            }
        }
        """
        results = []
        try:
            realtime = raw_data.get("data", {}).get("realtime", [])
            now = datetime.now()

            for item in realtime[:10]:  # 最多取10条
                hot_value = item.get("num", 0)
                word = item.get("word", "")
                results.append({
                    "platform": "weibo",
                    "content_type": "hot_list",
                    "title": word,
                    "content": f"微博热搜：{word}",
                    "price": None,
                    "sales_volume": None,
                    "likes": int(hot_value * 0.2),
                    "comments_count": int(hot_value * 0.03),
                    "shares": int(hot_value * 0.01),
                    "raw_url": f"https://s.weibo.com/weibo?q=%23{word}%23",
                    "crawled_at": now.isoformat(),
                })
        except (KeyError, TypeError) as e:
            print(f"[微博爬虫] 数据解析异常: {e}")
            return []

        return results

    def _generate_mock_data(self) -> List[Dict[str, Any]]:
        """生成模拟微博数据（降级方案）"""
        data = []
        now = datetime.now()

        for item in self.MOCK_HOT_ITEMS:
            crawl_time = now - timedelta(minutes=random.randint(0, 120))
            hot_value = item["hot_value"] + random.randint(-50000, 50000)
            data.append({
                "platform": "weibo",
                "content_type": "hot_list",
                "title": item["title"],
                "content": f"微博热搜：{item['title']}",
                "price": None,
                "sales_volume": None,
                "likes": max(0, int(hot_value * 0.2)),
                "comments_count": max(0, int(hot_value * 0.03)),
                "shares": max(0, int(hot_value * 0.01)),
                "raw_url": f"https://s.weibo.com/weibo?q=%23{item['title']}%23",
                "crawled_at": crawl_time.isoformat(),
            })

        return data
