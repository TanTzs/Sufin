import os
import uuid
import html as _html
import streamlit as st
from dotenv import load_dotenv
from datetime import date, timedelta
from langchain_core.messages import HumanMessage, SystemMessage
from agent import build_agent
from trading_agent.adapter import run_analysis

load_dotenv()

st.set_page_config(
    page_title="Sufin · 金融智能平台",
    page_icon="⚡",
    layout="wide",
)

st.markdown("""
<style>
header[data-testid="stHeader"] {
    background: #f4f7fa !important;
    border-bottom: 1px solid #e2e8f0 !important;
    box-shadow: none !important;
}
header[data-testid="stHeader"] * { color: #64748b !important; }
.stDeployButton { display: none !important; }
footer { display: none !important; }

.stApp { background: #f4f7fa; }
.block-container {
    padding-top: 3rem !important;
    padding-bottom: 5rem !important;
    max-width: 900px !important;
}

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
[data-testid="stSidebar"] [data-baseweb="select"] * { color: #a8c4d8 !important; }
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
    margin-bottom: 1rem;
    display: block;
}

/* ── 落地页 ── */
.landing-hero {
    text-align: center;
    padding: 1rem 0 2.5rem 0;
}
.landing-brand {
    font-size: 3rem;
    font-weight: 900;
    letter-spacing: 0.02em;
    background: linear-gradient(110deg, #1e3a8a 0%, #4338ca 50%, #0e7490 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.15;
    margin-bottom: 0.5rem;
}
.landing-sub {
    font-size: 0.9rem;
    color: #94a3b8;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0;
}
.agent-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    padding: 2rem 1.8rem 1.6rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    margin-bottom: 1.2rem;
    height: 100%;
}
.agent-card-sufin  { border-top: 4px solid #2563eb; }
.agent-card-trading { border-top: 4px solid #d97706; }
.card-icon  { font-size: 2.4rem; margin-bottom: 0.7rem; }
.card-name  { font-size: 1.25rem; font-weight: 700; color: #0f172a; margin-bottom: 0.35rem; }
.card-desc  { font-size: 0.86rem; color: #64748b; margin-bottom: 1.2rem; line-height: 1.5; }
.card-tags  { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 1.4rem; }
.tag {
    font-size: 0.73rem;
    padding: 3px 10px;
    border-radius: 20px;
    font-weight: 500;
}
.tag-blue   { background: #eff6ff; color: #1d4ed8; }
.tag-amber  { background: #fffbeb; color: #b45309; }
.tag-green  { background: #f0fdf4; color: #15803d; }
.tag-purple { background: #f5f3ff; color: #6d28d9; }

/* ── Agent 界面标题 ── */
.sufin-title {
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: 0.02em;
    background: linear-gradient(110deg, #1e3a8a 0%, #4338ca 55%, #0e7490 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
    margin-bottom: 0.3rem;
}
.ta-title {
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: 0.02em;
    background: linear-gradient(110deg, #b45309 0%, #d97706 50%, #92400e 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
    margin-bottom: 0.3rem;
}
.page-subtitle {
    font-size: 0.76rem;
    color: #94a3b8;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-bottom: 2rem;
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

/* ── 聊天输入 ── */
[data-testid="stBottom"] {
    background: linear-gradient(0deg, #f4f7fa 70%, transparent) !important;
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

hr { border-color: rgba(255,255,255,0.08) !important; }

::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #f4f7fa; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
</style>
""", unsafe_allow_html=True)


# ── 缓存 Agent ─────────────────────────────────────────────────────────────────
@st.cache_resource
def get_sufin_agent():
    api_key = os.getenv('DEEPSEEK_API_KEY') or st.secrets.get('DEEPSEEK_API_KEY', '')
    return build_agent(api_key)


# ── Session State ─────────────────────────────────────────────────────────────
def _new_tid():
    return str(uuid.uuid4())

if 'selected_agent' not in st.session_state:
    st.session_state['selected_agent'] = None

if 'threads' not in st.session_state:
    tid = _new_tid()
    st.session_state['threads'] = {tid: {'name': '新对话 1', 'display': []}}
    st.session_state['thread_order'] = [tid]
    st.session_state['current_thread'] = tid

if 'ta_result' not in st.session_state:
    st.session_state['ta_result'] = None

SUFIN_EXAMPLES = [
    "帮我分析苹果(AAPL)、微软(MSFT)、英伟达(NVDA) 2026年的美股组合",
    "分析平安银行(000001)、贵州茅台(600519)、宁德时代(300750) 2026年A股组合",
    "AAPL、GOOGL、META、AMZN 四只科技股2026年怎么配置最优？",
    "帮我看看招商银行(600036)和中国平安(601318)两只股票2026年的最优组合",
]

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

    if st.session_state['selected_agent'] is not None:
        if st.button("← 切换智能体", use_container_width=True):
            st.session_state['selected_agent'] = None
            st.rerun()
        st.divider()

        if st.session_state['selected_agent'] == 'Sufin':
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
            for ex in SUFIN_EXAMPLES:
                if st.button(ex, use_container_width=True, key=f"ex_{ex[:15]}"):
                    st.session_state['pending'] = ex
                    st.rerun()

            st.divider()
            st.markdown("**使用提示**")
            st.markdown("- A股：输入6位股票代码或股票名称\n- 美股：输入 Ticker 符号（如 AAPL）\n- 可直接用自然语言描述，无需填表")

        else:  # TradingAgent
            st.markdown("**模型配置**")
            st.selectbox("LLM 提供商", ["deepseek", "openai", "anthropic", "qwen"], key="ta_provider")
            st.text_input("深度思考模型", placeholder="留空使用默认", key="ta_deep_model")
            st.text_input("快速推理模型", placeholder="留空使用默认", key="ta_quick_model")
            st.divider()
            st.markdown("**启用分析师**")
            st.multiselect(
                "分析维度",
                ["market", "fundamentals", "news", "social"],
                default=["market", "fundamentals", "news", "social"],
                key="ta_analysts",
            )
            st.divider()
            st.markdown("**说明**")
            st.markdown(
                "- 支持 **A股**（6位代码）、港股、美股\n"
                "- 分析耗时约 **2–5 分钟**\n"
                "- deepseek 使用 `DEEPSEEK_API_KEY`\n"
                "- 结果仅供参考，不构成投资建议"
            )


# ── 主区域 ────────────────────────────────────────────────────────────────────
agent = st.session_state['selected_agent']

if agent is None:
    # ════════════════════════════════════════════════
    #  落地页：选择 Agent
    # ════════════════════════════════════════════════
    st.markdown('''
<div class="landing-hero">
    <div class="landing-brand">Sufin 金融智能平台</div>
    <div class="landing-sub">选择您需要的智能体，开始分析</div>
</div>
''', unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('''
<div class="agent-card agent-card-sufin">
    <div class="card-icon">⚡</div>
    <div class="card-name">Sufin Agent</div>
    <div class="card-desc">对话式投资组合助手，用自然语言描述需求，智能体自动完成数据下载与组合优化。</div>
    <div class="card-tags">
        <span class="tag tag-blue">A股 & 美股</span>
        <span class="tag tag-blue">Markowitz 优化</span>
        <span class="tag tag-green">实时联网搜索</span>
        <span class="tag tag-purple">多轮对话</span>
    </div>
</div>
''', unsafe_allow_html=True)
        if st.button("开始使用 Sufin Agent →", use_container_width=True, key="select_sufin"):
            st.session_state['selected_agent'] = 'Sufin'
            st.rerun()

    with col2:
        st.markdown('''
<div class="agent-card agent-card-trading">
    <div class="card-icon">📊</div>
    <div class="card-name">TradingAgent CN</div>
    <div class="card-desc">多智能体深度分析框架，由基本面、技术、新闻、情绪四路分析师协作，多轮辩论后输出决策。</div>
    <div class="card-tags">
        <span class="tag tag-amber">A股专项增强</span>
        <span class="tag tag-amber">多维度分析</span>
        <span class="tag tag-green">DeepSeek 支持</span>
        <span class="tag tag-purple">辩论决策机制</span>
    </div>
</div>
''', unsafe_allow_html=True)
        if st.button("开始使用 TradingAgent CN →", use_container_width=True, key="select_trading"):
            st.session_state['selected_agent'] = 'TradingAgent'
            st.rerun()

elif agent == 'Sufin':
    # ════════════════════════════════════════════════
    #  Sufin Agent 界面
    # ════════════════════════════════════════════════
    st.markdown('<div class="sufin-title">Sufin Agent</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Portfolio Intelligence · Powered by DeepSeek · 仅供参考，不构成投资建议</div>', unsafe_allow_html=True)

    current_tid    = st.session_state['current_thread']
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
                    sufin = get_sufin_agent()
                    new_messages = []
                    if len(current_thread['display']) == 1:
                        new_messages.append(
                            SystemMessage(content=f"今天是 {date.today().strftime('%Y年%m月%d日')}。")
                        )
                    new_messages.append(HumanMessage(content=prompt))
                    result = sufin.invoke(
                        {'messages': new_messages},
                        config={'configurable': {'thread_id': current_tid}},
                    )
                    answer = result['messages'][-1].content
                except Exception as e:
                    answer = f'分析出错：{e}'
            st.markdown(answer)

        current_thread['display'].append({'role': 'assistant', 'content': answer})

else:
    # ════════════════════════════════════════════════
    #  TradingAgent CN 界面
    # ════════════════════════════════════════════════
    st.markdown('<div class="ta-title">TradingAgent CN</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Multi-Agent Deep Analysis · A股增强 · 仅供参考，不构成投资建议</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        ta_ticker = st.text_input(
            "股票代码",
            placeholder="A股：600519  港股：0700.HK  美股：NVDA",
            key="ta_ticker",
        )
    with col2:
        ta_date = st.date_input(
            "分析日期",
            value=date.today() - timedelta(days=1),
            max_value=date.today() - timedelta(days=1),
            key="ta_date",
        )
    with col3:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        run_btn = st.button("🔍 开始分析", use_container_width=True, key="ta_run")

    if run_btn:
        if not ta_ticker.strip():
            st.warning("请输入股票代码")
        else:
            st.session_state['ta_result'] = None
            analysts = st.session_state.get('ta_analysts') or ["market", "fundamentals", "news", "social"]
            with st.spinner(f"多智能体分析 {ta_ticker.strip()} 中，约需 2–5 分钟，请耐心等待…"):
                result = run_analysis(
                    ticker=ta_ticker.strip(),
                    analysis_date=str(ta_date),
                    provider=st.session_state.get('ta_provider', 'deepseek'),
                    deep_model=st.session_state.get('ta_deep_model', ''),
                    quick_model=st.session_state.get('ta_quick_model', ''),
                    analysts=analysts,
                )
            st.session_state['ta_result'] = result

    if st.session_state.get('ta_result'):
        with st.chat_message('assistant', avatar=AVATAR_ASSISTANT):
            st.markdown(st.session_state['ta_result'])
