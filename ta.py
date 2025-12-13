import pandas as pd
import talib
import numpy as np

def talib_df(df):
    """
    Return a single DataFrame containing:
    - Original Date + OHLCV columns
    - All numeric TA-Lib indicators
    - All CDL patterns (0/1)
    """
    df = df.copy()
    
    # Ensure OHLCV columns exist
    for col in ['Open','High','Low','Close','Volume']:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    # Base DF with Date + OHLCV
    result_df = df[['Date','Close','High','Low','Open','Volume']].copy()

    # --- Indicators ---
    df_std = df.copy()
    df_std.columns = [c.lower() for c in df_std.columns]
    ohlcv = {k: df_std.get(k) for k in ['open','high','low','close','volume']}
    
    indicator_list = [
        f for f in dir(talib)
        if not f.startswith("CDL") and not f.startswith("_")
        and f not in ["wraps", "wrapped_func"]
    ]
    
    indicator_dfs = []
    for name in indicator_list:
        func = getattr(talib, name)
        try:
            if ohlcv['close'] is None:
                continue
            res = func(ohlcv['close'].values.astype(float))
            if isinstance(res, tuple):
                for i, arr in enumerate(res):
                    indicator_dfs.append(pd.DataFrame(arr, index=df.index, columns=[f"{name}_{i}"]))
            else:
                indicator_dfs.append(pd.DataFrame(res, index=df.index, columns=[name]))
        except:
            continue
    if indicator_dfs:
        result_df = pd.concat([result_df] + indicator_dfs, axis=1)

    # --- CDL Patterns ---
    pattern_list = [f for f in dir(talib) if f.startswith("CDL")]
    for p in pattern_list:
        func = getattr(talib, p)
        try:
            res = func(
                df['Open'].values.astype(float),
                df['High'].values.astype(float),
                df['Low'].values.astype(float),
                df['Close'].values.astype(float)
            )
            result_df[p] = (res != 0).astype(int)
        except:
            continue

    return result_df
