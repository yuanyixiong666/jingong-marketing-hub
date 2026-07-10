"""
舆情数据模型
AI生成：存储舆情关键词的社交讨论数据
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Index
from app.database import Base


class SentimentData(Base):
    __tablename__ = "sentiment_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    keyword = Column(String(200), nullable=False, comment="舆情关键词")
    platform = Column(String(50), comment="来源平台")
    title = Column(String(500), comment="标题")
    content = Column(Text, comment="内容摘要")
    sentiment = Column(String(20), default="neutral", comment="情感倾向: positive/negative/neutral")
    sentiment_score = Column(Float, default=0.0, comment="情感分数 -1~1")
    source_url = Column(String(1000), comment="来源链接")
    published_at = Column(DateTime, comment="发布时间")
    created_at = Column(DateTime, default=datetime.now)

    __table_args__ = (
        Index("idx_keyword", "keyword"),
        Index("idx_sentiment", "sentiment"),
    )
