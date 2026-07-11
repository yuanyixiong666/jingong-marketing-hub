"""
金宫味业数字营销数据中台 - FastAPI入口
AI生成：应用初始化、路由注册、生命周期管理
人工修改：添加了中文注释和CORS配置、归因分析路由、API Key认证
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db
from app.routers import platform_data, competitor, crawl_task, sentiment, report, attribution


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化数据库"""
    await init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# CORS配置 - 允许微信小程序跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API Key认证中间件（可选，配置了API_AUTH_KEY才生效）
@app.middleware("http")
async def api_key_auth(request: Request, call_next):
    """简单的API Key认证中间件
    - 健康检查接口 /api/health 不需要认证
    - 如果配置了 API_AUTH_KEY 环境变量，其他接口需要携带 X-API-Key 请求头
    - 未配置 API_AUTH_KEY 时不做认证（开发模式）
    """
    # 健康检查不需要认证
    if request.url.path == "/api/health":
        return await call_next(request)

    # 未配置认证密钥时跳过（开发模式）
    if not settings.API_AUTH_KEY:
        return await call_next(request)

    # 验证API Key
    api_key = request.headers.get("X-API-Key", "")
    if api_key != settings.API_AUTH_KEY:
        return JSONResponse(
            status_code=401,
            content={"code": 401, "message": "未授权：无效的API Key"},
        )

    return await call_next(request)


# 注册路由
app.include_router(platform_data.router)
app.include_router(competitor.router)
app.include_router(crawl_task.router)
app.include_router(sentiment.router)
app.include_router(report.router)
app.include_router(attribution.router)


@app.get("/api/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}
