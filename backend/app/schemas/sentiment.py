"""
舆情数据Schema
AI生成：舆情响应模型
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class SentimentOut(BaseModel):
    id: int
    keyword: str
    platform: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    sentiment: Optional[str] = "neutral"
    sentiment_score: Optional[float] = 0.0
    source_url: Optional[str] = None
    published_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
