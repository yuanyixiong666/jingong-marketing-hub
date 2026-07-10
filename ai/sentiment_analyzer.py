"""
AI情感分析服务
AI生成：使用LLM对抓取内容进行情感分析和标签分类
人工修改：优化了Prompt模板，添加了金宫味业业务上下文
"""
import httpx
from typing import List, Dict, Any
from app.config import settings


SENTIMENT_PROMPT = """你是一个调味品行业的舆情分析专家。请分析以下用户评论/内容，返回JSON格式结果。

分析要求：
1. sentiment_label: 情感倾向，只能是 positive/negative/neutral 之一
2. sentiment_score: 情感得分，范围 -1.0 到 1.0
3. content_tag: 内容标签，从以下选项中选择：测评/recipe/促销/讨论/投诉/其他
4. summary: 一句话总结（不超过30字）

待分析内容：
平台: {platform}
关键词: {keyword}
内容: {content}

请严格以JSON格式返回，不要包含其他文字：
{{"sentiment_label": "...", "sentiment_score": 0.0, "content_tag": "...", "summary": "..."}}"""


class SentimentAnalyzer:
    """AI情感分析器"""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.api_url = settings.OPENAI_BASE_URL + "/chat/completions"

    async def analyze(self, content: str, platform: str = "", keyword: str = "") -> Dict[str, Any]:
        """分析单条内容的情感"""
        prompt = SENTIMENT_PROMPT.format(
            platform=platform, keyword=keyword, content=content
        )
        try:
            resp = await self.client.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.LLM_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                },
            )
            result = resp.json()
            text = result["choices"][0]["message"]["content"]
            # 简单解析JSON（生产环境应使用更健壮的解析）
            import json
            return json.loads(text)
        except Exception as e:
            print(f"AI分析失败: {e}")
            return {
                "sentiment_label": "neutral",
                "sentiment_score": 0.0,
                "content_tag": "其他",
                "summary": "分析失败",
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
        await self.client.aclose()
