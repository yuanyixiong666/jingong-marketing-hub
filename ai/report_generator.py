"""
AI智能报告生成器
AI生成：使用LLM根据数据自动生成日报/周报
人工修改：添加了调味品行业特定的报告模板
"""
import httpx
from typing import Dict, Any
from app.config import settings


REPORT_PROMPT = """你是金宫味业的市场数据分析师。请根据以下数据摘要，生成一份简洁的{report_type}。

数据摘要：
- 各平台数据总量: {total_records}条
- 平台分布: {platform_stats}
- 竞品动态: {competitor_summary}
- 舆情概况: {sentiment_summary}

报告要求：
1. 核心发现（3-5条关键洞察）
2. 竞品动态分析
3. 风险预警（如有）
4. 行动建议（具体可执行的2-3条）

请用专业但易读的语言，控制在500字以内。"""


class ReportGenerator:
    """AI报告生成器"""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=60.0)
        self.api_url = settings.OPENAI_BASE_URL + "/chat/completions"

    async def generate(
        self,
        report_type: str = "日报",
        total_records: int = 0,
        platform_stats: str = "",
        competitor_summary: str = "",
        sentiment_summary: str = "",
    ) -> str:
        """生成分析报告"""
        prompt = REPORT_PROMPT.format(
            report_type=report_type,
            total_records=total_records,
            platform_stats=platform_stats,
            competitor_summary=competitor_summary,
            sentiment_summary=sentiment_summary,
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
                    "temperature": 0.7,
                    "max_tokens": 1000,
                },
            )
            result = resp.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            return f"报告生成失败: {e}"

    async def close(self):
        await self.client.aclose()
