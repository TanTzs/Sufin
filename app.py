import os
import uuid
import html as _html
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
/* ── 顶部栏（与主区域同色）── */
header[data-testid="stHeader"] {
    background: #f4f7fa !important;
    border-bottom: 1px solid #e2e8f0 !important;
    box-shadow: none !important;
}
header[data-testid="stHeader"] * { color: #64748b !important; }
.stDeployButton { display: none !important; }
footer { display: none !important; }

/* ── 主区域（浅色）── */
.stApp { background: #f4f7fa; }
.block-container {
    padding-top: 2.5rem !important;
    padding-bottom: 5rem !important;
    max-width: 860px !important;
}

/* ── 侧边栏 ── */
[data-testid="stSidebar"] {
    background: #1e3a5f !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #a8c4d8 !important;
}

/* ── 侧边栏按钮 ── */
[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: #a8c4d8 !important;
    border-radius: 10px !important;
    font-size: 0.81rem !important;
    transition: all 0.16s ease !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.1) !important;
    border-color: rgba(168,196,216,0.5) !important;
    color: #e8f2fa !important;
}

/* ── 品牌标题（主区域）── */
.sufin-title {
    font-size: 2.2rem;
    font-weight: 800;
    letter-spacing: 0.02em;
    background: linear-gradient(110deg, #1e3a8a 0%, #4338ca 55%, #0e7490 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
    margin-bottom: 0.3rem;
}
.sufin-subtitle {
    font-size: 0.76rem;
    color: #94a3b8;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-bottom: 2rem;
}

/* ── 侧边栏品牌 ── */
.sufin-logo {
    font-size: 1.4rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    background: linear-gradient(90deg, #7dd3fc, #c4b5fd) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    padding: 1rem 0 0.2rem 0;
    display: block;
}
.sufin-tagline {
    font-size: 0.65rem;
    color: #3a6a8a !important;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
    display: block;
}

/* ── 主区域按钮 ── */
.stButton > button {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    color: #475569 !important;
    border-radius: 10px !important;
    font-size: 0.81rem !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
    transition: all 0.16s ease !important;
}
.stButton > button:hover {
    background: #f8fafc !important;
    border-color: #94a3b8 !important;
    color: #1e3a8a !important;
    box-shadow: 0 2px 8px rgba(37,99,235,0.1) !important;
}

/* ── 聊天消息 ── */
[data-testid="stChatMessage"] {
    background: #ffffff !important;
    border: 1px solid #e9eef5 !important;
    border-radius: 16px !important;
    margin-bottom: 0.8rem !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05) !important;
    padding: 0.2rem 0.4rem !important;
}

/* ── 聊天输入区域 ── */
[data-testid="stBottom"] {
    background: linear-gradient(0deg, #f1f5f9 70%, transparent) !important;
}
[data-testid="stChatInput"],
div[data-testid="stChatInputContainer"] {
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 16px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
}
[data-testid="stChatInput"]:focus-within,
div[data-testid="stChatInputContainer"]:focus-within {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.1) !important;
}
[data-testid="stChatInput"] textarea,
[data-testid="stChatInputTextArea"] {
    background: transparent !important;
    color: #0f172a !important;
}

/* ── 分割线 ── */
hr { border-color: #e2e8f0 !important; }

/* ── 滚动条 ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #f1f5f9; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
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

# ── 头像 ─────────────────────────────────────────────────────────────────────
AVATAR_USER      = "🧑‍💼"
AVATAR_ASSISTANT = "📊"

def _user_bubble(content: str):
    safe = _html.escape(content).replace('\n', '<br>')
    st.markdown(f'''
<div style="display:flex;justify-content:flex-end;align-items:flex-end;
            gap:10px;margin:4px 0 14px 0;">
  <div style="background:#1d4ed8;color:#fff;padding:11px 16px;
              border-radius:20px 20px 4px 20px;max-width:72%;
              font-size:0.93rem;line-height:1.55;word-break:break-word;
              box-shadow:0 2px 6px rgba(29,78,216,0.2);">
    {safe}
  </div>
  <span style="font-size:1.5rem;flex-shrink:0;margin-bottom:2px;">{AVATAR_USER}</span>
</div>''', unsafe_allow_html=True)

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
    if msg['role'] == 'user':
        _user_bubble(msg['content'])
    else:
        with st.chat_message('assistant', avatar=AVATAR_ASSISTANT):
            st.markdown(msg['content'])

pending    = st.session_state.pop('pending', None)
user_input = st.chat_input("描述您想分析的投资组合，例如：分析苹果、微软、英伟达 2026 年应该如何配置？")
prompt     = pending or user_input

if prompt:
    _user_bubble(prompt)
    current_thread['display'].append({'role': 'user', 'content': prompt})

    if len(current_thread['display']) == 1:
        current_thread['name'] = prompt[:18] + ('…' if len(prompt) > 18 else '')

    with st.chat_message('assistant', avatar=AVATAR_ASSISTANT):
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
