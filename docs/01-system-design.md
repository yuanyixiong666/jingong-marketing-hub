# 系统设计文档

## 1. 系统概述

金宫味业数字营销数据中台是一个面向调味品行业的垂直数据平台，为市场部运营人员提供全域数据采集、智能分析和可视化决策支持。系统以微信小程序为载体，实现移动端实时数据洞察。

## 2. 架构设计

### 2.1 整体架构

系统采用前后端分离的四层架构：

```
┌─────────────────────────────────────────────────────┐
│                   微信小程序（Uni-app）                │
│  首页 │ 战情室 │ 采集中心 │ 智能报告                    │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP REST API
┌──────────────────────▼──────────────────────────────┐
│                  FastAPI 后端服务                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │ 数据接口  │ │ 舆情接口  │ │ 报告接口  │            │
│  └──────────┘ └──────────┘ └──────────┘            │
│  ┌──────────────────────────────────────┐           │
│  │          LLM 服务层（DashScope）       │           │
│  └──────────────────────────────────────┘           │
└──────────────────────┬──────────────────────────────┘
                       │ SQLAlchemy Async
┌──────────────────────▼──────────────────────────────┐
│                     MySQL 数据库                       │
│  platform_data │ competitors │ sentiment │ tasks     │
└─────────────────────────────────────────────────────┘
                       ▲
                       │ HTTP POST
┌──────────────────────┴──────────────────────────────┐
│                    爬虫引擎                            │
│  base_spider → mock_spider / douyin_spider           │
│  data_pipeline → 后端 API 写入                        │
└─────────────────────────────────────────────────────┘
```

### 2.2 技术选型

| 层级 | 技术 | 选型理由 |
|------|------|---------|
| 前端 | Uni-app + Vue3 | 跨端编译能力，一套代码可发布为微信小程序/H5/App |
| 可视化 | 纯 CSS | 减小小程序包体积，避免引入 ECharts 等大型库 |
| 后端 | FastAPI | 原生异步支持，自动 API 文档，类型安全 |
| ORM | SQLAlchemy 2.0 async | 成熟的 Python ORM，异步支持完善 |
| 数据库 | MySQL 8.0 | 金宫味业现有 IT 基础设施 |
| 爬虫 | httpx + Playwright | httpx 异步 HTTP，Playwright 处理 JS 渲染页面 |
| AI | DashScope（通义千问 Qwen 3.7 Max） | 国产大模型，OpenAI 兼容接口 |

### 2.3 模块划分

**后端模块**（`backend/app/`）：

- `main.py`：应用入口，路由注册，CORS 中间件，生命周期管理
- `config.py`：集中配置（MySQL、Redis、LLM），基于 Pydantic BaseSettings
- `database.py`：异步数据库引擎，会话管理，依赖注入
- `models/`：ORM 数据模型（4 个模块）
- `schemas/`：Pydantic 请求/响应模型（4 个模块 + 通用模型）
- `routers/`：API 路由（5 个模块，14 个端点）
- `services/`：业务逻辑层（LLM 服务、数据清洗）

**前端模块**（`frontend/`）：

- `pages/index/`：首页 - 核心 KPI + 数据概览 + 舆情预警
- `pages/dashboard/`：战情室 - CSS 数据可视化
- `pages/crawler/`：采集中心 - 任务管理 + 竞品监控
- `pages/report/`：智能报告 - AI 报告生成 + 情感分析
- `utils/request.js`：HTTP 请求封装
- `utils/api.js`：API 接口集中管理

**爬虫模块**（`crawler/`）：

- `spiders/base_spider.py`：抽象基类（httpx 客户端 + UA 轮换）
- `spiders/mock_spider.py`：模拟数据爬虫（开发演示用）
- `spiders/douyin_spider.py`：抖音爬虫框架
- `pipelines/data_pipeline.py`：数据管道（HTTP 写入后端）

**AI 模块**（`ai/`）：

- `sentiment_analyzer.py`：LLM 情感分析（独立模块）
- `report_generator.py`：LLM 报告生成（独立模块）

## 3. 数据流设计

### 3.1 数据采集流

```
爬虫启动 → Spider.crawl() → 获取原始数据
  → DataPipeline.process() → HTTP POST /api/platform-data
    → FastAPI Router → SQLAlchemy ORM → MySQL
```

### 3.2 智能分析流

```
用户点击"生成报告" → POST /api/report/generate
  → 聚合数据库多维度数据（平台统计、情感分布、竞品数据）
    → 构建 data_context → 调用 DashScope LLM
      → 返回 Markdown 报告 → 前端渲染
```

### 3.3 情感分析流

```
用户输入文本 → POST /api/report/analyze-sentiment
  → 调用 DashScope LLM（temperature=0.1 确保稳定性）
    → JSON 解析（含容错处理）
      → 返回情感标签 + 置信度 + 摘要 + 关键词
```

## 4. 安全设计

### 4.1 CORS 配置

开发阶段允许所有来源（`allow_origins=["*"]`），生产环境应限制为微信小程序的域名。

### 4.2 数据合规

- 仅爬取公开信息，不突破反爬机制
- 不获取个人隐私数据
- 模拟数据场景下标注了真实接入方案

### 4.3 API Key 管理

LLM API Key 通过 `.env` 文件管理，已加入 `.gitignore`，不会提交到代码仓库。

## 5. 扩展性设计

- `platform_data` 表的 `extra_data` JSON 字段支持灵活扩展
- 爬虫采用基类 + 子类模式，新增平台只需继承 `BaseSpider`
- LLM 服务层抽象了通用调用接口，切换模型只需修改 `.env` 配置
