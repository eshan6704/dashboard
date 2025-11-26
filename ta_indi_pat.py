import pandas as pd
import talib
import numpy as np

def patterns(df):
    """
    Return a DataFrame of all CDL patterns (0/1),
    with original Date + OHLC as the first columns.
    """
    df = df.copy()
    for col in ['Open','High','Low','Close']:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    pattern_df = pd.DataFrame({
        p: (getattr(talib, p)(
            df['Open'].values.astype(float),
            df['High'].values.astype(float),
            df['Low'].values.astype(float),
            df['Close'].values.astype(float)
        ) != 0).astype(int)
        for p in dir(talib) if p.startswith("CDL")
    }, index=df.index)

    # Prepend Date + OHLC
    for col in ['Date', 'Open', 'High', 'Low', 'Close'][::-1]:
        pattern_df.insert(0, col, df[col].values)

    return pattern_df


def indicators(df):
    """
    Return a DataFrame of numeric TA-Lib indicators,
    with original Date + OHLC as the first columns.
    """
    df_std = df.copy()
    df_std.columns = [c.lower() for c in df_std.columns]

    ohlcv = {k: df_std.get(k) for k in ['open','high','low','close','volume']}
    indicator_list = [f for f in dir(talib)
                      if not f.startswith("CDL") and not f.startswith("_")
                      and f not in ["wraps", "wrapped_func"]]

    dfs = []
    for name in indicator_list:
        func = getattr(talib, name)
        try:
            if ohlcv['close'] is None:
                continue
            result = func(ohlcv['close'].values.astype(float))
            # handle tuple outputs
            if isinstance(result, tuple):
                for i, arr in enumerate(result):
                    dfs.append(pd.DataFrame(arr, index=df.index, columns=[f"{name}_{i}"]))
            else:
                dfs.append(pd.DataFrame(result, index=df.index, columns=[name]))
        except:
            continue

    indicator_df = pd.concat(dfs, axis=1) if dfs else pd.DataFrame(index=df.index)

    # Prepend Date + OHLC
    for col in ['Date', 'Open', 'High', 'Low', 'Close'][::-1]:
        indicator_df.insert(0, col, df[col].values)

    return indicator_df
