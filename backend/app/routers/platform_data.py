"""
平台数据API路由
AI生成：CRUD接口 + 数据查询
人工修改：集成 Redis 缓存层，提升查询性能
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.platform_data import PlatformData
from app.schemas.common import ResponseModel, PaginatedResponse
from app.schemas.platform_data import PlatformDataCreate, PlatformDataOut
from app.services.cache_service import RedisCache

router = APIRouter(prefix="/api/platform-data", tags=["平台数据"])


@router.post("", response_model=ResponseModel)
async def create_data(data: PlatformDataCreate, db: AsyncSession = Depends(get_db)):
    """新增平台数据（爬虫写入）"""
    record = PlatformData(**data.model_dump())
    db.add(record)
    await db.flush()
    return ResponseModel(data={"id": record.id}, message="创建成功")


@router.post("/batch", response_model=ResponseModel)
async def create_batch_data(data: list[PlatformDataCreate], db: AsyncSession = Depends(get_db)):
    """批量新增平台数据（爬虫批量写入）"""
    records = [PlatformData(**item.model_dump()) for item in data]
    db.add_all(records)
    await db.flush()
    return ResponseModel(data={"count": len(records)}, message=f"批量创建成功，共{len(records)}条")


@router.get("", response_model=PaginatedResponse[PlatformDataOut])
async def list_data(
    platform: str = Query(None, description="平台筛选"),
    content_type: str = Query(None, description="内容类型筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """分页查询平台数据"""
    query = select(PlatformData)
    count_query = select(func.count(PlatformData.id))

    if platform:
        query = query.where(PlatformData.platform == platform)
        count_query = count_query.where(PlatformData.platform == platform)
    if content_type:
        query = query.where(PlatformData.content_type == content_type)
        count_query = count_query.where(PlatformData.content_type == content_type)

    total = (await db.execute(count_query)).scalar() or 0
    query = query.order_by(PlatformData.crawled_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedResponse(data=items, total=total, page=page, page_size=page_size)


@router.get("/stats", response_model=ResponseModel)
async def get_stats(db: AsyncSession = Depends(get_db)):
    """获取各平台数据统计概览（带 Redis 缓存）"""
    cache_key = "platform_stats"

    # 尝试从 Redis 缓存读取
    cached = await RedisCache.get(cache_key)
    if cached is not None:
        return ResponseModel(data=cached, message="缓存命中")

    # 缓存未命中，查询数据库
    stats_query = (
        select(
            PlatformData.platform,
            func.count(PlatformData.id).label("total"),
            func.sum(PlatformData.likes).label("total_likes"),
            func.avg(PlatformData.price).label("avg_price"),
        )
        .group_by(PlatformData.platform)
    )
    result = await db.execute(stats_query)
    rows = result.all()
    stats = [
        {
            "platform": r.platform,
            "total": r.total,
            "total_likes": int(r.total_likes or 0),
            "avg_price": round(float(r.avg_price), 2) if r.avg_price else 0,
        }
        for r in rows
    ]

    # 写入 Redis 缓存，5 分钟过期
    await RedisCache.set(cache_key, stats, ttl=300)

    return ResponseModel(data=stats)
