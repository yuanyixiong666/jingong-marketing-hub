-- ============================================
-- 金宫味业数字营销数据中台 - 数据库初始化
-- AI生成：建表语句和初始数据
-- ============================================

CREATE DATABASE IF NOT EXISTS jingong_marketing
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE jingong_marketing;

-- 平台数据表
CREATE TABLE IF NOT EXISTS platform_data (
    id INT PRIMARY KEY AUTO_INCREMENT,
    platform VARCHAR(50) NOT NULL COMMENT "平台名称",
    content_type VARCHAR(50) COMMENT "内容类型",
    title VARCHAR(500) COMMENT "标题/商品名",
    content TEXT COMMENT "正文内容",
    price FLOAT COMMENT "价格",
    sales_volume INT COMMENT "销量",
    likes INT DEFAULT 0 COMMENT "点赞数",
    comments_count INT DEFAULT 0 COMMENT "评论数",
    shares INT DEFAULT 0 COMMENT "分享数",
    extra_data JSON COMMENT "扩展字段",
    raw_url VARCHAR(1000) COMMENT "原始链接",
    crawled_at DATETIME COMMENT "爬取时间",
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_platform_type (platform, content_type),
    INDEX idx_crawled_at (crawled_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT="平台数据表";

-- 竞品品牌表
CREATE TABLE IF NOT EXISTS competitors (
    id INT PRIMARY KEY AUTO_INCREMENT,
    brand_name VARCHAR(100) NOT NULL UNIQUE COMMENT "品牌名称",
    keywords VARCHAR(500) COMMENT "监控关键词",
    description TEXT COMMENT "品牌描述",
    is_active TINYINT DEFAULT 1 COMMENT "是否启用",
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT="竞品品牌表";

-- 竞品价格表
CREATE TABLE IF NOT EXISTS competitor_prices (
    id INT PRIMARY KEY AUTO_INCREMENT,
    competitor_id INT NOT NULL COMMENT "竞品ID",
    platform VARCHAR(50) NOT NULL COMMENT "平台",
    product_name VARCHAR(500) COMMENT "商品名称",
    price FLOAT NOT NULL COMMENT "价格",
    original_price FLOAT COMMENT "原价",
    promotion_info TEXT COMMENT "促销信息",
    crawled_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_competitor_platform (competitor_id, platform)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT="竞品价格表";

-- 舆情记录表
CREATE TABLE IF NOT EXISTS sentiment_records (
    id INT PRIMARY KEY AUTO_INCREMENT,
    keyword VARCHAR(200) NOT NULL COMMENT "舆情关键词",
    platform VARCHAR(50) NOT NULL COMMENT "来源平台",
    content TEXT COMMENT "原始内容",
    sentiment_label VARCHAR(20) COMMENT "情感标签",
    sentiment_score FLOAT COMMENT "情感得分",
    content_tag VARCHAR(50) COMMENT "内容标签",
    source_url VARCHAR(1000) COMMENT "来源链接",
    analyzed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_keyword_sentiment (keyword, sentiment_label)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT="舆情记录表";

-- 爬虫任务表
CREATE TABLE IF NOT EXISTS crawl_tasks (
    id INT PRIMARY KEY AUTO_INCREMENT,
    task_name VARCHAR(200) NOT NULL COMMENT "任务名称",
    task_type VARCHAR(50) COMMENT "任务类型",
    cron_expr VARCHAR(100) COMMENT "Cron表达式",
    status VARCHAR(20) DEFAULT "pending" COMMENT "状态",
    last_run_at DATETIME COMMENT "上次执行时间",
    next_run_at DATETIME COMMENT "下次执行时间",
    result_summary TEXT COMMENT "执行结果摘要",
    error_message TEXT COMMENT "错误信息",
    config JSON COMMENT "任务配置",
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT="爬虫任务表";

-- ============================================
-- 初始数据：竞品品牌
-- ============================================
INSERT INTO competitors (brand_name, keywords, description) VALUES
("海天", "海天酱油,海天蚝油,海天料酒", "海天味业，调味品龙头"),
("千禾", "千禾酱油,千禾零添加,千禾醋", "千禾味业，主打零添加"),
("李锦记", "李锦记蚝油,李锦记酱油", "李锦记，港资调味品品牌"),
("厨邦", "厨邦酱油,厨邦调味", "厨邦食品，中炬高新旗下"),
("欣和", "欣和酱油,欣和豆瓣酱", "欣和集团，北方调味品品牌");

-- 初始数据：爬虫任务
INSERT INTO crawl_tasks (task_name, task_type, cron_expr, status) VALUES
("抖音热榜采集", "crawl", "0 * * * *", "pending"),
("小红书笔记搜索", "crawl", "0 */2 * * *", "pending"),
("天猫商品数据", "crawl", "0 */4 * * *", "pending"),
("京东销量数据", "crawl", "0 */4 * * *", "pending"),
("竞品价格监控", "crawl", "0 */6 * * *", "pending"),
("舆情关键词监控", "crawl", "30 */1 * * *", "pending"),
("数据清洗任务", "clean", "0 2 * * *", "pending"),
("AI情感分析", "analyze", "0 3 * * *", "pending");
