"""
智能报告API路由
AI生成：使用LLM（通义千问）生成数据分析报告
人工修改：添加了金宫味业业务场景的prompt模板
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.platform_data import PlatformData
from app.models.sentiment import SentimentData
from app.models.competitor import Competitor, CompetitorPrice
from app.schemas.common import ResponseModel
from app.services.llm_service import generate_report_content, analyze_sentiment

router = APIRouter(prefix="/api/report", tags=["智能报告"])


@router.post("/generate", response_model=ResponseModel)
async def generate_report(data: dict, db: AsyncSession = Depends(get_db)):
    """AI生成数据分析报告（调用通义千问LLM）"""
    report_type = data.get("type", "daily")

    # ========== 1. 收集数据摘要 ==========
    total_data = (await db.execute(select(func.count(PlatformData.id)))).scalar() or 0

    platform_stats = (await db.execute(
        select(PlatformData.platform, func.count(PlatformData.id), func.sum(PlatformData.likes))
        .group_by(PlatformData.platform)
    )).all()

    sentiment_stats = (await db.execute(
        select(SentimentData.sentiment, func.count(SentimentData.id))
        .group_by(SentimentData.sentiment)
    )).all()

    # 关键词维度舆情详情
    keyword_stats = (await db.execute(
        select(SentimentData.keyword, SentimentData.sentiment, func.count(SentimentData.id))
        .group_by(SentimentData.keyword, SentimentData.sentiment)
    )).all()

    competitors = (await db.execute(
        select(Competitor).where(Competitor.is_active == 1)
    )).scalars().all()

    # 互动总量
    engagement = (await db.execute(
        select(
            func.sum(PlatformData.likes),
            func.sum(PlatformData.comments_count),
            func.sum(PlatformData.shares),
        )
    )).one()

    # 竞品价格区间
    price_range = (await db.execute(
        select(func.min(CompetitorPrice.price), func.max(CompetitorPrice.price))
    )).one()

    # ========== 2. 构建数据上下文 ==========
    platform_lines = "\n".join([
        f"  - {r[0]}: {r[1]} 条数据, {r[2] or 0} 次点赞"
        for r in platform_stats
    ]) if platform_stats else "  暂无数据"

    sentiment_lines = "\n".join([
        f"  - {r[0]}: {r[1]} 条"
        for r in sentiment_stats
    ]) if sentiment_stats else "  暂无舆情数据"

    # 按关键词聚合舆情
    keyword_map = {}
    for kw, sent, cnt in keyword_stats:
        keyword_map.setdefault(kw, {})[sent] = cnt
    keyword_details = "\n".join([
        f"  - {kw}: " + ", ".join([f"{s}={c}" for s, c in details.items()])
        for kw, details in keyword_map.items()
    ]) if keyword_map else "  暂无详细数据"

    comp_list = ", ".join([c.brand_name for c in competitors]) if competitors else "暂无竞品"

    price_str = f"{price_range[0]:.1f} - {price_range[1]:.1f} 元" if price_range[0] else "暂无价格数据"

    data_context = {
        "total_data": total_data,
        "platform_lines": platform_lines,
        "sentiment_lines": sentiment_lines,
        "keyword_details": keyword_details,
        "comp_list": comp_list,
        "price_range": price_str,
        "total_likes": engagement[0] or 0,
        "total_comments": engagement[1] or 0,
        "total_shares": engagement[2] or 0,
    }

    # ========== 3. 调用LLM生成报告 ==========
    report_content = await generate_report_content(report_type, data_context)

    period_name = "日报" if report_type == "daily" else "周报"
    return ResponseModel(data=report_content, message=f"AI智能{period_name}生成成功")


@router.post("/analyze-sentiment", response_model=ResponseModel)
async def analyze_text_sentiment(data: dict):
    """AI分析文本情感（调用通义千问LLM）"""
    text = data.get("text", "")
    keyword = data.get("keyword", "")

    if not text:
        return ResponseModel(data=None, message="请输入待分析的文本内容", code=400)

    result = await analyze_sentiment(text, keyword)
    return ResponseModel(data=result, message="情感分析完成")
