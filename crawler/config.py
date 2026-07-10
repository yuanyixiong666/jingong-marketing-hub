"""
爬虫配置
AI生成：各平台爬取配置、请求头、代理设置
"""

# 通用请求头池（轮换使用，降低被封风险）
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
]

# 各平台爬取配置
PLATFORM_CONFIG = {
    "douyin": {
        "base_url": "https://www.douyin.com",
        "hot_list_url": "https://www.douyin.com/aweme/v1/web/hot/search/list/",
        "interval_seconds": 3600,  # 1小时一次
    },
    "xiaohongshu": {
        "base_url": "https://www.xiaohongshu.com",
        "search_url": "https://www.xiaohongshu.com/web-login/search",
        "interval_seconds": 7200,  # 2小时一次
    },
    "tmall": {
        "base_url": "https://www.tmall.com",
        "interval_seconds": 14400,  # 4小时一次
    },
    "jd": {
        "base_url": "https://www.jd.com",
        "interval_seconds": 14400,
    },
}

# 竞品关键词（金宫味业主要竞品）
COMPETITOR_KEYWORDS = ["海天", "千禾", "李锦记", "厨邦", "欣和"]

# 舆情关键词
SENTIMENT_KEYWORDS = ["零添加", "有机酱油", "调味品推荐", "鸡精怎么选", "火锅底料测评"]
