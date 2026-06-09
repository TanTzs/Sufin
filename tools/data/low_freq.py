import json
import pandas as pd
import yfinance as yf
from langchain_core.tools import tool
from tools.state import portfolio_data

def _a_code_to_yahoo(code: str) -> str:
    if code.startswith('6'):
        return f'{code}.SS'
    elif code.startswith(('0', '3')):
        return f'{code}.SZ'
    elif code.startswith(('4', '8')):
        return f'{code}.BJ'
    return code


def _fetch(codes: list, start_date: str, end_date: str) -> "dict | str":
    """下载收盘价并计算日收益率，返回 {'prices': DataFrame, 'returns': DataFrame} 或 JSON 错误串。"""
    start = pd.to_datetime(start_date, format='%Y%m%d').strftime('%Y-%m-%d')
    end   = pd.to_datetime(end_date,   format='%Y%m%d').strftime('%Y-%m-%d')
    try:
        raw = yf.download(codes, start=start, end=end, progress=False, auto_adjust=True)

        if raw.empty:
            return json.dumps({'错误': 'yfinance 返回空数据，请检查股票代码和日期范围'}, ensure_ascii=False)

        if isinstance(raw.columns, pd.MultiIndex):
            level0 = raw.columns.get_level_values(0).unique().tolist()
            price_col = 'Close' if 'Close' in level0 else ('Adj Close' if 'Adj Close' in level0 else None)
            if price_col is None:
                return json.dumps({'错误': f'找不到收盘价列，现有字段：{level0}'}, ensure_ascii=False)
            close = raw[price_col]
            if isinstance(close, pd.Series):
                close = close.to_frame(name=codes[0])
            close.columns = [str(c) for c in close.columns]
        else:
            price_col = 'Close' if 'Close' in raw.columns else 'Adj Close'
            close = raw[[price_col]].rename(columns={price_col: codes[0]})

        close   = close.dropna(how='all')
        returns = close.pct_change().dropna()

        if returns.empty or len(returns) < 5:
            return json.dumps({'错误': '有效数据不足，请确认股票代码正确或换个日期范围'}, ensure_ascii=False)

        return {'prices': close, 'returns': returns}
    except Exception as e:
        return json.dumps({'错误': f'yfinance 下载失败：{e}'}, ensure_ascii=False)


def _fetch_a(codes: list, start_date: str, end_date: str):
    yahoo_codes = [_a_code_to_yahoo(c) for c in codes]
    result = _fetch(yahoo_codes, start_date, end_date)
    if isinstance(result, dict):
        result['prices']  = result['prices'].rename(columns=dict(zip(yahoo_codes, codes)))
        result['returns'] = result['returns'].rename(columns=dict(zip(yahoo_codes, codes)))
    return result


@tool
def download_stock_data(
    stock_codes: str,
    market: str = 'A',
    start_date: str = '20240101',
    end_date: str = '20241231',
    query_type: str = 'summary',
) -> str:
    '''下载股票历史行情数据，支持 A 股和美股。

    Args:
        stock_codes: 股票代码，多只用英文逗号分隔。
                     A股示例：000001,600519,300750
                     美股示例：AAPL,MSFT,GOOGL
        market:      市场选择，A 表示 A 股，US 表示美股，默认 A
        start_date:  起始日期，格式 YYYYMMDD，默认 20240101
        end_date:    结束日期，格式 YYYYMMDD，默认 20241231
        query_type:  返回内容类型：
                     "summary" —— 综合摘要（年化收益、波动率），适合做组合优化前的概览；
                     "price"   —— 最近 10 条收盘价及价格区间统计；
                     "returns" —— 日收益率统计（均值、标准差、最大/最小值）。

    Returns:
        JSON 字符串，内容取决于 query_type。数据同时保存供 markowitz_optimize 使用。
    '''
    codes  = [c.strip() for c in stock_codes.split(',')]
    result = _fetch(codes, start_date, end_date) if market.upper() == 'US' \
             else _fetch_a(codes, start_date, end_date)

    if isinstance(result, str):
        return result

    prices_df  = result['prices']
    returns_df = result['returns']

    # 始终保存供 markowitz_optimize 使用
    portfolio_data['returns'] = returns_df
    portfolio_data['prices']  = prices_df
    portfolio_data['stocks']  = codes
    portfolio_data['market']  = market.upper()

    qt = query_type.lower()

    if qt == 'price':
        recent = prices_df.tail(10).round(4).copy()
        recent.index = recent.index.strftime('%Y-%m-%d')
        output = {
            '状态': '下载成功',
            '市场': 'A股' if market.upper() == 'A' else '美股',
            '股票代码': codes,
            '有效交易日数': len(prices_df),
            '日期范围': f'{prices_df.index[0].strftime("%Y-%m-%d")} 至 {prices_df.index[-1].strftime("%Y-%m-%d")}',
            '最近10日收盘价': recent.to_dict(orient='index'),
            '区间最高价': prices_df.max().round(4).to_dict(),
            '区间最低价': prices_df.min().round(4).to_dict(),
            '区间涨跌幅': {
                code: f'{(prices_df[code].iloc[-1] / prices_df[code].iloc[0] - 1):.2%}'
                for code in codes
            },
        }

    elif qt == 'returns':
        output = {
            '状态': '下载成功',
            '市场': 'A股' if market.upper() == 'A' else '美股',
            '股票代码': codes,
            '有效交易日数': len(returns_df),
            '日期范围': f'{str(returns_df.index[0])} 至 {str(returns_df.index[-1])}',
            '日均收益率': returns_df.mean().map('{:.4%}'.format).to_dict(),
            '日收益率标准差': returns_df.std().map('{:.4%}'.format).to_dict(),
            '单日最大涨幅': returns_df.max().map('{:.2%}'.format).to_dict(),
            '单日最大跌幅': returns_df.min().map('{:.2%}'.format).to_dict(),
            '年化收益率（估算）': {
                code: f'{returns_df[code].mean() * 252:.2%}' for code in codes
            },
            '年化波动率（估算）': {
                code: f'{returns_df[code].std() * (252 ** 0.5):.2%}' for code in codes
            },
        }

    else:  # summary（默认）
        output = {
            '状态': '下载成功',
            '市场': 'A股' if market.upper() == 'A' else '美股',
            '股票代码': codes,
            '有效交易日数': len(returns_df),
            '日期范围': f'{str(returns_df.index[0])} 至 {str(returns_df.index[-1])}',
            '区间涨跌幅': {
                code: f'{(prices_df[code].iloc[-1] / prices_df[code].iloc[0] - 1):.2%}'
                for code in codes
            },
            '年化收益率（估算）': {
                code: f'{returns_df[code].mean() * 252:.2%}' for code in codes
            },
            '年化波动率（估算）': {
                code: f'{returns_df[code].std() * (252 ** 0.5):.2%}' for code in codes
            },
            '提示': '数据已保存，可调用 markowitz_optimize 进行优化',
        }

    return json.dumps(output, ensure_ascii=False, indent=2)
