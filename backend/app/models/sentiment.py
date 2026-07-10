"""
舆情分析模型
AI生成：存储AI情感分析结果
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Index
from app.database import Base


class SentimentRecord(Base):
    __tablename__ = "sentiment_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    keyword = Column(String(200), nullable=False, comment="舆情关键词")
    platform = Column(String(50), nullable=False, comment="来源平台")
    content = Column(Text, comment="原始内容")
    sentiment_label = Column(String(20), comment="情感标签: positive/negative/neutral")
    sentiment_score = Column(Float, comment="情感得分(-1~1)")
    content_tag = Column(String(50), comment="内容标签: 测评/recipe/促销/讨论")
    source_url = Column(String(1000), comment="来源链接")
    analyzed_at = Column(DateTime, default=datetime.now, comment="分析时间")

    __table_args__ = (
        Index("idx_keyword_sentiment", "keyword", "sentiment_label"),
    )
