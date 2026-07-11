"""
营销归因分析API路由
人工编写：提供归因模型查询接口
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.common import ResponseModel
from app.services.attribution import compute_attribution

router = APIRouter(prefix="/api/attribution", tags=["归因分析"])


@router.get("/scores", response_model=ResponseModel)
async def get_attribution_scores(
    days: int = Query(30, ge=1, le=365, description="分析最近N天的数据"),
    db: AsyncSession = Depends(get_db),
):
    """
    获取营销归因分析结果

    归因模型采用时间衰减的多触点归因算法：
    - 时间衰减：越近的数据权重越高（半衰期7天）
    - 互动加权：分享(×3) > 评论(×2) > 点赞(×1) > 销量(×5)
    - 归因占比：各平台/内容类型的贡献分占总分的比例

    参数:
        days: 分析最近N天的数据（默认30天，最大365天）
    """
    result = await compute_attribution(db, days=days)
    return ResponseModel(data=result, message="归因分析完成")
