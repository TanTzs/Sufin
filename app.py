import os
import uuid
import streamlit as st
from dotenv import load_dotenv
from datetime import date
from langchain_core.messages import HumanMessage, SystemMessage
from agent import build_agent

load_dotenv()

# ── 页面配置 ──────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sufin · 金融智能体",
    page_icon="⚡",
    layout="wide",
)

# ── 全局样式注入 ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── 顶部工具栏 → 深色 ── */
header[data-testid="stHeader"] {
    background: #050d1c !important;
    border-bottom: 1px solid rgba(14, 165, 233, 0.12) !important;
}
header[data-testid="stHeader"] * { color: #5a8aaa !important; }
.stDeployButton { display: none !important; }

/* ── 主区域 ── */
.stApp { background: #050d1c; }
.block-container {
    padding-top: 2.5rem !important;
    padding-bottom: 5rem !important;
    max-width: 860px !important;
}

/* ── 侧边栏 ── */
[data-testid="stSidebar"] {
    background: #07111f !important;
    border-right: 1px solid rgba(14, 165, 233, 0.1) !important;
}

/* ── 自定义品牌文字 ── */
.sufin-title {
    font-size: 2.2rem;
    font-weight: 800;
    letter-spacing: 0.03em;
    background: linear-gradient(100deg, #38bdf8 0%, #818cf8 55%, #34d399 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
    margin-bottom: 0.3rem;
}
.sufin-subtitle {
    font-size: 0.78rem;
    color: #3a6a88;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-bottom: 2rem;
}
.sufin-logo {
    font-size: 1.4rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    background: linear-gradient(90deg, #38bdf8, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    padding: 1rem 0 0.2rem 0;
    display: block;
}
.sufin-tagline {
    font-size: 0.65rem;
    color: #1e4a6a;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
    display: block;
}

/* ── 按钮 ── */
.stButton > button {
    background: rgba(14, 165, 233, 0.05) !important;
    border: 1px solid rgba(14, 165, 233, 0.2) !important;
    color: #7ab8d4 !important;
    border-radius: 10px !important;
    font-size: 0.81rem !important;
    transition: all 0.18s ease !important;
}
.stButton > button:hover {
    background: rgba(14, 165, 233, 0.12) !important;
    border-color: rgba(56, 189, 248, 0.55) !important;
    color: #38bdf8 !important;
    box-shadow: 0 0 14px rgba(14, 165, 233, 0.18) !important;
}

/* ── 聊天消息气泡 ── */
[data-testid="stChatMessage"] {
    background: #0c1a30 !important;
    border: 1px solid rgba(14, 165, 233, 0.1) !important;
    border-radius: 14px !important;
    margin-bottom: 0.8rem !important;
    padding: 0.2rem 0.4rem !important;
}

/* ── 聊天输入区域 ── */
[data-testid="stBottom"] {
    background: linear-gradient(0deg, #050d1c 80%, transparent) !important;
    padding-bottom: 0.5rem !important;
}
[data-testid="stChatInput"],
div[data-testid="stChatInputContainer"] {
    background: #0c1a30 !important;
    border: 1px solid rgba(14, 165, 233, 0.25) !important;
    border-radius: 14px !important;
    box-shadow: 0 0 0 1px rgba(14, 165, 233, 0.08) !important;
}
[data-testid="stChatInput"]:focus-within,
div[data-testid="stChatInputContainer"]:focus-within {
    border-color: rgba(56, 189, 248, 0.55) !important;
    box-shadow: 0 0 18px rgba(14, 165, 233, 0.12) !important;
}
[data-testid="stChatInput"] textarea,
[data-testid="stChatInputTextArea"] {
    background: transparent !important;
    color: #dde6f0 !important;
    caret-color: #38bdf8 !important;
}

/* ── 分割线 ── */
hr { border-color: rgba(14, 165, 233, 0.1) !important; }

/* ── 滚动条 ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #050d1c; }
::-webkit-scrollbar-thumb { background: #1a3a58; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #1e5070; }

/* ── footer 隐藏 ── */
footer { display: none !important; }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_agent():
    api_key = os.getenv('DEEPSEEK_API_KEY') or st.secrets.get('DEEPSEEK_API_KEY', '')
    return build_agent(api_key)


# ── Session State 初始化 ──────────────────────────────────────────────────────
def _new_tid():
    return str(uuid.uuid4())

if 'threads' not in st.session_state:
    tid = _new_tid()
    st.session_state['threads'] = {tid: {'name': '新对话 1', 'display': []}}
    st.session_state['thread_order'] = [tid]
    st.session_state['current_thread'] = tid

# ── 示例问题 ──────────────────────────────────────────────────────────────────
EXAMPLES = [
    "帮我分析苹果(AAPL)、微软(MSFT)、英伟达(NVDA) 2026年的美股投资组合，给出配置建议",
    "分析平安银行(000001)、贵州茅台(600519)、宁德时代(300750) 2026年A股组合",
    "AAPL、GOOGL、META、AMZN 四只科技股2026年怎么配置最优？",
    "帮我看看招商银行(600036)和中国平安(601318)两只股票2026年的最优组合",
]

# ── 侧边栏 ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sufin-logo">⚡ SUFIN</div>', unsafe_allow_html=True)
    st.markdown('<div class="sufin-tagline">Financial Intelligence</div>', unsafe_allow_html=True)

    if st.button("＋ 新建对话", use_container_width=True):
        tid = _new_tid()
        n = len(st.session_state['thread_order']) + 1
        st.session_state['threads'][tid] = {'name': f'新对话 {n}', 'display': []}
        st.session_state['thread_order'].append(tid)
        st.session_state['current_thread'] = tid
        st.rerun()

    st.subheader("历史对话")
    for tid in reversed(st.session_state['thread_order']):
        thread = st.session_state['threads'][tid]
        is_current = tid == st.session_state['current_thread']
        label = ("▸ " if is_current else "　") + thread['name']
        if st.button(label, key=f"t_{tid}", use_container_width=True):
            st.session_state['current_thread'] = tid
            st.rerun()

    st.divider()
    if st.button("✕ 清除当前对话", use_container_width=True):
        old_tid = st.session_state['current_thread']
        old_name = st.session_state['threads'][old_tid]['name']
        new_tid = _new_tid()
        idx = st.session_state['thread_order'].index(old_tid)
        del st.session_state['threads'][old_tid]
        st.session_state['thread_order'][idx] = new_tid
        st.session_state['threads'][new_tid] = {'name': old_name, 'display': []}
        st.session_state['current_thread'] = new_tid
        st.rerun()

    st.divider()
    st.markdown("**示例问题**")
    st.caption("点击可直接发送")
    for ex in EXAMPLES:
        if st.button(ex, use_container_width=True, key=f"ex_{ex[:15]}"):
            st.session_state['pending'] = ex
            st.rerun()

    st.divider()
    st.markdown("**使用提示**")
    st.markdown("- A股：输入6位股票代码或股票名称\n- 美股：输入 Ticker 符号（如 AAPL）\n- 可直接用自然语言描述，无需填表")

# ── 主区域 ────────────────────────────────────────────────────────────────────
st.markdown('<div class="sufin-title">Sufin 金融智能体</div>', unsafe_allow_html=True)
st.markdown('<div class="sufin-subtitle">Portfolio Intelligence · Powered by AI · 仅供参考，不构成投资建议</div>', unsafe_allow_html=True)

current_tid = st.session_state['current_thread']
current_thread = st.session_state['threads'][current_tid]

for msg in current_thread['display']:
    with st.chat_message(msg['role']):
        st.markdown(msg['content'])

pending    = st.session_state.pop('pending', None)
user_input = st.chat_input("描述您想分析的投资组合，例如：分析苹果、微软、英伟达 2024 年的组合")
prompt     = pending or user_input

if prompt:
    with st.chat_message('user'):
        st.markdown(prompt)
    current_thread['display'].append({'role': 'user', 'content': prompt})

    if len(current_thread['display']) == 1:
        current_thread['name'] = prompt[:18] + ('…' if len(prompt) > 18 else '')

    with st.chat_message('assistant'):
        with st.spinner('智能体分析中，请稍候（约 20–40 秒）…'):
            try:
                agent = get_agent()

                is_first = len(current_thread['display']) == 1
                new_messages = []
                if is_first:
                    new_messages.append(
                        SystemMessage(content=f"今天是 {date.today().strftime('%Y年%m月%d日')}。")
                    )
                new_messages.append(HumanMessage(content=prompt))

                result = agent.invoke(
                    {'messages': new_messages},
                    config={'configurable': {'thread_id': current_tid}},
                )
                answer = result['messages'][-1].content
            except Exception as e:
                answer = f'分析出错：{e}'
        st.markdown(answer)

    current_thread['display'].append({'role': 'assistant', 'content': answer})
