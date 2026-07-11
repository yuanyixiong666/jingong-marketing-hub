"""
AI情感分析服务
统一使用 backend/app/services/llm_service.py 中的LLM服务
本模块保留类接口，内部委托给统一的 llm_service
"""
from typing import List, Dict, Any
from app.services.llm_service import analyze_sentiment as _analyze_sentiment


class SentimentAnalyzer:
    """AI情感分析器 - 委托给统一LLM服务"""

    def __init__(self):
        pass

    async def analyze(self, content: str, platform: str = "", keyword: str = "") -> Dict[str, Any]:
        """分析单条内容的情感 - 委托给 llm_service"""
        result = await _analyze_sentiment(content, keyword)
        # 适配旧接口返回格式
        return {
            "sentiment_label": result.get("sentiment", "neutral"),
            "sentiment_score": result.get("score", 0.5),
            "content_tag": "其他",
            "summary": result.get("summary", ""),
        }

    async def analyze_batch(self, items: List[Dict]) -> List[Dict]:
        """批量分析"""
        results = []
        for item in items:
            result = await self.analyze(
                content=item.get("content", ""),
                platform=item.get("platform", ""),
                keyword=item.get("keyword", ""),
            )
            results.append({**item, **result})
        return results

    async def close(self):
        pass
