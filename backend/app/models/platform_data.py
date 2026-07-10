"""
平台数据模型 - 存储各平台爬取的原始数据
AI生成：基础表结构，含抖音、小红书、天猫、京东等
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, Index
from app.database import Base


class PlatformData(Base):
    __tablename__ = "platform_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    platform = Column(String(50), nullable=False, comment="平台名称: douyin/xiaohongshu/tmall/jd")
    content_type = Column(String(50), comment="内容类型: product/review/post/hot_list")
    title = Column(String(500), comment="标题/商品名")
    content = Column(Text, comment="正文内容")
    price = Column(Float, comment="价格")
    sales_volume = Column(Integer, comment="销量")
    likes = Column(Integer, default=0, comment="点赞数")
    comments_count = Column(Integer, default=0, comment="评论数")
    shares = Column(Integer, default=0, comment="分享数")
    extra_data = Column(JSON, comment="扩展字段(JSON)")
    raw_url = Column(String(1000), comment="原始数据链接")
    crawled_at = Column(DateTime, default=datetime.now, comment="爬取时间")
    created_at = Column(DateTime, default=datetime.now)

    __table_args__ = (
        Index("idx_platform_type", "platform", "content_type"),
        Index("idx_crawled_at", "crawled_at"),
    )
