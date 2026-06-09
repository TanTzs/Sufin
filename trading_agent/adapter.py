"""
TradingAgents-CN 适配层（A股增强版）
项目地址：https://github.com/hsliuping/TradingAgents-CN

安装方式：
    pip install git+https://github.com/hsliuping/TradingAgents-CN.git
"""

_PROVIDER_DEFAULTS = {
    "deepseek": {
        "llm_provider": "deepseek",
        "deep_think_llm": "deepseek-chat",
        "quick_think_llm": "deepseek-chat",
        "backend_url": "https://api.deepseek.com/v1",
    },
    "openai": {
        "llm_provider": "openai",
        "deep_think_llm": "gpt-4o",
        "quick_think_llm": "gpt-4o-mini",
        "backend_url": "https://api.openai.com/v1",
    },
    "anthropic": {
        "llm_provider": "anthropic",
        "deep_think_llm": "claude-opus-4-8",
        "quick_think_llm": "claude-haiku-4-5-20251001",
        "backend_url": "",
    },
    "qwen": {
        "llm_provider": "dashscope",
        "deep_think_llm": "qwen-plus-latest",
        "quick_think_llm": "qwen-turbo",
        "backend_url": "",
    },
}

ALL_ANALYSTS = ["market", "social", "news", "fundamentals"]


def _build_config(provider: str, deep_model: str, quick_model: str) -> dict:
    base = {
        "max_debate_rounds": 1,
        "max_risk_discuss_rounds": 1,
        "online_tools": True,
        "online_news": True,
        "checkpoint_enabled": False,
    }
    defaults = _PROVIDER_DEFAULTS.get(provider, _PROVIDER_DEFAULTS["deepseek"])
    base.update(defaults)
    if deep_model:
        base["deep_think_llm"] = deep_model
    if quick_model:
        base["quick_think_llm"] = quick_model
    return base


def run_analysis(
    ticker: str,
    analysis_date: str,
    provider: str = "deepseek",
    deep_model: str = "",
    quick_model: str = "",
    analysts: list = None,
) -> str:
    """
    调用 TradingAgents-CN 对指定股票进行多智能体深度分析。

    Args:
        ticker:        股票代码。A股：6位数字如 000001、600519；
                       港股：如 0700.HK；美股：如 AAPL
        analysis_date: 分析日期，格式 YYYY-MM-DD
        provider:      LLM 提供商：deepseek / openai / anthropic / qwen
        deep_model:    深度思考模型，留空使用 provider 默认值
        quick_model:   快速推理模型，留空使用 provider 默认值
        analysts:      启用的分析师列表，默认全部启用
                       可选项：market / social / news / fundamentals

    Returns:
        分析报告（Markdown 格式字符串）
    """
    try:
        from tradingagents.graph.trading_graph import TradingAgentsGraph
    except ImportError:
        return (
            "**未检测到 TradingAgents-CN，请先安装：**\n\n"
            "```bash\n"
            "pip install git+https://github.com/hsliuping/TradingAgents-CN.git\n"
            "```"
        )

    config = _build_config(provider, deep_model, quick_model)
    selected = analysts or ALL_ANALYSTS

    try:
        ta = TradingAgentsGraph(
            selected_analysts=selected,
            debug=False,
            config=config,
        )
        insights, decision = ta.propagate(ticker.strip(), analysis_date)

        parts = [f"## {ticker.upper()} · {analysis_date} 深度分析报告\n"]

        if isinstance(insights, dict) and insights:
            parts.append("### 各分析师观点摘要\n")
            label_map = {
                "market":       "市场技术分析",
                "fundamentals": "基本面分析",
                "news":         "新闻资讯",
                "social":       "社交情绪",
            }
            for key, content in insights.items():
                label = label_map.get(key, key)
                parts.append(f"**{label}**\n{content}\n")

        parts.append("### 最终投资决策\n")
        parts.append(str(decision))

        return "\n".join(parts)

    except Exception as e:
        return f"分析出错：{e}"
