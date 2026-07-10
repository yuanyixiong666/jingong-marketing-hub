# API 接口文档

## 基础信息

- **Base URL**：`http://localhost:8000`
- **协议**：HTTP（开发环境）
- **数据格式**：JSON
- **字符编码**：UTF-8

## 通用响应格式

所有接口统一返回以下格式：

```json
{
  "code": 200,
  "message": "成功",
  "data": { ... }
}
```

分页接口返回：

```json
{
  "code": 200,
  "message": "成功",
  "data": {
    "items": [ ... ],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

---

## 1. 健康检查

### GET /api/health

检查服务运行状态。

**响应示例**：
```json
{
  "app": "金宫味业数字营销数据中台",
  "version": "1.0.0",
  "status": "healthy"
}
```

---

## 2. 平台数据（/api/platform-data）

### POST /api/platform-data

创建平台数据记录（爬虫写入接口）。

**请求体**：
```json
{
  "platform": "douyin",
  "content_type": "review",
  "title": "金宫鸡精测评",
  "content": "这款鸡精味道很鲜...",
  "price": 29.9,
  "sales_volume": 1500,
  "likes": 320,
  "comments_count": 45,
  "shares": 12,
  "extra_data": {"tags": ["测评", "调味品"]}
}
```

### GET /api/platform-data

分页查询平台数据。

**查询参数**：
- `platform`（可选）：平台筛选，如 `douyin`、`xiaohongshu`、`tmall`、`jd`
- `content_type`（可选）：内容类型筛选
- `page`（默认 1）：页码
- `page_size`（默认 20）：每页条数

### GET /api/platform-data/stats

获取各平台汇总统计。

**响应 data 示例**：
```json
[
  {
    "platform": "douyin",
    "data_count": 50,
    "total_likes": 12500,
    "avg_price": 35.6
  },
  {
    "platform": "xiaohongshu",
    "data_count": 30,
    "total_likes": 8900,
    "avg_price": 42.1
  }
]
```

---

## 3. 竞品管理（/api/competitors）

### POST /api/competitors

添加竞品品牌。

**请求体**：
```json
{
  "brand_name": "海天",
  "keywords": "海天酱油,海天蚝油,海天调味",
  "description": "国内调味品龙头企业"
}
```

### GET /api/competitors

获取所有活跃竞品列表。

**响应 data 示例**：
```json
[
  {
    "id": 1,
    "brand_name": "海天",
    "keywords": "海天酱油,海天蚝油,海天调味",
    "description": "国内调味品龙头企业",
    "is_active": 1
  }
]
```

### GET /api/competitors/{id}/prices

获取指定竞品的价格历史（最近 50 条）。

**路径参数**：
- `id`：竞品 ID

---

## 4. 采集任务（/api/tasks）

### GET /api/tasks

获取所有采集任务列表（按创建时间倒序）。

**响应 data 示例**：
```json
[
  {
    "id": 1,
    "task_name": "抖音热门调味品采集",
    "task_type": "hot_list",
    "cron_expr": "0 */6 * * *",
    "status": "running",
    "last_run_at": "2026-07-11T08:00:00",
    "config": {"platform": "douyin"}
  }
]
```

### POST /api/tasks/{id}/run

手动触发任务执行。

**状态要求**：任务必须处于 `pending` 或 `paused` 状态。

**状态变更**：`pending/paused → running`

### POST /api/tasks/{id}/pause

暂停正在运行的任务。

**状态要求**：任务必须处于 `running` 状态。

**状态变更**：`running → paused`

### POST /api/tasks/{id}/stop

停止任务并重置状态。

**状态变更**：`running/paused → pending`

---

## 5. 舆情数据（/api/sentiment）

### GET /api/sentiment

分页查询舆情数据。

**查询参数**：
- `keyword`（可选）：关键词筛选
- `sentiment`（可选）：情感倾向筛选，可选值 `positive`、`negative`、`neutral`
- `page`（默认 1）：页码
- `page_size`（默认 20）：每页条数

### GET /api/sentiment/stats

获取舆情统计数据。

**响应 data 示例**：
```json
{
  "keyword_stats": [
    {
      "keyword": "零添加",
      "total": 8,
      "positive_count": 3,
      "negative_count": 2,
      "neutral_count": 3
    }
  ],
  "overall": {
    "total": 29,
    "positive": 10,
    "negative": 8,
    "neutral": 11
  }
}
```

---

## 6. 智能报告（/api/report）

### POST /api/report/generate

AI 生成数据分析报告。

**请求体**：
```json
{
  "report_type": "daily"
}
```

- `report_type`：报告类型，可选 `daily`（日报）或 `weekly`（周报）

**响应 data 示例**：
```json
{
  "report_type": "daily",
  "generated_at": "2026-07-11T10:30:00",
  "content": "## 金宫味业每日营销数据报告\n\n### 一、核心发现\n\n1. 抖音平台数据量占比最高..."
}
```

**处理流程**：
1. 聚合平台数据统计
2. 统计情感分布和关键词情感明细
3. 获取竞品列表和价格区间
4. 汇总互动量数据
5. 调用通义千问 LLM 生成分析报告

### POST /api/report/analyze-sentiment

AI 实时情感分析。

**请求体**：
```json
{
  "text": "金宫的零添加酱油真的很好用，味道鲜美，家人都喜欢",
  "keyword": "零添加"
}
```

- `text`（必填）：待分析文本
- `keyword`（可选）：关联关键词

**响应 data 示例**：
```json
{
  "sentiment": "正面",
  "sentiment_score": 0.85,
  "summary": "用户对金宫零添加酱油持积极评价，认为产品味道鲜美",
  "keywords": ["零添加", "酱油", "味道鲜美"]
}
```

---

## 错误码说明

| 状态码 | 含义 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |
