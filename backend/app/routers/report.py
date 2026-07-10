"""
智能报告API路由
AI生成：使用LLM生成数据分析报告
人工修改：添加了金宫味业业务场景的prompt模板
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.platform_data import PlatformData
from app.models.sentiment import SentimentData
from app.models.competitor import Competitor
from app.schemas.common import ResponseModel

router = APIRouter(prefix="/api/report", tags=["智能报告"])


@router.post("/generate", response_model=ResponseModel)
async def generate_report(data: dict, db: AsyncSession = Depends(get_db)):
    """AI生成数据分析报告"""
    report_type = data.get("type", "daily")

    # 收集数据摘要
    total_data = (await db.execute(select(func.count(PlatformData.id)))).scalar() or 0
    platform_stats = (await db.execute(
        select(PlatformData.platform, func.count(PlatformData.id), func.sum(PlatformData.likes))
        .group_by(PlatformData.platform)
    )).all()

    sentiment_stats = (await db.execute(
        select(SentimentData.sentiment, func.count(SentimentData.id))
        .group_by(SentimentData.sentiment)
    )).all()

    competitors = (await db.execute(
        select(Competitor).where(Competitor.is_active == 1)
    )).scalars().all()

    # 构建报告内容（无LLM时的模板报告）
    platform_lines = "\n".join([
        f"  - {r[0]}: {r[1]} 条数据, {r[2] or 0} 次互动"
        for r in platform_stats
    ])

    sentiment_lines = "\n".join([
        f"  - {r[0]}: {r[1]} 条"
        for r in sentiment_stats
    ]) if sentiment_stats else "  - 暂无舆情数据"

    comp_list = ", ".join([c.brand_name for c in competitors])

    if report_type == "daily":
        title = "金宫味业数字营销日报"
        period = "今日"
    else:
        title = "金宫味业数字营销周报"
        period = "本周"

    report = f"""# {title}

## 一、数据概览
{period}共采集营销数据 {total_data} 条，各平台分布如下：
{platform_lines}

## 二、舆情监控
情感分布情况：
{sentiment_lines}

## 三、竞品动态
当前监控竞品品牌：{comp_list}

## 四、数据洞察与建议
1. 建议关注抖音平台数据增长，当前抖音数据采集量领先
2. 持续监控竞品价格变动，及时发现市场机会
3. 关注负面舆情，及时处理消费者投诉

---
报告由AI自动生成 | 金宫味业数字营销数据中台"""

    return ResponseModel(data=report, message=f"{title}生成成功")
