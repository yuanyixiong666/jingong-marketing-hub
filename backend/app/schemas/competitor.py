"""
竞品Schema
AI生成：竞品相关请求和响应模型
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CompetitorCreate(BaseModel):
    brand_name: str
    keywords: Optional[str] = None
    description: Optional[str] = None


class CompetitorOut(BaseModel):
    id: int
    brand_name: str
    keywords: Optional[str] = None
    description: Optional[str] = None
    is_active: int = 1
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
