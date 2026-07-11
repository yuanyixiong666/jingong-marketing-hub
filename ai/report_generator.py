"""
AI智能报告生成器
统一使用 backend/app/services/llm_service.py 中的LLM服务
本模块保留类接口，内部委托给统一的 llm_service
"""
from app.services.llm_service import generate_report_content


class ReportGenerator:
    """AI报告生成器 - 委托给统一LLM服务"""

    def __init__(self):
        pass

    async def generate(
        self,
        report_type: str = "日报",
        total_records: int = 0,
        platform_stats: str = "",
        competitor_summary: str = "",
        sentiment_summary: str = "",
    ) -> str:
        """生成分析报告 - 委托给 llm_service"""
        data_context = {
            "total_data": total_records,
            "platform_lines": platform_stats or "暂无数据",
            "sentiment_lines": sentiment_summary or "暂无舆情数据",
            "keyword_details": "",
            "comp_list": competitor_summary or "暂无竞品",
            "price_range": "",
            "total_likes": 0,
            "total_comments": 0,
            "total_shares": 0,
        }
        return await generate_report_content(report_type, data_context)

    async def close(self):
        pass
