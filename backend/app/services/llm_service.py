"""
LLM服务模块
封装DashScope（通义千问）API调用，兼容OpenAI接口格式
"""
import json
import httpx
import logging
from app.config import settings

logger = logging.getLogger(__name__)

# DashScope OpenAI兼容端点
CHAT_COMPLETIONS_URL = f"{settings.DASHSCOPE_BASE_URL}/chat/completions"

# 请求超时时间（秒）
TIMEOUT = 60.0


async def chat_completion(
    messages: list[dict],
    temperature: float = 0.7,
    max_tokens: int = 2000,
) -> str:
    """
    调用LLM进行对话补全

    Args:
        messages: OpenAI格式的消息列表
        temperature: 采样温度
        max_tokens: 最大生成token数

    Returns:
        模型生成的文本内容
    """
    if not settings.DASHSCOPE_API_KEY:
        logger.warning("DASHSCOPE_API_KEY未配置，跳过LLM调用")
        return "[AI服务未配置：请在.env中设置DASHSCOPE_API_KEY]"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.DASHSCOPE_API_KEY}",
    }

    payload = {
        "model": settings.LLM_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        # 禁用Qwen3思考模式，避免reasoning_content消耗max_tokens导致空响应
        "enable_thinking": False,
    }

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                CHAT_COMPLETIONS_URL,
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        # 提取回复内容
        content = data["choices"][0]["message"]["content"]
        if not content:
            logger.warning(f"LLM返回空内容, response: {data}")
            return "[AI未返回有效内容]"

        usage = data.get("usage", {})
        logger.info(f"LLM调用成功, model={settings.LLM_MODEL}, "
                     f"prompt_tokens={usage.get('prompt_tokens', 0)}, "
                     f"completion_tokens={usage.get('completion_tokens', 0)}")
        return content

    except httpx.TimeoutException:
        logger.error("LLM API调用超时")
        return "[AI服务响应超时，请稍后重试]"
    except httpx.HTTPStatusError as e:
        logger.error(f"LLM API返回错误状态: {e.response.status_code} - {e.response.text[:200]}")
        return f"[AI服务调用失败: HTTP {e.response.status_code} | URL:{CHAT_COMPLETIONS_URL} | KEY:{settings.DASHSCOPE_API_KEY[:8]}... | RESP:{e.response.text[:100]}]"
    except Exception as e:
        logger.error(f"LLM API调用异常: {e}")
        return f"[AI服务异常: {str(e)}]"


async def generate_report_content(report_type: str, data_context: dict) -> str:
    """
    调用LLM生成数据分析报告

    Args:
        report_type: 报告类型 daily/weekly
        data_context: 数据上下文字典

    Returns:
        Markdown格式的报告内容
    """
    period = "今日" if report_type == "daily" else "本周"
    title = "金宫味业数字营销日报" if report_type == "daily" else "金宫味业数字营销周报"

    system_prompt = (
        "你是金宫味业数字营销数据中台的AI分析师。你的任务是根据提供的数据，"
        "生成专业的数据分析报告。报告要求：\n"
        "1. 使用Markdown格式\n"
        "2. 语言专业、简洁，突出关键数据变化\n"
        "3. 给出可执行的营销建议\n"
        "4. 关注调味品行业特点（季节性、渠道差异、竞品对比）\n"
        "5. 报告标题使用#，章节使用##，不要嵌套过深"
    )

    user_prompt = (
        f"请根据以下数据生成{title}：\n\n"
        f"## 数据采集概况\n"
        f"- 总数据量：{data_context.get('total_data', 0)} 条\n"
        f"- 各平台数据：\n{data_context.get('platform_lines', '暂无数据')}\n\n"
        f"## 舆情监控数据\n"
        f"- 情感分布：\n{data_context.get('sentiment_lines', '暂无舆情数据')}\n"
        f"- 各关键词舆情：\n{data_context.get('keyword_details', '暂无详细数据')}\n\n"
        f"## 竞品监控\n"
        f"- 监控品牌：{data_context.get('comp_list', '暂无竞品数据')}\n"
        f"- 竞品价格区间：{data_context.get('price_range', '暂无价格数据')}\n\n"
        f"## 互动数据\n"
        f"- 总点赞数：{data_context.get('total_likes', 0)}\n"
        f"- 总评论数：{data_context.get('total_comments', 0)}\n"
        f"- 总分享数：{data_context.get('total_shares', 0)}\n\n"
        f"请生成一份完整的{period}数据分析报告，包含：\n"
        "1. 数据概览（核心指标汇总）\n"
        "2. 平台分析（各渠道表现对比）\n"
        "3. 舆情分析（情感趋势、热点话题）\n"
        "4. 竞品动态（价格策略、市场表现）\n"
        "5. 数据洞察与建议（3-5条可执行建议）\n\n"
        "报告结尾加上：\n---\n报告由AI自动生成 | 金宫味业数字营销数据中台"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    return await chat_completion(messages, temperature=0.7, max_tokens=3000)


async def analyze_sentiment(text: str, keyword: str = "") -> dict:
    """
    调用LLM分析文本情感

    Args:
        text: 待分析文本
        keyword: 关联关键词

    Returns:
        包含sentiment和analysis的字典
    """
    messages = [
        {"role": "system", "content": "你是调味品行业舆情分析专家。分析给定文本的情感倾向，返回JSON格式结果。"},
        {"role": "user", "content": (
            f"请分析以下关于\"{keyword}\"的文本情感：\n\n"
            f"文本：{text}\n\n"
            f"请严格按以下JSON格式返回：\n"
            '{{"sentiment": "positive/negative/neutral", "score": 0.0到1.0之间的置信度, '
            '"summary": "一句话情感摘要", "keywords": ["关键词1", "关键词2"]}}'
        )},
    ]

    result = await chat_completion(messages, temperature=0.3, max_tokens=500)

    # 尝试解析JSON
    try:
        start = result.find("{")
        end = result.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(result[start:end])
    except (json.JSONDecodeError, ValueError):
        pass

    return {
        "sentiment": "neutral",
        "score": 0.5,
        "summary": result[:200],
        "keywords": [],
        "raw_response": result,
    }
