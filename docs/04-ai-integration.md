# AI 集成文档

## 1. 概述

本项目集成阿里云百炼平台（DashScope）的通义千问 Qwen 3.7 Max 模型，提供两大 AI 功能：智能报告生成和实时情感分析。

## 2. 接入方式

### 2.1 DashScope OpenAI 兼容接口

DashScope 提供了与 OpenAI API 兼容的 HTTP 接口，可以直接使用 httpx 调用，无需安装 openai SDK。

**接口地址**：`https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions`

**认证方式**：Bearer Token（在 `.env` 中配置 `OPENAI_API_KEY`）

### 2.2 配置

```env
# .env
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_API_KEY=sk-***
LLM_MODEL=qwen3.7-max
```

配置通过 `backend/app/config.py` 的 `Settings` 类加载：

```python
class Settings(BaseSettings):
    OPENAI_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    OPENAI_API_KEY: str = ""
    LLM_MODEL: str = "qwen3.7-max"
```

## 3. 核心实现

### 3.1 LLM 服务层（llm_service.py）

位于 `backend/app/services/llm_service.py`，提供三个核心函数。

#### chat_completion() — 通用对话

```python
async def chat_completion(messages, temperature=0.7, max_tokens=1000):
    """通用 LLM 对话接口"""
    payload = {
        "model": settings.LLM_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "enable_thinking": False,  # 关键参数
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{settings.OPENAI_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
            json=payload,
        )
```

#### generate_report_content() — 智能报告

接收聚合数据上下文，构建系统 Prompt + 用户 Prompt，调用 LLM 生成 Markdown 格式的分析报告。

**系统 Prompt**：
```
你是金宫味业的资深市场数据分析师，擅长调味品行业的数据分析和市场洞察。
请根据以下数据生成一份专业的{report_type}。

报告要求：
1. 核心发现（3-5 条关键洞察）
2. 竞品动态分析
3. 风险预警
4. 可执行的建议（2-3 条）
控制在 500 字以内，使用 Markdown 格式。
```

**数据上下文注入**：将平台统计、情感分布、竞品数据等聚合结果格式化为文本，嵌入用户 Prompt。

#### analyze_sentiment() — 情感分析

接收文本和关键词，调用 LLM 进行情感分析，返回结构化 JSON。

**关键参数**：`temperature=0.1`（低温度确保分类稳定性）

**返回结构**：
```json
{
  "sentiment": "正面/负面/中性",
  "sentiment_score": 0.85,
  "summary": "分析摘要",
  "keywords": ["关键词1", "关键词2"]
}
```

**JSON 提取容错**：LLM 返回的文本可能包含额外说明文字，通过查找 `{` 和 `}` 的边界位置提取 JSON 部分。

## 4. Qwen3 关键注意事项

### 4.1 enable_thinking 参数

Qwen3 系列模型默认开启"思考模式"（thinking mode），模型会先进行内部推理（`reasoning_content`），再生成实际输出（`content`）。思考内容会消耗 `max_tokens` 配额，可能导致实际输出为空。

**解决方案**：在请求体顶层添加 `"enable_thinking": False`。

```python
# 正确写法（httpx 直接调用）
payload = {
    "model": "qwen3.7-max",
    "messages": [...],
    "enable_thinking": False,  # 顶层
}

# 错误写法（OpenAI SDK 专用，httpx 不识别）
payload = {
    "model": "qwen3.7-max",
    "messages": [...],
    "extra_body": {"enable_thinking": False},  # 无效
}
```

### 4.2 模型选择

| 模型 | 特点 | 适用场景 |
|------|------|---------|
| qwen3.7-max | 综合能力最强 | 报告生成、复杂分析 |
| qwen3.7-plus | 性价比高，速度更快 | 简单情感分析、批量处理 |

## 5. API 端点

### POST /api/report/generate

生成日报/周报。

**请求**：`{"report_type": "daily"}`

**处理流程**：
1. 查询 platform_data 各平台统计
2. 查询 sentiment_records 情感分布
3. 查询各关键词的情感明细
4. 查询竞品列表和价格区间
5. 汇总互动量数据
6. 构建 data_context 字典
7. 调用 `generate_report_content(data_context, report_type)`
8. 返回 Markdown 报告

### POST /api/report/analyze-sentiment

实时情感分析。

**请求**：`{"text": "待分析文本", "keyword": "关键词"}`

**处理流程**：
1. 校验文本非空
2. 调用 `analyze_sentiment(text, keyword)`
3. 返回情感标签 + 置信度 + 摘要 + 关键词

## 6. 独立 AI 模块

除后端集成外，`ai/` 目录还提供了独立的 AI 模块，可单独运行测试：

```python
# 情感分析
from ai.sentiment_analyzer import SentimentAnalyzer
analyzer = SentimentAnalyzer()
result = await analyzer.analyze("这款酱油味道很好", keyword="酱油")

# 报告生成
from ai.report_generator import ReportGenerator
generator = ReportGenerator()
report = await generator.generate(data_summary, report_type="daily")
```

这些模块的 Prompt 模板与后端集成版一致，但支持独立调用，便于开发和调试。

## 7. 错误处理

LLM 调用可能因网络、配额、模型异常等原因失败。服务层做了以下容错：

- **网络超时**：httpx 设置 60 秒超时
- **API 错误**：捕获异常，返回中文友好提示
- **JSON 解析失败**：情感分析返回默认中性结果
- **空响应**：检查 content 是否为空，提供 fallback 文案
