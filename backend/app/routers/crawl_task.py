"""
爬虫任务调度API路由
AI生成：任务管理接口
人工修改：修复序列化问题，使用Pydantic Schema
"""
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.crawl_task import CrawlTask
from app.schemas.common import ResponseModel
from app.schemas.crawl_task import CrawlTaskOut

router = APIRouter(prefix="/api/tasks", tags=["任务调度"])


@router.get("", response_model=ResponseModel[list[CrawlTaskOut]])
async def list_tasks(db: AsyncSession = Depends(get_db)):
    """获取所有爬虫任务"""
    result = await db.execute(select(CrawlTask).order_by(CrawlTask.created_at.desc()))
    tasks = result.scalars().all()
    task_outs = [CrawlTaskOut.model_validate(t) for t in tasks]
    return ResponseModel(data=task_outs)


@router.post("/{task_id}/run", response_model=ResponseModel)
async def run_task(task_id: int, db: AsyncSession = Depends(get_db)):
    """手动触发任务执行"""
    result = await db.execute(select(CrawlTask).where(CrawlTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        return ResponseModel(code=404, message="任务不存在")
    task.status = "running"
    task.last_run_at = datetime.now()
    await db.flush()
    # TODO: 实际触发爬虫任务（通过Redis队列或Celery）
    return ResponseModel(message="任务已触发")
