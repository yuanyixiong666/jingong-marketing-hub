# 金宫味业 - 数字营销数据中台

> AI应用全栈工程师实操项目

## 项目简介

为金宫味业构建的数字营销数据中台，实现全域数据采集、智能分析到可视化决策的闭环。
通过微信小程序为市场部运营人员提供实时数据洞察。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Uni-app + Vue3 + ECharts-for-weixin |
| 后端 | Python FastAPI + SQLAlchemy |
| 数据库 | MySQL + Redis |
| 爬虫 | httpx + Playwright |
| AI | OpenAI API (情感分析 + 报告生成) |

## 项目结构

```
jingong-marketing-hub/
├── backend/          # FastAPI 后端服务
│   ├── app/
│   │   ├── main.py          # 应用入口
│   │   ├── config.py        # 配置管理
│   │   ├── database.py      # 数据库连接
│   │   ├── models/          # 数据模型
│   │   ├── schemas/         # 请求/响应模型
│   │   ├── routers/         # API路由
│   │   └── services/        # 业务逻辑
│   └── requirements.txt
├── crawler/          # 爬虫引擎
│   ├── spiders/             # 各平台爬虫
│   ├── pipelines/           # 数据管道
│   └── run_crawler.py       # 爬虫启动入口
├── ai/               # AI服务模块
│   ├── sentiment_analyzer.py  # 情感分析
│   └── report_generator.py   # 报告生成
├── frontend/         # Uni-app 微信小程序
│   ├── pages/               # 页面
│   ├── components/          # 组件
│   └── utils/               # 工具函数
├── sql/              # 数据库脚本
│   └── init.sql
├── docs/             # 开发文档
└── .ai-history/      # AI协作日志
```

## 快速启动

### 1. 初始化数据库

```bash
mysql -u root -p < sql/init.sql
```

### 2. 启动后端

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # 编辑配置
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 运行爬虫

```bash
cd crawler
pip install -r requirements.txt
python run_crawler.py
```

### 4. 前端开发

使用 HBuilderX 或微信开发者工具打开 `frontend/` 目录。

## AI协作说明

本项目强制使用AI编程平台辅助开发：

- 代码注释中标注了「AI生成」与「人工修改」的部分
- AI协作日志记录在 `.ai-history/` 目录
- 核心算法（归因模型）保留了人工理解和讲解能力

## 数据合规

- 仅爬取公开信息，不突破反爬机制
- 不获取个人隐私数据
- 模拟数据场景下标注了真实接入方案
