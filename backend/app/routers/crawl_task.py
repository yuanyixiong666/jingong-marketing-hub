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
    """手动触发任务执行（pending/paused→running）"""
    result = await db.execute(select(CrawlTask).where(CrawlTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        return ResponseModel(code=404, message="任务不存在")
    if task.status == "running":
        return ResponseModel(code=400, message="任务已在运行中")
    task.status = "running"
    task.last_run_at = datetime.now()
    await db.flush()
    # TODO: 实际触发爬虫任务（通过Redis队列或Celery）
    return ResponseModel(message="任务已触发")


@router.post("/{task_id}/pause", response_model=ResponseModel)
async def pause_task(task_id: int, db: AsyncSession = Depends(get_db)):
    """暂停正在运行的任务（running→paused）"""
    result = await db.execute(select(CrawlTask).where(CrawlTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        return ResponseModel(code=404, message="任务不存在")
    if task.status != "running":
        return ResponseModel(code=400, message="任务未在运行中，无法暂停")
    task.status = "paused"
    await db.flush()
    return ResponseModel(message="任务已暂停")


@router.post("/{task_id}/stop", response_model=ResponseModel)
async def stop_task(task_id: int, db: AsyncSession = Depends(get_db)):
    """停止任务（running/paused→pending，可重新执行）"""
    result = await db.execute(select(CrawlTask).where(CrawlTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        return ResponseModel(code=404, message="任务不存在")
    task.status = "pending"
    await db.flush()
    return ResponseModel(message="任务已停止")
