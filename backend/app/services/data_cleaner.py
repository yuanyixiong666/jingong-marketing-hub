"""
数据清洗服务
AI生成：去重、异常值处理、字段填充率统计
人工修改：添加了业务特定的清洗规则
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete

from app.models.platform_data import PlatformData


class DataCleaner:
    """数据清洗管道"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_quality_report(self) -> dict:
        """生成数据质量报告"""
        total = await self.db.execute(select(func.count(PlatformData.id)))
        total_count = total.scalar() or 0

        # 计算各字段填充率
        fields = ["title", "content", "price", "sales_volume"]
        fill_rates = {}
        for field in fields:
            col = getattr(PlatformData, field)
            filled = await self.db.execute(
                select(func.count(PlatformData.id)).where(col.isnot(None))
            )
            fill_rates[field] = round((filled.scalar() or 0) / max(total_count, 1) * 100, 1)

        return {
            "total_records": total_count,
            "fill_rates": fill_rates,
            "duplicate_rate": 0.0,  # TODO: 实现去重率统计
        }

    async def remove_duplicates(self) -> int:
        """去重：基于platform+title+content去重"""
        # TODO: 实现去重逻辑
        return 0
