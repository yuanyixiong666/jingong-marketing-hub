"""
营销归因模型 - 分析各平台/内容对用户转化的贡献度
人工编写：基于时间衰减的多触点归因算法

归因模型说明：
本模块实现了一个多触点营销归因模型（Multi-Touch Attribution），用于分析
不同平台和内容类型对用户转化（销量）的贡献度。

算法核心思路：
1. 收集每个平台/内容类型的互动数据（点赞、评论、分享、销量）
2. 使用时间衰减因子：越近的数据权重越高（半衰期 = 7天）
3. 计算每个触点的"互动贡献分" = 加权互动量
4. 按贡献分占比分配归因权重
5. 输出各平台/内容类型的归因分数和排名

公式：
  时间衰减权重 w(t) = 2^(-t / half_life_days)
  互动贡献分 S = w(t) × (likes × 1 + comments × 2 + shares × 3)
  归因占比 A_i = S_i / ΣS
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.platform_data import PlatformData


# 归因模型参数
HALF_LIFE_DAYS = 7  # 时间衰减半衰期（天）
LIKES_WEIGHT = 1.0  # 点赞权重
COMMENTS_WEIGHT = 2.0  # 评论权重（互动更深，权重更高）
SHARES_WEIGHT = 3.0  # 分享权重（传播最广，权重最高）
SALES_WEIGHT = 5.0  # 销量权重（直接转化，权重最高）


def time_decay_weight(crawled_at: datetime, now: datetime = None) -> float:
    """
    计算时间衰减权重
    使用指数衰减模型：w(t) = 2^(-t / half_life)
    越近的数据权重越高，7天前的数据权重降为一半
    """
    if now is None:
        now = datetime.now()
    if crawled_at is None:
        return 0.5  # 无时间信息时给默认权重
    days_diff = (now - crawled_at).total_seconds() / 86400
    if days_diff < 0:
        days_diff = 0
    return 2 ** (-days_diff / HALF_LIFE_DAYS)


def calculate_engagement_score(record: dict) -> float:
    """
    计算单条记录的互动贡献分
    S = w(t) × (likes×1 + comments×2 + shares×3 + sales×5)
    """
    weight = time_decay_weight(record.get("crawled_at"))
    score = (
        (record.get("likes") or 0) * LIKES_WEIGHT
        + (record.get("comments_count") or 0) * COMMENTS_WEIGHT
        + (record.get("shares") or 0) * SHARES_WEIGHT
        + (record.get("sales_volume") or 0) * SALES_WEIGHT
    )
    return weight * score


async def compute_attribution(db: AsyncSession, days: int = 30) -> Dict[str, Any]:
    """
    计算营销归因分析结果

    参数:
        db: 数据库会话
        days: 分析最近N天的数据

    返回:
        包含平台归因、内容类型归因、趋势分析的完整归因报告
    """
    now = datetime.now()
    cutoff = now - timedelta(days=days)

    # 1. 查询时间范围内的所有数据
    query = select(PlatformData).where(PlatformData.crawled_at >= cutoff)
    result = await db.execute(query)
    records = result.scalars().all()

    if not records:
        return {
            "period_days": days,
            "total_records": 0,
            "platform_attribution": [],
            "content_type_attribution": [],
            "trend": [],
            "summary": "暂无数据",
        }

    # 2. 计算每条记录的互动贡献分
    scored_records = []
    for r in records:
        record_dict = {
            "platform": r.platform,
            "content_type": r.content_type,
            "likes": r.likes,
            "comments_count": r.comments_count,
            "shares": r.shares,
            "sales_volume": r.sales_volume,
            "crawled_at": r.crawled_at,
        }
        score = calculate_engagement_score(record_dict)
        scored_records.append({**record_dict, "score": score})

    total_score = sum(r["score"] for r in scored_records)

    # 3. 按平台聚合归因分数
    platform_scores: Dict[str, float] = {}
    platform_engagement: Dict[str, Dict[str, int]] = {}
    for r in scored_records:
        p = r["platform"]
        platform_scores[p] = platform_scores.get(p, 0) + r["score"]
        if p not in platform_engagement:
            platform_engagement[p] = {"likes": 0, "comments": 0, "shares": 0, "sales": 0, "count": 0}
        platform_engagement[p]["likes"] += r["likes"] or 0
        platform_engagement[p]["comments"] += r["comments_count"] or 0
        platform_engagement[p]["shares"] += r["shares"] or 0
        platform_engagement[p]["sales"] += r["sales_volume"] or 0
        platform_engagement[p]["count"] += 1

    platform_attribution = []
    for p, score in sorted(platform_scores.items(), key=lambda x: x[1], reverse=True):
        ratio = round(score / total_score * 100, 1) if total_score > 0 else 0
        eng = platform_engagement[p]
        platform_attribution.append({
            "platform": p,
            "platform_name": _platform_name(p),
            "attribution_score": round(score, 2),
            "attribution_ratio": ratio,
            "data_count": eng["count"],
            "total_likes": eng["likes"],
            "total_comments": eng["comments"],
            "total_shares": eng["shares"],
            "total_sales": eng["sales"],
        })

    # 4. 按内容类型聚合归因分数
    content_scores: Dict[str, float] = {}
    for r in scored_records:
        ct = r["content_type"] or "unknown"
        content_scores[ct] = content_scores.get(ct, 0) + r["score"]

    content_attribution = []
    for ct, score in sorted(content_scores.items(), key=lambda x: x[1], reverse=True):
        ratio = round(score / total_score * 100, 1) if total_score > 0 else 0
        content_attribution.append({
            "content_type": ct,
            "content_name": _content_type_name(ct),
            "attribution_score": round(score, 2),
            "attribution_ratio": ratio,
        })

    # 5. 按天统计趋势（最近N天）
    daily_scores: Dict[str, float] = {}
    for r in scored_records:
        day = r["crawled_at"].strftime("%Y-%m-%d") if r["crawled_at"] else "unknown"
        daily_scores[day] = daily_scores.get(day, 0) + r["score"]

    trend = sorted(
        [{"date": d, "score": round(s, 2)} for d, s in daily_scores.items()],
        key=lambda x: x["date"],
    )

    # 6. 生成归因总结
    top_platform = platform_attribution[0] if platform_attribution else None
    summary = ""
    if top_platform:
        summary = (
            f"近{days}天内，{top_platform['platform_name']}平台贡献了{top_platform['attribution_ratio']}%的营销效果，"
            f"是最主要的流量来源。"
        )
        if len(platform_attribution) > 1:
            second = platform_attribution[1]
            summary += f"{second['platform_name']}平台占比{second['attribution_ratio']}%，位居第二。"

    return {
        "period_days": days,
        "total_records": len(scored_records),
        "total_engagement_score": round(total_score, 2),
        "model_params": {
            "half_life_days": HALF_LIFE_DAYS,
            "likes_weight": LIKES_WEIGHT,
            "comments_weight": COMMENTS_WEIGHT,
            "shares_weight": SHARES_WEIGHT,
            "sales_weight": SALES_WEIGHT,
        },
        "platform_attribution": platform_attribution,
        "content_type_attribution": content_attribution,
        "trend": trend,
        "summary": summary,
    }


def _platform_name(platform: str) -> str:
    """平台标识转中文名"""
    names = {
        "douyin": "抖音",
        "xiaohongshu": "小红书",
        "tmall": "天猫",
        "jd": "京东",
        "weibo": "微博",
        "mock": "模拟数据",
    }
    return names.get(platform, platform)


def _content_type_name(content_type: str) -> str:
    """内容类型转中文名"""
    names = {
        "product": "商品",
        "review": "评价",
        "post": "帖子",
        "hot_list": "热榜",
        "video": "视频",
        "unknown": "其他",
    }
    return names.get(content_type, content_type)
