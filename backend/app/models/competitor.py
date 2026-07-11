"""
竞品监控模型
AI生成：竞品品牌表 + 竞品价格记录表
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Index, ForeignKey
from app.database import Base


class Competitor(Base):
    __tablename__ = "competitors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    brand_name = Column(String(100), nullable=False, unique=True, comment="品牌名称")
    keywords = Column(String(500), comment="监控关键词(逗号分隔)")
    description = Column(Text, comment="品牌描述")
    is_active = Column(Integer, default=1, comment="是否启用: 1启用 0停用")
    created_at = Column(DateTime, default=datetime.now)


class CompetitorPrice(Base):
    __tablename__ = "competitor_prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id", ondelete="CASCADE"), nullable=False, comment="竞品ID")
    platform = Column(String(50), nullable=False, comment="平台")
    product_name = Column(String(500), comment="商品名称")
    price = Column(Float, nullable=False, comment="价格")
    original_price = Column(Float, comment="原价")
    promotion_info = Column(Text, comment="促销信息")
    crawled_at = Column(DateTime, default=datetime.now)

    __table_args__ = (
        Index("idx_competitor_platform", "competitor_id", "platform"),
    )
