"""
爬虫任务Schema
AI生成：任务响应模型
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CrawlTaskOut(BaseModel):
    id: int
    task_name: str
    task_type: Optional[str] = None
    cron_expr: Optional[str] = None
    status: str = "pending"
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    result_summary: Optional[str] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
