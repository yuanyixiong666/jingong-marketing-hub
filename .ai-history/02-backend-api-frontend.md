# AI 协作日志 02：后端 API 完善 + 前端全量对接

- **日期**：2026-07-10
- **AI 工具**：QoderWork（Qoder AI 编程助手）
- **提交记录**：`5b2fbee` feat: 完善后端API + 前端全量对接

## 任务目标

在骨架基础上补全缺失的后端 API（舆情模块、报告模块），修复数据序列化问题，完成前端所有页面与后端接口的对接。

## AI 完成的工作

### 后端新增

- **舆情模块**完整实现：
  - `models/sentiment.py`：舆情数据 ORM 模型（keyword、platform、title、content、sentiment、sentiment_score）
  - `schemas/sentiment.py`：请求/响应模型
  - `routers/sentiment.py`：分页查询接口（支持 keyword/sentiment 过滤）+ 统计接口（按关键词分组统计 + 整体情感分布）
  - 统计接口使用 `func.if_()` 实现 MySQL 条件计数的 SQL 聚合

- **报告模块**初始实现：
  - `routers/report.py`：日报/周报生成接口（初版为模板填充，后续迭代为 LLM 生成）

### Bug 修复

- **任务列表 500 错误**：`crawl_task.py` 路由返回 ORM 对象时，Pydantic 无法序列化 SQLAlchemy 模型，导致接口报 500。修复方案：引入 `CrawlTaskOut` Pydantic Schema，通过 `model_validate()` 进行 ORM → Schema 转换
- **前端请求工具**：`request.js` 优化了错误处理逻辑，添加全局 loading 提示

### 前端全量对接

- **首页**（index.vue）：对接 `getPlatformStats`、`getTasks`、`getSentimentStats` 三个接口，使用 `Promise.all` 并行请求，展示核心 KPI 卡片、平台数据概览（CSS 柱状图）、近期采集任务、负面舆情预警
- **战情室**（dashboard.vue）：对接 `getPlatformStats`、`getSentimentStats`，纯 CSS 实现数据可视化——平台数据占比横向条形图、情感分布柱状图、关键词情感热力图（正面/中性/负面三色叠加）、平台互动量展示
- **采集页**（crawler.vue）：对接 `getTasks`、`runTask`、`getCompetitors`、`getPlatformStats`，实现任务列表 + 执行按钮、竞品监控列表（关键词标签展示）、数据质量概览
- **报告页**（report.vue）：对接 `generateReport`，实现日报/周报生成按钮 + 报告内容展示区域

### 种子数据

- `sql/seed_sentiment.sql`：新增 29 条舆情记录，覆盖 5 个调味品行业关键词（零添加、有机酱油、调味品推荐、鸡精怎么选、火锅底料测评），分布在微博/小红书/抖音三个平台

## 人工审查与修改

| 文件 | 人工修改内容 |
|------|-------------|
| `crawl_task.py` | 修复序列化问题，将直接返回 ORM 对象改为使用 Pydantic Schema 转换 |
| `index.vue` | 完善 API 对接后的数据展示逻辑，调整 KPI 卡片的数据映射 |
| `dashboard.vue` | 对接真实 API 数据，替换骨架阶段的硬编码演示数据 |
| `crawler.vue` | 完善数据展示和交互逻辑，优化任务状态显示 |
| `report.vue` | 完善报告内容展示区域的样式和滚动体验 |

## 关键决策

1. **纯 CSS 可视化**：战情室页面没有引入 ECharts 等图表库，而是用纯 CSS 实现所有可视化效果，减小小程序包体积
2. **Promise.all 并行请求**：首页同时请求三个接口，减少页面加载等待时间
3. **Pydantic Schema 序列化**：统一使用 Schema 层做 ORM → JSON 转换，避免 SQLAlchemy 对象直接序列化

## 经验总结

这一阶段的核心问题是"数据流通"——确保从数据库到后端 API 到前端展示的完整链路畅通。AI 快速生成了 CRUD 代码和前端模板，人工的主要贡献在于调试序列化 Bug 和打磨前端数据展示细节。`func.if_()` 条件计数是 AI 建议的 MySQL 特定优化，避免了在 Python 层做循环统计。
