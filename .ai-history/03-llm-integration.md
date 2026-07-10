# AI 协作日志 03：集成通义千问 LLM，实现 AI 智能功能

- **日期**：2026-07-10
- **AI 工具**：QoderWork（Qoder AI 编程助手）
- **提交记录**：`0f20409` feat: 集成通义千问LLM，实现AI智能报告和情感分析

## 任务目标

将项目中的 AI 功能从模板填充升级为真正的 LLM 驱动，接入阿里云百炼平台的通义千问（Qwen 3.7 Max）模型，实现智能报告生成和实时情感分析。

## AI 完成的工作

### LLM 服务层（核心模块）

新建 `backend/app/services/llm_service.py`，封装 DashScope API 调用：

- **`chat_completion()`**：通用 LLM 对话接口，使用 httpx AsyncClient 调用 DashScope OpenAI 兼容 API
- **`generate_report_content()`**：智能报告生成，接收聚合数据上下文，输出结构化 Markdown 报告
- **`analyze_sentiment()`**：实时情感分析，接收文本和关键词，返回情感标签/置信度/摘要/关键词提取

关键技术细节：
```python
payload = {
    "model": settings.LLM_MODEL,
    "messages": messages,
    "temperature": temperature,
    "max_tokens": max_tokens,
    "enable_thinking": False,  # 关键：禁用 Qwen3 思考模式
}
```

### 报告模块重构

将 `routers/report.py` 从模板填充改为 LLM 驱动：

- `/api/report/generate` 端点重构：
  1. 从数据库聚合多维度数据（平台统计、情感分布、关键词情感明细、竞品列表、价格区间、互动量汇总）
  2. 构建结构化数据上下文（data_context 字典）
  3. 调用 `generate_report_content()` 让 LLM 生成专业分析报告
  4. 返回 Markdown 格式的报告内容

- 新增 `/api/report/analyze-sentiment` 端点：
  1. 接收用户输入的文本和可选关键词
  2. 调用 `analyze_sentiment()` 进行实时情感分析
  3. 返回情感标签（正面/负面/中性）、置信度分数、摘要、提取的关键词

### 前端交互升级

- **报告页**新增 AI 加载动画：脉冲圆点 + "AI 分析中" 文字提示
- **报告页**新增 AI 情感分析交互区：
  - 文本输入框（textarea）
  - 关键词输入框
  - "开始分析"按钮
  - 结果展示区：情感标签（绿色正面/红色负面/灰色中性）、置信度百分比、分析摘要、提取关键词列表
- **api.js** 新增 `analyzeSentiment` 接口调用

### 配置更新

- `.env` 配置 DashScope：
  ```
  OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
  OPENAI_API_KEY=sk-***
  LLM_MODEL=qwen3.7-max
  ```

## 人工审查与修改

| 文件 | 人工修改内容 |
|------|-------------|
| `report.py` | 添加了金宫味业业务场景的 Prompt 模板，要求报告围绕调味品行业分析 |
| `report.vue` | 完善报告展示样式，添加 AI 情感分析的交互逻辑和结果展示 |

## 踩坑记录

### Qwen3 思考模式导致空响应

**问题**：首次调用 Qwen 3.7 Max 时，返回的 `content` 字段为空，所有输出都在 `reasoning_content` 中。

**原因**：Qwen3 系列模型默认开启"思考模式"（thinking mode），会先进行内部推理，推理内容消耗了 `max_tokens` 配额，导致实际输出为空。

**解决**：在 payload 顶层添加 `"enable_thinking": False`。注意不能用 OpenAI SDK 的 `extra_body` 参数，因为项目使用 httpx 直接调用，所以直接放在请求体中。

### enable_thinking 参数位置

**问题**：最初写成 `extra_body: {enable_thinking: False}`，这是 OpenAI Python SDK 的用法。

**解决**：项目使用 httpx 直接发 HTTP 请求，不经过 OpenAI SDK，所以 `enable_thinking` 必须放在 payload 顶层。

## 关键决策

1. **httpx 而非 openai SDK**：减少依赖，DashScope 的 OpenAI 兼容接口完全可以用 httpx 直接调用
2. **数据上下文注入**：报告生成前先聚合数据库数据，让 LLM 基于真实数据生成分析，而非凭空编造
3. **JSON 提取容错**：情感分析返回的文本中查找 `{...}` 边界，兼容 LLM 输出多余文字的情况

## 经验总结

LLM 集成阶段最大的收获是理解了 DashScope 兼容接口的调用细节。AI 帮助快速搭建了服务层代码和前端交互，但 `enable_thinking: False` 这个关键参数是人工调试发现的——这体现了 AI 协作中"人工把关"的必要性。整体上，通义千问生成的报告质量很高，能够基于数据给出专业的行业分析。
