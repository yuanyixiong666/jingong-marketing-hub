"""
数据清洗服务
AI生成：去重、异常值处理、字段填充率统计
人工修改：实现了完整的去重逻辑（基于platform+title+content哈希去重）
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete, and_

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

        # 计算重复率
        duplicate_count = await self._count_duplicates()
        duplicate_rate = round(duplicate_count / max(total_count, 1) * 100, 1)

        return {
            "total_records": total_count,
            "fill_rates": fill_rates,
            "duplicate_rate": duplicate_rate,
            "duplicate_count": duplicate_count,
        }

    async def _count_duplicates(self) -> int:
        """
        统计重复数据数量
        重复定义：相同 platform + title + content 的记录视为重复
        使用子查询找出出现次数>1的组合，统计多余的记录数
        """
        # 查询每个 (platform, title, content) 组合的出现次数
        dup_query = (
            select(
                PlatformData.platform,
                PlatformData.title,
                PlatformData.content,
                func.count(PlatformData.id).label("cnt"),
            )
            .group_by(PlatformData.platform, PlatformData.title, PlatformData.content)
            .having(func.count(PlatformData.id) > 1)
        )
        result = await self.db.execute(dup_query)
        rows = result.all()

        # 每组重复数据中保留1条，多余的计入重复数
        duplicate_count = sum(row.cnt - 1 for row in rows)
        return duplicate_count

    async def remove_duplicates(self) -> int:
        """
        去重：基于 platform + title + content 去重
        策略：对每组重复记录，保留 id 最小的一条，删除其余
        返回删除的记录数
        """
        # 找出所有重复组合
        dup_query = (
            select(
                PlatformData.platform,
                PlatformData.title,
                PlatformData.content,
                func.count(PlatformData.id).label("cnt"),
            )
            .group_by(PlatformData.platform, PlatformData.title, PlatformData.content)
            .having(func.count(PlatformData.id) > 1)
        )
        result = await self.db.execute(dup_query)
        dup_groups = result.all()

        if not dup_groups:
            return 0

        deleted_count = 0

        for group in dup_groups:
            # 查询该组所有记录，按 id 升序
            records_query = (
                select(PlatformData)
                .where(
                    and_(
                        PlatformData.platform == group.platform,
                        PlatformData.title == group.title,
                        PlatformData.content == group.content,
                    )
                )
                .order_by(PlatformData.id.asc())
            )
            records_result = await self.db.execute(records_query)
            records = records_result.scalars().all()

            # 保留第一条（id最小），删除其余
            ids_to_delete = [r.id for r in records[1:]]
            if ids_to_delete:
                await self.db.execute(
                    delete(PlatformData).where(PlatformData.id.in_(ids_to_delete))
                )
                deleted_count += len(ids_to_delete)

        await self.db.flush()
        return deleted_count
