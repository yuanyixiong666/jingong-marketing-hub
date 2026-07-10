# 部署与运行指南

## 1. 环境要求

- Python 3.11+
- MySQL 8.0+
- Node.js 16+（HBuilderX 内置）
- 微信开发者工具（最新稳定版）
- HBuilderX（Uni-app 开发 IDE）

## 2. 数据库初始化

```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE jingong_marketing CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 导入表结构和初始数据
mysql -u root -p jingong_marketing < sql/init.sql

# 导入舆情种子数据
mysql -u root -p jingong_marketing < sql/seed_sentiment.sql
```

验证：
```bash
mysql -u root -p -e "USE jingong_marketing; SHOW TABLES;"
# 应显示 5 张表：competitors, competitor_prices, crawl_tasks, platform_data, sentiment_records
```

## 3. 后端启动

```bash
cd backend

# 创建虚拟环境（首次）
python -m venv venv
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env，填入数据库密码和 DashScope API Key

# 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

启动成功后访问：
- API 服务：`http://localhost:8000`
- 健康检查：`http://localhost:8000/api/health`
- 自动文档：`http://localhost:8000/docs`（Swagger UI）

**注意**：
- 启动命令必须从 `backend/` 目录执行，因为 `.env` 的相对路径基于此
- 模块路径是 `app.main:app`（不是 `app:main`）
- `0.0.0.0` 是绑定地址，浏览器访问请用 `localhost:8000` 或 `127.0.0.1:8000`

## 4. 爬虫运行

```bash
cd crawler

# 安装依赖（可使用后端虚拟环境）
pip install -r requirements.txt

# 运行模拟爬虫
python run_crawler.py
```

爬虫会通过 HTTP POST 将模拟数据写入后端 API。

## 5. 前端运行

### 5.1 HBuilderX 配置

1. 下载并安装 [HBuilderX](https://www.dcloud.io/hbuilderx.html)
2. 文件 → 打开目录 → 选择 `frontend/` 文件夹
3. 运行 → 运行到小程序模拟器 → 微信开发者工具

### 5.2 微信开发者工具配置

1. 下载并安装 [微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)
2. 在 HBuilderX 中配置微信开发者工具路径（首次运行时会提示）
3. 打开微信开发者工具的 **详情 → 本地设置**：
   - 勾选 **"不校验合法域名、web-view（业务域名）、TLS 版本以及 HTTPS 证书"**
   - 这一步是必须的，因为开发环境使用 HTTP + localhost

### 5.3 预览和调试

- 编译后微信开发者工具会自动刷新预览
- Console 中的 `webapi_getwxaasyncsecinfo:fail` 错误可忽略（无 AppID 的访客模式）
- 确保后端服务已启动，否则 API 请求会失败

## 6. 配置文件说明

### .env（后端）

```env
# 数据库
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=你的MySQL密码
DB_NAME=jingong_marketing

# Redis（可选，用于任务队列）
REDIS_URL=redis://localhost:6379/0

# LLM（DashScope 百炼平台）
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_API_KEY=sk-***
LLM_MODEL=qwen3.7-max
```

### frontend/manifest.json

由 HBuilderX 管理，包含 Uni-app 项目配置和微信小程序 AppID。开发阶段使用测试 AppID，发布时需替换为正式 AppID。

### frontend/pages.json

定义页面路由和 TabBar 配置。当前 4 个 Tab：首页、战情室、采集、报告。

## 7. 项目代码结构

```
jingong-marketing-hub/
├── backend/              # 后端服务
│   ├── app/
│   │   ├── main.py       # FastAPI 入口
│   │   ├── config.py     # 配置管理
│   │   ├── database.py   # 数据库连接
│   │   ├── models/       # ORM 模型（4 个）
│   │   ├── schemas/      # 请求/响应模型（5 个）
│   │   ├── routers/      # API 路由（5 个，14 个端点）
│   │   └── services/     # 业务逻辑（LLM + 数据清洗）
│   ├── .env              # 环境变量（不提交 git）
│   ├── .env.example      # 环境变量模板
│   └── requirements.txt  # Python 依赖
├── frontend/             # 微信小程序
│   ├── pages/            # 4 个页面
│   ├── utils/            # 请求工具 + API 定义
│   ├── pages.json        # 页面路由
│   └── manifest.json     # 项目配置
├── crawler/              # 爬虫引擎
│   ├── spiders/          # 爬虫实现
│   ├── pipelines/        # 数据管道
│   └── run_crawler.py    # 启动入口
├── ai/                   # AI 独立模块
│   ├── sentiment_analyzer.py
│   └── report_generator.py
├── sql/                  # 数据库脚本
│   ├── init.sql          # 建表 + 初始数据
│   └── seed_sentiment.sql # 舆情种子数据
├── docs/                 # 开发文档
└── .ai-history/          # AI 协作日志
```

## 8. 常见问题

**Q: 后端启动报 ModuleNotFoundError？**
A: 确保从 `backend/` 目录执行启动命令，且虚拟环境已激活。

**Q: 微信小程序请求超时？**
A: 检查微信开发者工具是否勾选了"不校验合法域名"，以及后端服务是否正常运行。

**Q: 访问 0.0.0.0:8000 报错？**
A: `0.0.0.0` 是绑定地址，不是访问地址。请使用 `localhost:8000` 或 `127.0.0.1:8000`。

**Q: LLM 返回空内容？**
A: 检查 `.env` 中的 API Key 是否正确，以及 `enable_thinking: False` 是否在 payload 顶层。

**Q: 数据库连接失败？**
A: 确认 MySQL 服务已启动，`.env` 中的数据库密码正确，且已执行 `init.sql` 创建数据库。
