"""
竞品监控API路由
AI生成：竞品管理 + 价格追踪接口
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.competitor import Competitor, CompetitorPrice
from app.schemas.common import ResponseModel
from app.schemas.competitor import CompetitorCreate, CompetitorOut

router = APIRouter(prefix="/api/competitors", tags=["竞品监控"])


@router.post("", response_model=ResponseModel)
async def add_competitor(data: CompetitorCreate, db: AsyncSession = Depends(get_db)):
    """添加竞品品牌"""
    record = Competitor(**data.model_dump())
    db.add(record)
    await db.flush()
    return ResponseModel(data={"id": record.id}, message="添加成功")


@router.get("", response_model=ResponseModel[list[CompetitorOut]])
async def list_competitors(db: AsyncSession = Depends(get_db)):
    """获取竞品列表"""
    result = await db.execute(select(Competitor).where(Competitor.is_active == 1))
    items = result.scalars().all()
    return ResponseModel(data=items)


@router.get("/{competitor_id}/prices", response_model=ResponseModel)
async def get_prices(competitor_id: int, db: AsyncSession = Depends(get_db)):
    """获取竞品价格记录"""
    result = await db.execute(
        select(CompetitorPrice)
        .where(CompetitorPrice.competitor_id == competitor_id)
        .order_by(CompetitorPrice.crawled_at.desc())
        .limit(50)
    )
    items = result.scalars().all()
    return ResponseModel(data=items)
