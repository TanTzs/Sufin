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
/* ── 基础背景 ── */
.stApp {
    background: #050c1a;
    color: #c9d6e8;
}

/* ── 侧边栏 ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #070e1f 0%, #0a1428 100%);
    border-right: 1px solid rgba(0, 200, 255, 0.15);
}
[data-testid="stSidebar"] * {
    color: #a8c0d8 !important;
}

/* ── 主标题渐变 ── */
.sufin-title {
    font-size: 2.4rem;
    font-weight: 800;
    letter-spacing: 0.04em;
    background: linear-gradient(90deg, #00c8ff 0%, #7b5fff 50%, #00e5b0 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.1rem;
}
.sufin-subtitle {
    font-size: 0.85rem;
    color: #4a7fa5;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 1.6rem;
}

/* ── 侧边栏 Logo ── */
.sufin-logo {
    font-size: 1.5rem;
    font-weight: 800;
    letter-spacing: 0.06em;
    background: linear-gradient(90deg, #00c8ff, #7b5fff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    padding: 0.8rem 0 0.4rem 0;
}
.sufin-tagline {
    font-size: 0.7rem;
    color: #2a5a7a;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-bottom: 1rem;
}

/* ── 按钮 ── */
.stButton > button {
    background: rgba(0, 180, 240, 0.06);
    border: 1px solid rgba(0, 180, 240, 0.25);
    color: #7fc8e8 !important;
    border-radius: 6px;
    font-size: 0.82rem;
    transition: all 0.2s ease;
}
.stButton > button:hover {
    background: rgba(0, 180, 240, 0.15);
    border-color: rgba(0, 200, 255, 0.6);
    color: #00e5ff !important;
    box-shadow: 0 0 12px rgba(0, 200, 255, 0.2);
}

/* ── 聊天消息 ── */
[data-testid="stChatMessage"] {
    background: rgba(10, 20, 40, 0.7);
    border: 1px solid rgba(0, 180, 240, 0.1);
    border-radius: 10px;
    margin-bottom: 0.6rem;
    backdrop-filter: blur(4px);
}

/* ── 聊天输入框 ── */
[data-testid="stChatInput"] textarea {
    background: rgba(5, 15, 35, 0.9) !important;
    border: 1px solid rgba(0, 180, 240, 0.3) !important;
    color: #c9d6e8 !important;
    border-radius: 10px !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: rgba(0, 200, 255, 0.7) !important;
    box-shadow: 0 0 16px rgba(0, 200, 255, 0.12) !important;
}

/* ── 分割线 ── */
hr {
    border-color: rgba(0, 180, 240, 0.12) !important;
}

/* ── 滚动条 ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #070e1f; }
::-webkit-scrollbar-thumb { background: #1a3a5c; border-radius: 2px; }
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
    "帮我分析苹果(AAPL)、微软(MSFT)、英伟达(NVDA) 2024年的美股投资组合，给出配置建议",
    "分析平安银行(000001)、贵州茅台(600519)、宁德时代(300750) 2023年A股组合",
    "AAPL、GOOGL、META、AMZN 四只科技股2024年怎么配置最优？",
    "帮我看看招商银行(600036)和中国平安(601318)两只股票2024年的最优组合",
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
