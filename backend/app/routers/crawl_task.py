"""
爬虫任务调度API路由
AI生成：任务管理接口
人工修改：修复序列化问题，使用Pydantic Schema，实现真实爬虫触发
"""
import asyncio
from datetime import datetime
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.crawl_task import CrawlTask
from app.schemas.common import ResponseModel
from app.schemas.crawl_task import CrawlTaskOut

router = APIRouter(prefix="/api/tasks", tags=["任务调度"])


async def _execute_crawl_task(task_id: int):
    """
    后台执行爬虫任务
    在后台异步运行Mock爬虫，完成后更新任务状态和结果摘要
    """
    import sys
    import os
    # 确保能导入crawler模块
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    from app.database import async_session
    from crawler.spiders.mock_spider import MockSpider, MockHotListSpider
    from crawler.spiders.douyin_spider import DouyinSpider
    from crawler.spiders.weibo_spider import WeiboSpider
    from crawler.spiders.xiaohongshu_spider import XiaohongshuSpider
    from crawler.spiders.tmall_spider import TmallSpider
    from crawler.spiders.jd_spider import JdSpider
    from crawler.spiders.playwright_spider import PlaywrightSpider
    from crawler.pipelines.data_pipeline import DataPipeline

    result_summary = ""
    try:
        pipeline = DataPipeline()

        # 运行Mock爬虫
        spider = MockSpider()
        data = await spider.crawl()
        await spider.close()
        save_result = await pipeline.save_batch(data)
        result_summary += f"Mock爬虫: {save_result['success']}成功/{save_result['failed']}失败 "

        # 运行热榜爬虫
        hot_spider = MockHotListSpider()
        hot_data = await hot_spider.crawl()
        await hot_spider.close()
        save_result2 = await pipeline.save_batch(hot_data)
        result_summary += f"热榜爬虫: {save_result2['success']}成功/{save_result2['failed']}失败 "

        # 运行抖音爬虫
        douyin_spider = DouyinSpider()
        douyin_data = await douyin_spider.crawl()
        await douyin_spider.close()
        save_result3 = await pipeline.save_batch(douyin_data)
        result_summary += f"抖音爬虫: {save_result3['success']}成功/{save_result3['failed']}失败 "

        # 运行微博爬虫
        weibo_spider = WeiboSpider()
        weibo_data = await weibo_spider.crawl()
        await weibo_spider.close()
        save_result4 = await pipeline.save_batch(weibo_data)
        result_summary += f"微博爬虫: {save_result4['success']}成功/{save_result4['failed']}失败 "

        # 运行小红书爬虫
        xhs_spider = XiaohongshuSpider()
        xhs_data = await xhs_spider.crawl()
        await xhs_spider.close()
        save_result5 = await pipeline.save_batch(xhs_data)
        result_summary += f"小红书爬虫: {save_result5['success']}成功/{save_result5['failed']}失败 "

        # 运行天猫爬虫
        tmall_spider = TmallSpider()
        tmall_data = await tmall_spider.crawl()
        await tmall_spider.close()
        save_result6 = await pipeline.save_batch(tmall_data)
        result_summary += f"天猫爬虫: {save_result6['success']}成功/{save_result6['failed']}失败 "

        # 运行京东爬虫
        jd_spider = JdSpider()
        jd_data = await jd_spider.crawl()
        await jd_spider.close()
        save_result7 = await pipeline.save_batch(jd_data)
        result_summary += f"京东爬虫: {save_result7['success']}成功/{save_result7['failed']}失败 "

        # 运行 Playwright 爬虫（JS渲染页面）
        pw_spider = PlaywrightSpider()
        pw_data = await pw_spider.crawl()
        await pw_spider.close()
        save_result8 = await pipeline.save_batch(pw_data)
        result_summary += f"Playwright爬虫: {save_result8['success']}成功/{save_result8['failed']}失败"

        await pipeline.close()

        # 更新任务状态为成功
        async with async_session() as db:
            result = await db.execute(select(CrawlTask).where(CrawlTask.id == task_id))
            task = result.scalar_one_or_none()
            if task:
                task.status = "success"
                task.result_summary = result_summary
                await db.commit()

    except Exception as e:
        # 更新任务状态为失败
        try:
            async with async_session() as db:
                result = await db.execute(select(CrawlTask).where(CrawlTask.id == task_id))
                task = result.scalar_one_or_none()
                if task:
                    task.status = "failed"
                    task.error_message = str(e)[:500]
                    await db.commit()
        except Exception:
            pass


@router.get("", response_model=ResponseModel[list[CrawlTaskOut]])
async def list_tasks(db: AsyncSession = Depends(get_db)):
    """获取所有爬虫任务"""
    result = await db.execute(select(CrawlTask).order_by(CrawlTask.created_at.desc()))
    tasks = result.scalars().all()
    task_outs = [CrawlTaskOut.model_validate(t) for t in tasks]
    return ResponseModel(data=task_outs)


@router.post("/{task_id}/run", response_model=ResponseModel)
async def run_task(
    task_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """手动触发任务执行（pending/paused→running），后台异步运行爬虫"""
    result = await db.execute(select(CrawlTask).where(CrawlTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        return ResponseModel(code=404, message="任务不存在")
    if task.status == "running":
        return ResponseModel(code=400, message="任务已在运行中")

    task.status = "running"
    task.last_run_at = datetime.now()
    task.error_message = None
    await db.flush()

    # 通过BackgroundTasks异步触发爬虫执行
    background_tasks.add_task(_execute_crawl_task, task_id)

    return ResponseModel(message="任务已触发，正在后台执行")


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
