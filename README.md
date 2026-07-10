# 金宫味业 - 数字营销数据中台

> AI应用全栈工程师实操项目

## 项目简介

为金宫味业构建的数字营销数据中台，实现全域数据采集、智能分析到可视化决策的闭环。
通过微信小程序为市场部运营人员提供实时数据洞察。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Uni-app + Vue3（纯 CSS 数据可视化） |
| 后端 | Python FastAPI + SQLAlchemy Async |
| 数据库 | MySQL 8.0 |
| 爬虫 | httpx + Playwright |
| AI | 通义千问 Qwen 3.7 Max（DashScope 百炼平台） |

## 项目结构

```
jingong-marketing-hub/
├── backend/          # FastAPI 后端服务
│   ├── app/
│   │   ├── main.py          # 应用入口
│   │   ├── config.py        # 配置管理
│   │   ├── database.py      # 数据库连接
│   │   ├── models/          # 数据模型（4个）
│   │   ├── schemas/         # 请求/响应模型（5个）
│   │   ├── routers/         # API路由（5个，14个端点）
│   │   └── services/        # 业务逻辑（LLM + 数据清洗）
│   └── requirements.txt
├── crawler/          # 爬虫引擎
│   ├── spiders/             # 各平台爬虫
│   ├── pipelines/           # 数据管道
│   └── run_crawler.py       # 爬虫启动入口
├── ai/               # AI服务模块（独立）
│   ├── sentiment_analyzer.py  # 情感分析
│   └── report_generator.py   # 报告生成
├── frontend/         # Uni-app 微信小程序
│   ├── pages/               # 4个页面（首页/战情室/采集/报告）
│   └── utils/               # 工具函数
├── sql/              # 数据库脚本
│   ├── init.sql             # 建表 + 初始数据
│   └── seed_sentiment.sql   # 舆情种子数据
├── docs/             # 开发文档
│   ├── 01-system-design.md      # 系统设计
│   ├── 02-api-reference.md      # API接口文档
│   ├── 03-database-design.md    # 数据库设计
│   ├── 04-ai-integration.md     # AI集成文档
│   └── 05-deployment-guide.md   # 部署运行指南
└── .ai-history/      # AI协作日志
    ├── 01-project-skeleton.md   # 阶段1：项目骨架
    ├── 02-backend-api-frontend.md # 阶段2：API+前端对接
    ├── 03-llm-integration.md    # 阶段3：LLM集成
    ├── 04-task-management.md    # 阶段4：任务管理
    └── summary.md              # 协作总结
```

## 快速启动

### 1. 初始化数据库

```bash
mysql -u root -p < sql/init.sql
mysql -u root -p jingong_marketing < sql/seed_sentiment.sql
```

### 2. 启动后端

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # 编辑配置，填入数据库密码和 DashScope API Key
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 运行爬虫

```bash
cd crawler
pip install -r requirements.txt
python run_crawler.py
```

### 4. 前端开发

使用 HBuilderX 打开 `frontend/` 目录，运行到微信开发者工具。

微信开发者工具需开启：**详情 → 本地设置 → 不校验合法域名**

## 功能模块

| 模块 | 说明 |
|------|------|
| 首页 | 核心KPI卡片、平台数据概览、近期采集任务、负面舆情预警 |
| 战情室 | 平台数据占比、情感分布、关键词情感热力图、互动量展示 |
| 采集中心 | 任务管理（执行/暂停/停止）、竞品监控、数据质量概览 |
| 智能报告 | AI生成日报/周报、AI实时情感分析 |

## AI协作说明

本项目使用 QoderWork（Qoder AI 编程助手）辅助开发：

- 代码注释中标注了「AI生成」与「人工修改」的部分（24个源文件中23个标注AI生成，9个有人工修改）
- AI协作日志记录在 `.ai-history/` 目录，包含4个开发阶段的详细日志和总结
- LLM集成使用阿里云百炼平台（DashScope）的通义千问 Qwen 3.7 Max 模型
- 核心算法保留了人工理解和讲解能力

## 数据合规

- 仅爬取公开信息，不突破反爬机制
- 不获取个人隐私数据
- 模拟数据场景下标注了真实接入方案
