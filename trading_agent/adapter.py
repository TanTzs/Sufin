"""
TradingAgents 适配层
项目地址：https://github.com/tauricresearch/tradingagents

安装方式（二选一）：
    pip install tradingagents
    git clone https://github.com/TauricResearch/TradingAgents && cd TradingAgents && pip install .
"""


def _build_config(provider: str, deep_model: str, quick_model: str) -> dict:
    configs = {
        "openai": {
            "llm_provider": "openai",
            "deep_think_llm": deep_model or "gpt-4o",
            "quick_think_llm": quick_model or "gpt-4o-mini",
            "backend_url": "https://api.openai.com/v1",
        },
        "deepseek": {
            "llm_provider": "deepseek",
            "deep_think_llm": deep_model or "deepseek-chat",
            "quick_think_llm": quick_model or "deepseek-chat",
            "backend_url": "https://api.deepseek.com/v1",
        },
        "anthropic": {
            "llm_provider": "anthropic",
            "deep_think_llm": deep_model or "claude-opus-4-8",
            "quick_think_llm": quick_model or "claude-haiku-4-5-20251001",
            "backend_url": "",
        },
    }
    base = {
        "max_debate_rounds": 1,
        "max_risk_discuss_rounds": 1,
        "online_tools": True,
        "checkpoint_enabled": False,
    }
    base.update(configs.get(provider, configs["openai"]))
    return base


def run_analysis(
    ticker: str,
    analysis_date: str,
    provider: str = "openai",
    deep_model: str = "",
    quick_model: str = "",
) -> str:
    """
    调用 TradingAgents 对指定股票和日期进行多智能体分析。

    Args:
        ticker:        股票代码，如 NVDA、AAPL（目前主要支持美股）
        analysis_date: 分析日期，格式 YYYY-MM-DD
        provider:      LLM 提供商，支持 openai / deepseek / anthropic
        deep_model:    深度思考模型名，留空使用默认值
        quick_model:   快速推理模型名，留空使用默认值

    Returns:
        分析报告字符串（Markdown）
    """
    try:
        from tradingagents.graph.trading_graph import TradingAgentsGraph
    except ImportError:
        return (
            "**未检测到 TradingAgents，请先安装：**\n\n"
            "```bash\n"
            "pip install tradingagents\n"
            "```\n"
            "或从源码安装：\n"
            "```bash\n"
            "git clone https://github.com/TauricResearch/TradingAgents\n"
            "cd TradingAgents && pip install .\n"
            "```"
        )

    config = _build_config(provider, deep_model or None, quick_model or None)
    try:
        ta = TradingAgentsGraph(debug=False, config=config)
        _, decision = ta.propagate(ticker.upper(), analysis_date)
        return f"## {ticker.upper()} · {analysis_date} 分析报告\n\n{decision}"
    except Exception as e:
        return f"分析出错：{e}"
