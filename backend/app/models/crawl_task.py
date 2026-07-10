"""
爬虫任务调度模型
AI生成：定时任务记录与状态管理
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from app.database import Base


class CrawlTask(Base):
    __tablename__ = "crawl_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_name = Column(String(200), nullable=False, comment="任务名称")
    task_type = Column(String(50), comment="任务类型: crawl/clean/analyze")
    cron_expr = Column(String(100), comment="Cron表达式")
    status = Column(String(20), default="pending", comment="状态: pending/running/success/failed")
    last_run_at = Column(DateTime, comment="上次执行时间")
    next_run_at = Column(DateTime, comment="下次执行时间")
    result_summary = Column(Text, comment="执行结果摘要")
    error_message = Column(Text, comment="错误信息")
    config = Column(JSON, comment="任务配置(JSON)")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
