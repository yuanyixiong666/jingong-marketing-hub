"""
平台数据Schema
AI生成：请求和响应数据验证
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class PlatformDataCreate(BaseModel):
    platform: str
    content_type: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    price: Optional[float] = None
    sales_volume: Optional[int] = None
    likes: Optional[int] = 0
    comments_count: Optional[int] = 0
    shares: Optional[int] = 0
    extra_data: Optional[dict] = None
    raw_url: Optional[str] = None


class PlatformDataOut(BaseModel):
    id: int
    platform: str
    content_type: Optional[str] = None
    title: Optional[str] = None
    price: Optional[float] = None
    sales_volume: Optional[int] = None
    likes: int = 0
    comments_count: int = 0
    crawled_at: Optional[datetime] = None

    class Config:
        from_attributes = True
