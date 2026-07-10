"""
舆情数据API路由
AI生成：舆情查询与统计接口
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.sentiment import SentimentData
from app.schemas.common import ResponseModel
from app.schemas.sentiment import SentimentOut

router = APIRouter(prefix="/api/sentiment", tags=["舆情监控"])


@router.get("", response_model=ResponseModel)
async def list_sentiment(
    keyword: str = Query(None, description="关键词筛选"),
    sentiment: str = Query(None, description="情感筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """获取舆情数据列表"""
    query = select(SentimentData)
    if keyword:
        query = query.where(SentimentData.keyword.contains(keyword))
    if sentiment:
        query = query.where(SentimentData.sentiment == sentiment)
    query = query.order_by(SentimentData.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()
    items_out = [SentimentOut.model_validate(i) for i in items]
    return ResponseModel(data=items_out)


@router.get("/stats", response_model=ResponseModel)
async def get_sentiment_stats(db: AsyncSession = Depends(get_db)):
    """获取舆情统计概览"""
    # 按关键词统计
    keyword_query = (
        select(
            SentimentData.keyword,
            func.count(SentimentData.id).label("total"),
            func.sum(func.if_(SentimentData.sentiment == "positive", 1, 0)).label("positive"),
            func.sum(func.if_(SentimentData.sentiment == "negative", 1, 0)).label("negative"),
            func.sum(func.if_(SentimentData.sentiment == "neutral", 1, 0)).label("neutral"),
        )
        .group_by(SentimentData.keyword)
    )
    result = await db.execute(keyword_query)
    rows = result.all()
    stats = [
        {
            "keyword": r.keyword,
            "total": r.total,
            "positive": r.positive or 0,
            "negative": r.negative or 0,
            "neutral": r.neutral or 0,
        }
        for r in rows
    ]

    # 总体情感分布
    dist_query = select(SentimentData.sentiment, func.count(SentimentData.id)).group_by(SentimentData.sentiment)
    dist_result = await db.execute(dist_query)
    distribution = {r[0]: r[1] for r in dist_result.all()}

    return ResponseModel(data={"by_keyword": stats, "distribution": distribution})
