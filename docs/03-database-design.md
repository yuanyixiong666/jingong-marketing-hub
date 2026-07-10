# 数据库设计文档

## 1. 概述

数据库使用 MySQL 8.0，字符集统一为 `utf8mb4`，排序规则 `utf8mb4_unicode_ci`。共 5 张表，覆盖平台数据、竞品管理、采集任务和舆情分析四个业务域。

## 2. ER 关系

```
competitors (1) ──── (N) competitor_prices
     │
     │（独立表，通过 competitor_id 关联）
     
platform_data （独立表，爬虫写入）

sentiment_records （独立表，AI 分析写入）

crawl_tasks （独立表，任务调度）
```

## 3. 表结构

### 3.1 platform_data — 平台数据表

存储各平台采集到的营销数据。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT, PK, AUTO_INCREMENT | 主键 |
| platform | VARCHAR(50), NOT NULL | 平台标识（douyin/xiaohongshu/tmall/jd/weibo） |
| content_type | VARCHAR(50) | 内容类型（review/post/video/hot_list） |
| title | VARCHAR(500) | 标题 |
| content | TEXT | 正文内容 |
| price | DECIMAL(10,2) | 价格 |
| sales_volume | INT, DEFAULT 0 | 销量 |
| likes | INT, DEFAULT 0 | 点赞数 |
| comments_count | INT, DEFAULT 0 | 评论数 |
| shares | INT, DEFAULT 0 | 分享数 |
| extra_data | JSON | 扩展数据（标签、属性等） |
| created_at | DATETIME, DEFAULT NOW() | 创建时间 |
| updated_at | DATETIME, ON UPDATE NOW() | 更新时间 |

**索引**：`idx_platform`（platform）、`idx_content_type`（content_type）、`idx_created_at`（created_at）

### 3.2 competitors — 竞品品牌表

存储监控的竞品品牌信息。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT, PK, AUTO_INCREMENT | 主键 |
| brand_name | VARCHAR(100), UNIQUE, NOT NULL | 品牌名称 |
| keywords | TEXT | 监控关键词（逗号分隔） |
| description | TEXT | 品牌描述 |
| is_active | TINYINT(1), DEFAULT 1 | 是否启用 |
| created_at | DATETIME, DEFAULT NOW() | 创建时间 |

**初始数据**：海天、千禾、李锦记、厨邦、欣和（5 个调味品行业主要竞品）

### 3.3 competitor_prices — 竞品价格表

记录竞品的价格变动历史。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT, PK, AUTO_INCREMENT | 主键 |
| competitor_id | INT, FK → competitors.id | 关联竞品 |
| platform | VARCHAR(50) | 数据来源平台 |
| product_name | VARCHAR(200) | 产品名称 |
| price | DECIMAL(10,2) | 当前价格 |
| original_price | DECIMAL(10,2) | 原价 |
| promotion_info | VARCHAR(500) | 促销信息 |
| recorded_at | DATETIME, DEFAULT NOW() | 记录时间 |

**索引**：`idx_competitor_id`（competitor_id）、`idx_recorded_at`（recorded_at）

### 3.4 sentiment_records — 舆情数据表

存储 AI 分析后的舆情数据。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT, PK, AUTO_INCREMENT | 主键 |
| keyword | VARCHAR(100), NOT NULL | 关联关键词 |
| platform | VARCHAR(50) | 来源平台 |
| title | VARCHAR(500) | 标题 |
| content | TEXT | 内容 |
| sentiment | VARCHAR(20) | 情感标签（positive/negative/neutral） |
| sentiment_score | DECIMAL(3,2) | 情感分数（-1.00 到 1.00） |
| created_at | DATETIME, DEFAULT NOW() | 创建时间 |

**索引**：`idx_keyword`（keyword）、`idx_sentiment`（sentiment）、`idx_platform`（platform）

**初始数据**：29 条种子记录，覆盖 5 个关键词（零添加、有机酱油、调味品推荐、鸡精怎么选、火锅底料测评）

### 3.5 crawl_tasks — 采集任务表

管理数据采集任务的配置和状态。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT, PK, AUTO_INCREMENT | 主键 |
| task_name | VARCHAR(200), NOT NULL | 任务名称 |
| task_type | VARCHAR(50) | 任务类型（hot_list/search/category） |
| cron_expr | VARCHAR(100) | Cron 调度表达式 |
| status | VARCHAR(20), DEFAULT 'pending' | 任务状态 |
| last_run_at | DATETIME | 上次执行时间 |
| config | JSON | 任务配置（平台、关键词等） |
| created_at | DATETIME, DEFAULT NOW() | 创建时间 |
| updated_at | DATETIME, ON UPDATE NOW() | 更新时间 |

**任务状态机**：

```
pending ──run──→ running ──pause──→ paused
  ↑                   │                │
  └──── stop ─────────┘                │
  ↑                                    │
  └──────────── stop ──────────────────┘
                   │
         paused ──run──→ running（继续执行）
```

**初始数据**：8 个任务，包括抖音热门采集、小红书搜索、天猫品类、AI 情感分析等。

## 4. 数据库初始化

```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE jingong_marketing CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 导入建表语句和初始数据
mysql -u root -p jingong_marketing < sql/init.sql

# 导入舆情种子数据
mysql -u root -p jingong_marketing < sql/seed_sentiment.sql
```

## 5. 设计说明

- **platform_data 的 extra_data JSON 字段**：为未来扩展预留，可存储平台特有的属性（如抖音的视频链接、小红书的笔记 ID 等）
- **competitor_prices 独立建表**：价格数据变化频繁，独立表便于查询价格历史，避免 platform_data 表过于臃肿
- **sentiment_records 独立建表**：舆情数据由 AI 分析生成，与原始采集数据分离，便于独立统计和查询
- **crawl_tasks 的 config JSON 字段**：不同任务类型有不同的配置需求，JSON 字段提供灵活性
