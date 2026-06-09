import os
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from tools import ALL_TOOLS

load_dotenv()

SYSTEM_PROMPT = '''你是 Sufin 金融智能体，一位专业、简洁的股票投资分析顾问。你的回答客观严谨，基于数据说话，不带无关的吹捧或废话。

工作流程：
1. 如果是看行情数据，可以通过 download_stock_data 进行观察；如果需要其他 download_stock_data 没有的数据，才可调用 tavily_search；
2. 调用 download_stock_data 下载数据（注意传入正确的 market 参数）；
3. 调用 markowitz_optimize 进行优化（A股无风险利率用 0.02，美股用 0.045）；
4. 从"风险收益特征"和"适合人群"两个维度给出配置建议。

注意：本分析仅供参考，不构成实际投资建议。
'''


def build_agent(api_key: str = None):
    '''创建并返回 Agent 实例（含 InMemorySaver checkpointer，支持多 thread_id 对话）。'''
    if api_key is None:
        api_key = os.getenv('DEEPSEEK_API_KEY', 'TAVILY_API_KEY')
    llm = ChatDeepSeek(model='deepseek-chat', api_key=api_key, temperature=0)
    return create_agent(
        model=llm,
        tools=ALL_TOOLS,
        checkpointer=InMemorySaver(),
        system_prompt=SYSTEM_PROMPT,
    )
