"""临时脚本：生成 case_portfolio_langchain.ipynb，规避手写 JSON 转义问题。"""
import json, pathlib, textwrap

def md(source: str, cell_id: str) -> dict:
    return {"cell_type": "markdown", "id": cell_id, "metadata": {},
            "source": source.splitlines(keepends=True)}

def code(source: str, cell_id: str) -> dict:
    return {"cell_type": "code", "execution_count": None, "id": cell_id,
            "metadata": {}, "outputs": [],
            "source": source.splitlines(keepends=True)}

# ─────────────────────────────────────────────────────────────────────────────
cells = []

# ── Cell 1: 封面 ─────────────────────────────────────────────────────────────
cells.append(md("""\
# 📈 金融智能体设计案例
## 当马科维茨遭遇现实：一个量化研究员的蜕变之路

> *上海财经大学《金融智能体设计》课程教学案例*
> *核心方法：Fan, Liao & Mincheva (2012) · JASA | 智能体框架：LangChain*

---

### 🎯 学习目标

跟着这个故事走完一遍，你将掌握：

| # | 知识点 | 核心内容 |
|:---:|:---|:---|
| 1 | **LangChain Tool** | 用 `@tool` 装饰器把 Python 函数变成 AI 可调用的工具 |
| 2 | **LangChain Agent** | 用 `create_agent` 组装「大脑 + 工具」的完整智能体 |
| 3 | **马科维茨理论** | 均值-方差优化的原理、代码实现与局限性 |
| 4 | **高维协方差难题** | 为什么股票多了之后，经典方法会失效？ |
| 5 | **Fan et al. (2012)** | 用高频数据突破低维瓶颈——前沿方法的故事 |

---

> 📖 **阅读指南**：本案例采用「边听故事，边跑代码」的形式。
> 请**按顺序运行每个代码格**，感受主人公的命运起伏，同时理解每一行代码背后的设计逻辑。
""", "cell-title"))

# ── Cell 2: 人物 ─────────────────────────────────────────────────────────────
cells.append(md("""\
## 🎭 登场人物

| 人物 | 身份 | 性格 |
|:---|:---|:---|
| **陈天明** | 上财金融学博士，鼎盛资本量化研究员，本故事的主角 | 年轻气盛，相信数学的力量，不撞南墙不回头 |
| **林总** | 鼎盛资本投资总监，陈天明的直属上司 | 表面温文尔雅，内心如同钢铁，每一句话都算过利息 |
| **苏阿姨** | 鼎盛资本最大个人客户，5000万委托人 | 做过实业，见过风浪，雷厉风行，不容一点马虎 |
| **张教授** | 上财统计学院教授，陈天明的博士导师 | 深藏功与名，关键时刻一句话，价值十年功 |
""", "cell-characters"))

# ── Cell 3: 第一章故事 ───────────────────────────────────────────────────────
cells.append(md("""\
---
# 第一章：意气风发
### 2023年1月，上海·陆家嘴，鼎盛资本22楼

上海的冬天总是阴冷而潮湿，灰色的云压得很低，连东方明珠都只剩下一个模糊的轮廓。

但这些，陈天明完全顾不上看。

他的眼睛死死盯着两块显示器，屏幕的蓝白光打在眼镜片上。键盘噼啪声断断续续，最后在一阵急促的敲击后，戛然而止。

```
智能体初始化完成。
已注册工具: ['download_stock_data', 'markowitz_optimize']
```

**搞定了。**

陈天明靠回椅背，长出一口气。三个月，他把博士论文里关于马科维茨投资组合的全套理论，硬生生地用 LangChain 封装成了一个 AI 智能顾问系统。给它一句自然语言，它能自己下载数据、优化权重、输出报告——**全程不需要人工干预**。

「天明。」

林总的声音从身后传来，没有任何预兆，却让陈天明猛地绷直了背。他转过头——林总站在那里，西装笔挺，手里端着一杯咖啡，眼神里什么都没有。

「苏阿姨那边，谈好了。」林总顿了一下，「五千万，全权委托给你的系统。」

陈天明愣了一秒，随即脑子里的某根弦开始紧绷。

「年底，」林总抿了一口咖啡，「如果业绩不达预期……你自己想想后果。」

办公室里的空调低鸣着，陈天明感觉自己的手心有点凉。

五千万。这不是模拟盘，这是真实的钱，是苏阿姨半辈子的心血。

---

> 🎓 **同学们注意！**
> 接下来，就是陈天明当时搭建的 LangChain 智能体系统。
> 让我们跟着他的视角，从零开始理解 Agent 的设计逻辑。
""", "cell-ch1-story"))

# ── Cell 4: LangChain 概念 ───────────────────────────────────────────────────
cells.append(md("""\
## 📚 LangChain Agent 核心设计逻辑

陈天明在白板上画了一张架构图，用来向林总解释这套系统：

```
┌─────────────────────────────────────────────────────────┐
│                   用户的自然语言问题                       │
│     「帮我分析苹果、微软、英伟达三只股票的最优配置」          │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                   LLM 大模型（大脑）                       │
│    思考：我需要先下载数据，再做优化。调用哪个工具？           │
└──────────┬──────────────────────────────────────────────┘
           │ 决策：调用 Tool
     ┌─────▼─────┐         ┌──────────────────┐
     │  Tool 1   │         │     Tool 2       │
     │ 下载股票  │────────>│  马科维茨优化    │
     │   数据    │         │  输出最优权重    │
     └───────────┘         └────────┬─────────┘
                                    │ 结果
                                    ▼
┌─────────────────────────────────────────────────────────┐
│             LLM 综合工具结果，生成投资建议报告              │
└─────────────────────────────────────────────────────────┘
```

### 一句话理解 Agent

$$\\text{Agent} = \\text{LLM（大脑）} + \\text{Tools（工具集）}$$

- **LLM** 负责「想」：理解用户意图，决定调用哪个工具、传什么参数
- **Tool** 负责「做」：执行具体的计算、数据获取等操作
- **Agent** 负责「连」：把大脑和工具串联起来，形成完整的推理-行动循环

### 什么是 Tool？

Tool 就是一个加了 `@tool` 装饰器的普通 Python 函数。关键在三点：

| 要素 | 作用 | 举例 |
|:---|:---|:---|
| **函数签名** | 告诉 LLM 需要哪些参数及其类型 | `stock_codes: str, market: str` |
| **Docstring** | 告诉 LLM 工具的用途、参数含义、何时调用 | `'''下载股票历史行情数据...'''` |
| **返回值** | 工具执行结果，原文发回给 LLM 做下一步判断 | JSON 字符串 |

> ⚠️ **特别注意**：Docstring 写得好不好，直接决定 LLM 能不能正确使用你的工具！
> 这是 Agent 开发中最容易被忽视，却最重要的地方。
""", "cell-langchain-concepts"))

# ── Cell 5: 环境准备 ─────────────────────────────────────────────────────────
cells.append(code("""\
# ── 环境准备 ──────────────────────────────────────────────
# 如果缺少依赖，先运行：
# pip install langchain langchain-deepseek yfinance scipy python-dotenv

import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from dotenv import load_dotenv
from scipy.optimize import minimize
import yfinance as yf

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_deepseek import ChatDeepSeek
from langchain.agents import create_agent

matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

print('✅ 所有依赖导入成功')
""", "cell-imports"))

# ── Cell 6: LLM 初始化 ───────────────────────────────────────────────────────
cells.append(code("""\
# ── 初始化大模型（LLM）──────────────────────────────────────
# 陈天明选择了 DeepSeek——国内访问稳定、推理能力强

load_dotenv()  # 从 .env 文件读取 DEEPSEEK_API_KEY

llm = ChatDeepSeek(
    model='deepseek-chat',
    api_key=os.getenv('DEEPSEEK_API_KEY'),
    temperature=0,   # temperature=0：确定性输出，金融分析需要可复现
)

print(f'✅ LLM 初始化成功，模型：{llm.model_name}')
""", "cell-llm-init"))

# ── Cell 7: Tool 说明 ────────────────────────────────────────────────────────
cells.append(md("""\
## 🔧 第一步：定义工具（Tool）——Agent 的「手」

陈天明为系统设计了两个工具，分别负责「数据获取」和「投资组合优化」。

注意观察 `@tool` 装饰器和 **Docstring 的写法**——这是 LLM 理解工具的唯一来源。
""", "cell-tool-design"))

# ── Cell 8: Tool 1 ───────────────────────────────────────────────────────────
cells.append(code("""\
# ── 工具1：股票数据下载 ────────────────────────────────────
# 全局状态：用于在工具之间共享下载好的数据
_portfolio_data: dict = {}


def _to_yahoo(code: str) -> str:
    '''将6位A股代码转为 Yahoo Finance 格式。'''
    if code.startswith('6'):        return f'{code}.SS'
    if code.startswith(('0', '3')): return f'{code}.SZ'
    return code


def _download_raw(codes: list, start_date: str, end_date: str):
    '''yfinance 下载收盘价并计算日收益率。'''
    start = pd.to_datetime(start_date, format='%Y%m%d').strftime('%Y-%m-%d')
    end   = pd.to_datetime(end_date,   format='%Y%m%d').strftime('%Y-%m-%d')
    raw   = yf.download(codes, start=start, end=end, progress=False, auto_adjust=True)
    if raw.empty:
        return json.dumps({'错误': 'yfinance 返回空数据，请检查代码和日期'}, ensure_ascii=False)
    if isinstance(raw.columns, pd.MultiIndex):
        close = raw['Close']
    else:
        close = raw[['Close']].rename(columns={'Close': codes[0]})
    if isinstance(close, pd.Series):
        close = close.to_frame(name=codes[0])
    close.columns = [str(c) for c in close.columns]
    return close.pct_change().dropna()


#           ↓↓↓ @tool 装饰器：把普通函数变成 AI 可调用的工具 ↓↓↓
@tool
def download_stock_data(
    stock_codes: str,
    market: str = 'A',
    start_date: str = '20240101',
    end_date: str = '20241231',
) -> str:
    '''下载股票历史行情数据并计算日收益率，支持 A 股和美股。

    Args:
        stock_codes: 股票代码，多只用英文逗号分隔。
                     A股示例：000001,600519,300750
                     美股示例：AAPL,MSFT,GOOGL
        market: 市场选择，A 表示 A 股，US 表示美股，默认 A
        start_date: 起始日期，格式 YYYYMMDD，默认 20240101
        end_date: 结束日期，格式 YYYYMMDD，默认 20241231

    Returns:
        数据下载状态及基本统计摘要（JSON 字符串）
    '''
    codes = [c.strip() for c in stock_codes.split(',')]
    if market.upper() == 'A':
        yahoo_codes = [_to_yahoo(c) for c in codes]
        returns_df = _download_raw(yahoo_codes, start_date, end_date)
        if isinstance(returns_df, pd.DataFrame):
            returns_df = returns_df.rename(columns=dict(zip(yahoo_codes, codes)))
    else:
        returns_df = _download_raw(codes, start_date, end_date)

    if isinstance(returns_df, str):   # 错误时返回错误消息字符串
        return returns_df

    _portfolio_data['returns'] = returns_df
    _portfolio_data['stocks']  = codes
    _portfolio_data['market']  = market.upper()

    summary = {
        '状态': '下载成功',
        '市场': 'A股' if market.upper() == 'A' else '美股',
        '股票代码': codes,
        '有效交易日数': len(returns_df),
        '日期范围': f'{str(returns_df.index[0])} 至 {str(returns_df.index[-1])}',
        '各股年化收益率（估算）': {code: f'{returns_df[code].mean() * 252:.2%}' for code in codes},
        '提示': '数据已保存，请调用 markowitz_optimize 进行优化',
    }
    return json.dumps(summary, ensure_ascii=False, indent=2)


print('✅ Tool 1 [download_stock_data] 注册成功')
print('   Docstring 首行：', download_stock_data.description[:55], '...')
""", "cell-tool1"))

# ── Cell 9: Tool 2 ───────────────────────────────────────────────────────────
cells.append(code("""\
# ── 工具2：马科维茨投资组合优化 ───────────────────────────────

@tool
def markowitz_optimize(risk_free_rate: float = 0.02) -> str:
    '''对已下载的股票数据进行马科维茨投资组合优化。

    同时求解两种最优组合：
    - 最大夏普比率组合：风险调整后收益最优，适合积极型投资者
    - 最小方差组合：波动率最低，适合保守型投资者

    请先调用 download_stock_data 下载数据后再使用此工具。

    Args:
        risk_free_rate: 年化无风险利率，默认 0.02（2%）。美股建议 0.045。

    Returns:
        两种最优组合的权重及风险收益指标（JSON 字符串）
    '''
    if 'returns' not in _portfolio_data:
        return '错误：请先调用 download_stock_data 下载数据。'

    returns_df = _portfolio_data['returns']
    stocks     = _portfolio_data['stocks']
    n          = len(stocks)

    # ── 核心数学：均值向量 + 协方差矩阵 ──────────────────────
    mean_ret = returns_df.mean().values           # 日均收益率向量
    cov_mat  = returns_df.cov().values * 252      # 年化协方差矩阵
    # ─────────────────────────────────────────────────────────

    constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
    bounds = [(0.0, 1.0)] * n
    w0 = np.ones(n) / n

    def neg_sharpe(w):
        ret = float(np.dot(w, mean_ret) * 252)
        vol = float(np.sqrt(w @ cov_mat @ w))
        return -(ret - risk_free_rate) / vol

    def port_vol(w):
        return float(np.sqrt(w @ cov_mat @ w))

    res_sr = minimize(neg_sharpe, w0, method='SLSQP', bounds=bounds, constraints=constraints)
    res_mv = minimize(port_vol,   w0, method='SLSQP', bounds=bounds, constraints=constraints)

    def stats(w):
        ret = float(np.dot(w, mean_ret) * 252)
        vol = float(np.sqrt(w @ cov_mat @ w))
        return ret, vol, (ret - risk_free_rate) / vol

    sr_ret, sr_vol, sr_sharpe = stats(res_sr.x)
    mv_ret, mv_vol, mv_sharpe = stats(res_mv.x)

    result = {
        '最大夏普比率组合（激进型）': {
            '权重配置': {stocks[i]: f'{res_sr.x[i]:.2%}' for i in range(n)},
            '年化预期收益': f'{sr_ret:.2%}',
            '年化波动率': f'{sr_vol:.2%}',
            '夏普比率': round(sr_sharpe, 4),
        },
        '最小方差组合（保守型）': {
            '权重配置': {stocks[i]: f'{res_mv.x[i]:.2%}' for i in range(n)},
            '年化预期收益': f'{mv_ret:.2%}',
            '年化波动率': f'{mv_vol:.2%}',
            '夏普比率': round(mv_sharpe, 4),
        },
        '参数说明': f'无风险利率 {risk_free_rate:.1%}，基于 {len(returns_df)} 个交易日历史数据',
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


print('✅ Tool 2 [markowitz_optimize] 注册成功')
""", "cell-tool2"))

# ── Cell 10: Agent 概念 ──────────────────────────────────────────────────────
cells.append(md("""\
## 🤖 第二步：构建智能体（Agent）——把大脑和工具连起来

工具定义好了，接下来是最关键的一步：**写系统提示词（System Prompt）并创建 Agent**。

System Prompt 就像给这个 AI 员工写的「岗位职责书」——告诉它：
1. 你的角色是什么
2. 遇到问题应该按什么流程处理
3. 有哪些注意事项

> **陈天明的体会**：写好 System Prompt，比写工具代码还难。
> 这是「与 AI 沟通」的艺术，也是 Agent 工程的核心竞争力。
""", "cell-agent-concepts"))

# ── Cell 11: 创建 Agent ──────────────────────────────────────────────────────
cells.append(code("""\
# ── 创建 Agent ────────────────────────────────────────────
SYSTEM_PROMPT = '''你是一位专业的股票投资顾问，擅长运用马科维茨现代投资组合理论进行资产配置分析，支持 A 股和美股两个市场。

工作流程（必须严格按顺序执行）：
1. 判断用户要分析的市场（A股 or 美股），调用 download_stock_data 时传入正确的 market 参数
   - A 股代码示例：000001, 600519, 300750
   - 美股代码示例：AAPL, MSFT, NVDA
2. 调用 markowitz_optimize 进行投资组合优化
   - A 股无风险利率用 0.02（国内国债）
   - 美股无风险利率用 0.045（美国国债）
3. 根据优化结果，从「风险收益特征」和「适合人群」两个维度给出配置建议

注意：本分析仅为教学演示，不构成实际投资建议。'''


#   ↓↓↓ create_agent：把 LLM + 工具列表 + 角色设定组装成完整的 Agent ↓↓↓
agent = create_agent(
    model=llm,
    tools=[download_stock_data, markowitz_optimize],
    system_prompt=SYSTEM_PROMPT,
)

print('✅ Agent 创建成功！')
print(f'   已注册工具：{[t.name for t in [download_stock_data, markowitz_optimize]]}')
""", "cell-create-agent"))

# ── Cell 12: 第一次运行 ──────────────────────────────────────────────────────
cells.append(md("""\
## 🚀 第三步：启动！陈天明的系统第一次运行

2023年2月，苹果春节后第一个交易周。

陈天明在会议室里，向苏阿姨做首次演示。他的手指停在回车键上，深呼吸。

「苏阿姨，您只需要用自然语言告诉系统您想怎么配置，它会自动完成所有分析。」

苏阿姨往后靠了靠，说：「那就分析我最熟悉的几只股票——贵州茅台、招商银行、宁德时代，2023年的A股组合，怎么配最好？」

陈天明按下了回车。

---

> ⌨️ **运行下方代码格，看看 Agent 如何一步步推理并给出答案！**
>
> Agent 内部的推理循环（ReAct pattern）：
> 1. LLM 读取问题 → 决定调用 `download_stock_data`
> 2. 工具执行 → 返回数据摘要给 LLM
> 3. LLM 决定调用 `markowitz_optimize`
> 4. 工具执行 → 返回优化结果给 LLM
> 5. LLM 综合所有信息 → 生成最终投资建议
""", "cell-first-run-intro"))

# ── Cell 13: 运行演示 ────────────────────────────────────────────────────────
cells.append(code("""\
# ── 调用 Agent ────────────────────────────────────────────
query = '''请帮我分析以下3只A股的投资组合配置：
- 贵州茅台（600519）
- 招商银行（600036）
- 宁德时代（300750）

使用2023年全年数据，进行马科维茨投资组合优化，并给出配置建议。'''

print('📨 用户提问：', query[:50], '...')
print('⏳ Agent 思考中（约20-40秒）...\\n')

result = agent.invoke({'messages': [HumanMessage(content=query)]})
print(result['messages'][-1].content)
""", "cell-first-run"))

# ── Cell 14: 第一章结尾 ──────────────────────────────────────────────────────
cells.append(md("""\
---

苏阿姨看完报告，点了点头：「不错，有模有样的。」

林总站在一旁，面无表情地说：「希望年底数字也这么好看。」

陈天明笑着送走了两位，转回办公桌，在笔记本上写下：

> *「2023年2月14日，系统上线。马科维茨，从未让我失望过。」*

---

他不知道，命运正在等待最好的时机，准备给他上一堂价值连城的课。
""", "cell-ch1-end"))

# ── Cell 15: 第二章 ──────────────────────────────────────────────────────────
cells.append(md("""\
---
# 第二章：晴天霹雳
### 2023年8月，上海，鼎盛资本

那个电话，是在一个周五下午4点17分打来的。

苏阿姨的声音从电话里传来，没有了上次演示时的和蔼：「天明，你给我解释一下，这个月的报告怎么是这个数字？」

陈天明盯着屏幕——**组合净值本月回撤 11.3%，超出预警线**。

他感觉血往脸上涌，耳朵嗡嗡的。

「苏阿姨，市场近期波动较大——」

「我不想听这些废话。」苏阿姨打断了他，「你那个 AI 系统，到底是怎么估的风险？」

电话挂断后，陈天明在空荡荡的办公室里坐了很久。

那天晚上，他没有回家。他把近半年的数据、回测结果、协方差矩阵的每一个参数，重新翻了一遍。

凌晨两点，他终于意识到了问题所在。

---

## 问题出在哪里？——高维协方差矩阵的「维度诅咒」

事情的起因，要从他 8 月初做的一个决定说起。

苏阿姨想要更分散的配置，于是陈天明把股票池从 **10 只** 扩大到了 **50 只**。

这在理论上完全合理——更多资产，更好的分散化。

但他忽略了一个关键问题：**协方差矩阵的估计质量，随着维度的增加而急剧下降。**

马科维茨优化的核心，是这个 $p \\times p$ 的协方差矩阵 $\\hat{\\Sigma}$：

$$\\hat{\\Sigma} = \\frac{1}{T-1} \\sum_{t=1}^{T} (r_t - \\bar{r})(r_t - \\bar{r})^\\top$$

其中 $p$ 是股票数量，$T$ 是观测天数（通常是 252 个交易日/年）。

当 $p = 50$，$T = 252$ 时：

- 参数数量：$p(p+1)/2 = 1275$ 个协方差参数
- 但观测数只有 252 个——**严重欠定**！
- 更糟的是，当 $p > T$ 时，**样本协方差矩阵直接变成奇异矩阵，无法求逆！**

下面，让我们用数据亲眼看看这个「维度诅咒」有多可怕：
""", "cell-ch2-story"))

# ── Cell 16: 协方差矩阵演示 ──────────────────────────────────────────────────
cells.append(code("""\
# ── 演示：高维协方差矩阵的「维度诅咒」─────────────────────────
# 陈天明当晚重现了这个实验，看到结果后，他手抖了。

np.random.seed(42)
T = 252   # 固定观测期：一年的交易日

dimensions   = [5, 10, 20, 50, 100, 200]
cond_numbers = []
ranks        = []

print(f'固定观测期 T = {T} 个交易日（约1年）\\n')
print(f'{"股票数 p":>8}  {"p/T":>6}  {"条件数":>14}  {"矩阵秩":>8}  {"是否满秩":>8}')
print('-' * 55)

for p in dimensions:
    R         = np.random.randn(T, p) * 0.01
    Sigma_hat = np.cov(R.T)
    cond      = np.linalg.cond(Sigma_hat)
    rank      = np.linalg.matrix_rank(Sigma_hat)
    full_rank = (rank == p)

    cond_numbers.append(cond)
    ranks.append(rank)

    flag = '' if full_rank else '  <- 💀 奇异！'
    print(f'{p:>8}  {p/T:>6.3f}  {cond:>14.1f}  {rank:>8}  {str(full_rank):>8}{flag}')

print('\\n📊 结论：')
print('  当 p 从5增加到200，条件数从百量级爆炸到亿量级以上')
print('  当 p >= T，矩阵秩 < p，变成奇异矩阵——马科维茨优化彻底崩溃！')
""", "cell-cov-demo"))

# ── Cell 17: 可视化 ──────────────────────────────────────────────────────────
cells.append(code("""\
# ── 可视化：条件数随维度的爆炸式增长 ─────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

# 左图：条件数（对数坐标）
axes[0].semilogy(dimensions, cond_numbers, 'o-', color='#E74C3C', linewidth=2, markersize=8)
axes[0].set_xlabel('股票数量 p', fontsize=12)
axes[0].set_ylabel('协方差矩阵条件数（对数）', fontsize=11)
axes[0].set_title('条件数随维度爆炸式增长', fontsize=13, fontweight='bold')
axes[0].axvline(x=T, color='gray', linestyle='--', alpha=0.7, label=f'T={T}（奇异临界）')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# 右图：有效秩比例
rank_ratio = [r / p for r, p in zip(ranks, dimensions)]
bar_colors = ['#27AE60' if r == 1.0 else '#E74C3C' for r in rank_ratio]
axes[1].bar(range(len(dimensions)), rank_ratio, color=bar_colors, alpha=0.8)
axes[1].set_xticks(range(len(dimensions)))
axes[1].set_xticklabels([str(d) for d in dimensions])
axes[1].set_xlabel('股票数量 p', fontsize=12)
axes[1].set_ylabel('有效秩 / p（越低越糟糕）', fontsize=11)
axes[1].set_title('矩阵秩随维度衰减', fontsize=13, fontweight='bold')
axes[1].axhline(y=1.0, color='green', linestyle='--', alpha=0.5, label='满秩（理想）')
axes[1].legend()
axes[1].grid(True, alpha=0.3, axis='y')

plt.suptitle('高维协方差矩阵的「维度诅咒」——马科维茨的软肋', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.show()

print('\\n陈天明盯着这张图，盯了很久很久。')
print('「我加了50只股票，以为是分散化，实际上是在用一个残缺的协方差矩阵做优化...」')
""", "cell-cov-plot"))

# ── Cell 18: 第三章 ──────────────────────────────────────────────────────────
cells.append(md("""\
---
# 第三章：绝处逢生
### 2023年9月，上财图书馆，深夜

林总那边的压力越来越大。苏阿姨的代理律师已经发来了一封措辞严峻的邮件。

陈天明请了年假，把自己关在上财图书馆里。

他知道，真正的问题不是市场，而是**协方差矩阵的估计**。样本协方差矩阵在高维情形下，就像一张被撑破了的网——洞越来越多，鱼全漏走了。

他翻遍了所有他能找到的高维统计文献，手机屏幕的光在黑暗里格外刺眼。

凌晨三点，他点开了一篇2012年发表在 *Journal of the American Statistical Association* 的论文：

> **Fan, J., Liao, Y., & Mincheva, M. (2012).**
> *Vast Volatility Matrix Estimation Using High-Frequency Data for Portfolio Selection.*
> **Journal of the American Statistical Association, 107(497), 412–428.**

他读到摘要的第二段，身体突然僵住了。

---

## 📄 Fan et al. (2012) 的核心思想

### 问题的根源：每天只有1个数据点

传统做法用**日频收益率**：一年只有 252 个数据点。
当股票数 $p = 50$，样本协方差的估计误差以 $\\mathcal{O}(p/T)$ 的速率积累，
$p/T = 50/252 \\approx 0.2$，这个误差会被优化器无限放大——**垃圾进，垃圾出**。

### 解决方案：用高频数据「制造」更多观测

Fan et al. 的洞见是：**如果我们用5分钟高频数据呢？**

| 数据频率 | 每天观测数 | 一年总观测数 | 相当于日频多少年 |
|:---:|:---:|:---:|:---:|
| 日频 | 1 | **252** | 1 年 |
| 5分钟 | 48 | **12,096** | 48 年！ |
| 1分钟 | 240 | **60,480** | 240 年！ |

更多的观测，意味着更精确的协方差矩阵估计。

### 技术核心：因子分解 + 稀疏化（POET 方法）

高频数据引入了新问题：**微观结构噪声**（买卖价差、报价误差等）。

Fan et al. 提出了优雅的两步分解，将协方差矩阵写成：

$$\\Sigma = \\underbrace{\\mathbf{B} \\Lambda \\mathbf{B}^\\top}_{\\text{系统性风险（低秩部分）}} + \\underbrace{\\Sigma_u}_{\\text{特质风险（稀疏部分）}}$$

| 分量 | 金融含义 | 如何估计 |
|:---|:---|:---|
| $\\mathbf{B} \\Lambda \\mathbf{B}^\\top$ | 市场、行业因子带来的**共同**波动 | 高频已实现协方差 + 主成分分析 |
| $\\Sigma_u$ | 各股特有、互不相关的**特质**风险 | 自适应阈值化（去除噪声） |

这个方法后来被称为 **POET**（Principal Orthogonal complEment Thresholding）。

### 直觉理解

想象整个A股市场，每只股票的波动都受两类力量驱动：

1. 🌍 **系统性力量**：宏观政策、板块轮动——大家一起涨跌（$\\mathbf{B} \\Lambda \\mathbf{B}^\\top$ 捕捉）
2. 🏢 **个股特质**：公司公告、换管理层——只影响这一只（$\\Sigma_u$ 捕捉）

POET 把这两部分精确分开，分别用最适合的方法来估计，从根本上解决了高维协方差矩阵的估计问题。
""", "cell-ch3-story"))

# ── Cell 19: 高频数据直觉 ────────────────────────────────────────────────────
cells.append(code("""\
# ── 直观演示：观测量对协方差估计精度的影响 ──────────────────
# 用蒙特卡洛模拟展示：T 越大，估计越准

np.random.seed(2024)
p = 20   # 固定股票数 = 20

# 构造「真实」协方差矩阵（3因子结构）
B      = np.random.randn(p, 3) * 0.05
Lambda = np.diag([0.04, 0.02, 0.01])
Sigma_u    = np.diag(np.random.uniform(0.0001, 0.0009, p))
Sigma_true = B @ Lambda @ B.T + Sigma_u

# 不同数据频率对应的样本量
sample_sizes = [
    ('日频  1年',  252),
    ('日频  3年',  756),
    ('5分钟 1年',  252 * 48),
    ('1分钟 1年',  252 * 240),
]

print(f'股票数量 p = {p}，比较不同数据频率下的协方差估计误差（100次蒙特卡洛均值）\\n')
print(f'{"数据频率":>12}  {"观测数 T":>10}  {"p/T":>7}  {"相对误差（Frobenius）":>22}')
print('-' * 60)

for label, T_eff in sample_sizes:
    errors = []
    for _ in range(100):
        R       = np.random.multivariate_normal(np.zeros(p), Sigma_true, T_eff)
        Sig_hat = np.cov(R.T)
        err = np.linalg.norm(Sig_hat - Sigma_true, 'fro') / np.linalg.norm(Sigma_true, 'fro')
        errors.append(err)
    mean_err = np.mean(errors)
    bar = '█' * int(mean_err * 50)
    print(f'{label:>12}  {T_eff:>10,}  {p/T_eff:>7.4f}  {mean_err:>8.4f}  {bar}')

print('\\n💡 结论：观测越多（高频数据），协方差矩阵估计越准确！')
print('   Fan et al. (2012) 将高频数据系统性地引入投资组合优化——这是关键贡献。')
""", "cell-hf-intuition"))

# ── Cell 20: 第三章结尾 ──────────────────────────────────────────────────────
cells.append(md("""\
---

图书馆的灯快关了，保安在走廊里催促。

陈天明把手机屏幕截图发给了一个人：张教授。消息发出的瞬间，已经是凌晨四点十二分。

他没想到，三分钟后，回复来了：

> *「这篇论文是 Fan 老师的经典之作。高频数据的核心是：用时间换空间。你找到正确方向了。加油。——张」*

陈天明收起手机，走出图书馆。夜风带着凉意，但他感觉心里热的。

---
""", "cell-ch3-end"))

# ── Cell 21: 第四章 ──────────────────────────────────────────────────────────
cells.append(md("""\
---
# 第四章：重建神殿
### 2023年10月，鼎盛资本

接下来的三周，陈天明几乎没有回家。

他要重新设计 Agent 系统——不只是修一个漏洞，而是**在原有架构上，加入一个全新的工具**：
一个基于 Fan et al. (2012) 方法的高频协方差矩阵估计工具。

新的系统架构：

```
                    用户问题（自然语言）
                           |
                    LLM 大模型（大脑）
               根据股票数量自动选择优化方法
                    /              \\
         p <= 20 只                p > 20 只
              |                        |
   markowitz_optimize      vast_volatility_optimize
   传统马科维茨（快）         POET 高频协方差（稳健）
```

关键设计决策：**让 LLM 根据问题的特征自动选择工具**——这正是 Agent 相比传统程序的核心优势。

> 🎓 **教学重点**：下面展示的新工具是一个「骨架设计」（Skeleton）。
> 完整的高频数据处理和 POET 算法实现，是后续课程的内容。
>
> 但请注意：**工具的「接口设计」和「Docstring」才是 Agent 开发的灵魂**——
> 正确描述工具的用途和适用场景，LLM 才能做出正确的调用决策。
""", "cell-ch4-story"))

# ── Cell 22: 新工具占位符 ────────────────────────────────────────────────────
cells.append(code("""\
# ── Tool 3（新）：Fan et al. (2012) 高频协方差估计工具 ────────
#
# 注意：这是一个精心设计的「骨架工具」
# 重点在于：
#   1. Docstring 的写法——告诉 LLM 何时选择这个工具（而非 markowitz）
#   2. 接口设计——参数如何设计才能让 LLM 正确传参
#   3. TODO 注释——展示完整实现的思路

@tool
def vast_volatility_optimize(
    risk_free_rate: float = 0.02,
    n_factors: int = 3,
) -> str:
    '''使用 Fan, Liao & Mincheva (2012) JASA 方法进行高维投资组合优化。

    当股票数量较多（通常 p > 20）时，传统马科维茨方法的样本协方差矩阵
    估计误差会急剧增大，导致优化结果失真。本工具采用高频数据与因子模型
    相结合的方式（POET 方法），在高维情形下显著提升协方差矩阵估计精度。

    适用场景：
    - 股票池规模较大（p > 20 只）
    - 需要在高波动市场中进行稳健的风险控制
    - 对传统马科维茨结果持怀疑态度时（如条件数过大）

    方法论（Fan et al., 2012, JASA）：
    - 使用高频日内数据（5分钟收益率）估计「已实现协方差矩阵」
    - 主成分分析提取系统性因子，分解 Sigma = B*Lambda*B' + Sigma_u
    - 对特质风险矩阵 Sigma_u 进行自适应阈值化（POET 核心步骤）
    - 基于改进后的协方差矩阵求解最大夏普比率组合

    请先调用 download_stock_data 下载低频数据（用于预期收益率估计）。

    Args:
        risk_free_rate: 年化无风险利率，默认 0.02（2%）。美股建议 0.045。
        n_factors: 提取的系统性因子数量，默认 3（市场、规模、价值三因子）。

    Returns:
        基于 POET 协方差估计的最优投资组合权重及风险指标（JSON 字符串）
    '''
    # =====================================================================
    # TODO：待实现以下步骤（下一阶段课程内容）
    # ---------------------------------------------------------------------
    # Step 1: 下载高频日内数据（5分钟 K 线）
    #         A 股: akshare.stock_zh_a_hist_min_em(symbol, period='5')
    #         美股: yfinance.download(ticker, interval='5m')
    #
    # Step 2: 计算「已实现协方差矩阵」
    #         对每个交易日 t，将日内5分钟收益率外积累加：
    #         Sigma_RC_t = sum_s  r_{t,s} @ r_{t,s}.T
    #         最终：Sigma_RC = (1/T) * sum_t Sigma_RC_t
    #
    # Step 3: 主成分分析（PCA）提取系统性因子
    #         eigenvalues, eigenvectors = np.linalg.eigh(Sigma_RC)
    #         取前 n_factors 个特征向量作为因子载荷 B
    #         Sigma_common = B @ diag(top_eigenvalues) @ B.T
    #         Sigma_u = Sigma_RC - Sigma_common
    #
    # Step 4: 自适应阈值化（POET 核心）
    #         对 Sigma_u 的非对角元素，低于阈值的置零（稀疏化）
    #         Sigma_POET = Sigma_common + threshold(Sigma_u)
    #
    # Step 5: 基于 Sigma_POET 求解最优权重（与 markowitz_optimize 相同逻辑）
    # =====================================================================

    return json.dumps({
        '状态': '此工具正在开发中，即将上线',
        '方法': 'Fan, Liao & Mincheva (2012) POET 方法',
        '参考论文': 'Vast Volatility Matrix Estimation Using High-Frequency Data for Portfolio Selection',
        '期刊': 'Journal of the American Statistical Association, 107(497), 412-428',
        '说明': '完整实现需要高频日内数据接口，下一阶段课程将带领大家完成此工具的开发！',
    }, ensure_ascii=False, indent=2)


print('✅ Tool 3 [vast_volatility_optimize] 骨架设计完成')
print('   Docstring 中明确了适用场景（p > 20），LLM 可据此自动选择工具')
""", "cell-new-tool"))

# ── Cell 23: 新 Agent ────────────────────────────────────────────────────────
cells.append(code("""\
# ── 重建 Agent：三工具新版本 ────────────────────────────────
NEW_SYSTEM_PROMPT = '''你是一位专业的量化投资顾问，擅长根据股票组合的规模和特征，
选择最适合的投资组合优化方法。

你有三个工具可以调用：
1. download_stock_data：下载股票低频（日频）历史行情数据
2. markowitz_optimize：传统马科维茨均值-方差优化（适合股票数 p <= 20 的小组合）
3. vast_volatility_optimize：Fan et al. (2012) 高频 POET 协方差估计法
   （适合股票数 p > 20 的大组合，或传统方法效果不佳时）

工作流程：
1. 调用 download_stock_data 下载数据
2. 根据股票数量判断优化方法：
   - p <= 20：调用 markowitz_optimize（传统方法，简单快速）
   - p > 20：调用 vast_volatility_optimize（高频方法，高维稳健）
3. 解读结果，从「风险收益特征」和「适合人群」两个维度给出配置建议

注意：本分析仅为教学演示，不构成实际投资建议。'''


new_agent = create_agent(
    model=llm,
    tools=[
        download_stock_data,
        markowitz_optimize,
        vast_volatility_optimize,   # <- 新增！高频协方差工具
    ],
    system_prompt=NEW_SYSTEM_PROMPT,
)

print('✅ 新版 Agent 创建成功！')
tool_names = [t.name for t in [download_stock_data, markowitz_optimize, vast_volatility_optimize]]
print(f'   已注册工具：{tool_names}')
print()
print('💡 设计亮点：System Prompt 明确了工具选择的业务逻辑')
print('   -> 当股票数 <= 20，LLM 会选择 markowitz_optimize')
print('   -> 当股票数 > 20，LLM 会自动切换到 vast_volatility_optimize')
""", "cell-new-agent"))

# ── Cell 24: 第五章 ──────────────────────────────────────────────────────────
cells.append(md("""\
---
# 第五章：涅槃重生
### 2023年12月，鼎盛资本会议室

苏阿姨坐在对面，表情依然严肃。林总坐在她旁边，捧着咖啡。

陈天明打开了他的笔记本，深吸一口气。

「苏阿姨，林总，今天我来汇报两件事：第一，8月的亏损，我已经找到了根本原因。第二，我们的系统已经完成了升级。」

接下来的二十分钟，他把一切都讲清楚了——维度诅咒、协方差矩阵的崩溃、Fan et al. 2012年的论文、POET 方法、新的三工具 Agent 架构。

苏阿姨没有打断他。等他说完，沉默了一会儿，然后说：

「你知道我为什么选鼎盛吗？不是因为他们从来不犯错。是因为他们犯了错，能搞清楚为什么犯、怎么不再犯。」

她顿了顿，「继续干。」

陈天明感到一股暖流涌上来，有点想笑，又有点想哭。

林总放下咖啡，拍了拍他的肩膀，什么都没说。

---

那天回去的路上，陈天明给张教授发了一条消息：

> *「教授，我把论文里的思路用在了 Agent 设计上。感谢您当时的指引。」*

张教授的回复来得很快：

> *「学以致用，这才是读书的意义。Fan 老师那篇文章，真正精彩的不是公式，是他对问题的定义。记住：好的研究，都是从真实的痛点出发的。——张」*

---
""", "cell-ch5-story"))

# ── Cell 25: 总结 ────────────────────────────────────────────────────────────
cells.append(md("""\
---
# 📚 课程总结

## LangChain Agent 设计的五条心法

| # | 原则 | 陈天明的教训 |
|:---:|:---|:---|
| 1 | **Docstring 是工具的灵魂** | 写清楚「用途、参数、适用场景」，LLM 才能正确调用 |
| 2 | **System Prompt 定义业务逻辑** | 何时用哪个工具，应在 System Prompt 中明确告知 LLM |
| 3 | **每个工具做单一事情** | `download` 和 `optimize` 分开，各司其职，便于组合 |
| 4 | **新需求 = 新增工具** | 不改原有工具，新增工具并更新 Agent 配置 |
| 5 | **错误信息要对 LLM 友好** | 工具出错时用自然语言解释原因，而非直接抛异常 |

## Fan et al. (2012) 的学术贡献

| 维度 | 传统马科维茨 | Fan et al. POET 方法 |
|:---|:---|:---|
| 数据 | 日频，252个观测/年 | 高频，12,096个观测/年（5分钟） |
| 高维问题 | p > T 时矩阵奇异 | 因子分解后 p/T_eff 极小，稳健估计 |
| 噪声处理 | 无处理 | POET 自适应阈值化去除微结构噪声 |
| 适用规模 | p < 20（小组合） | p 可达数百（大规模组合） |

## 代码架构速查

```python
from langchain_core.tools import tool
from langchain.agents import create_agent

# 1. 定义工具（关键：写好 Docstring！）
@tool
def my_tool(param: str) -> str:
    '''工具用途描述（LLM 的唯一学习来源）

    Args:
        param: 参数含义及示例
    Returns:
        返回值格式说明
    '''
    return json.dumps(result, ensure_ascii=False)

# 2. 创建 Agent
agent = create_agent(
    model=llm,
    tools=[my_tool, ...],
    system_prompt='角色设定 + 工作流程 + 工具选择逻辑 + 注意事项'
)

# 3. 调用 Agent
result = agent.invoke({'messages': [HumanMessage(content='用户问题')]})
print(result['messages'][-1].content)
```

---

> 🎓 **写在最后**：陈天明的故事告诉我们，金融 AI 不只是把公式变成代码。
>
> 真正的挑战，是在「模型失效」的时候，有勇气和能力找到真正的问题所在。
>
> Fan et al. (2012) 的洞见——**用时间换空间，用高频换精度**——正是因为
> 有人在真实的市场中受过伤，才被发现、被验证、被珍视。
>
> 这，就是理论与实践的最美距离。

---
*上海财经大学《金融智能体设计》课程 | 教学案例 v1.0*
""", "cell-summary"))

# ─────────────────────────────────────────────────────────────────────────────
notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "codemirror_mode": {"name": "ipython", "version": 3},
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "pygments_lexer": "ipython3",
            "version": "3.11.0"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 5
}

out = pathlib.Path(__file__).parent / "case_portfolio_langchain.ipynb"
out.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"✅ 生成成功: {out}")
print(f"   共 {len(cells)} 个 Cell")
