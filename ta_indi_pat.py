
import pandas as pd
import talib
import numpy as np

def patterns(df):

    # Copy and normalize columns
    df = df.copy()
    required_cols = ['Open','High','Low','Close']

    # DataFrame to store patterns only
    pattern_df = pd.DataFrame(index=df.index)

    # Get all CDL pattern functions
    pattern_list = [f for f in dir(talib) if f.startswith("CDL")]

    # Apply each pattern function
    for pattern in pattern_list:
        func = getattr(talib, pattern)
        result = func(
            df['Open'].values.astype(float),
            df['High'].values.astype(float),
            df['Low'].values.astype(float),
            df['Close'].values.astype(float)
        )

        # Convert +100/-100 → 1, 0 stays 0
        pattern_df[pattern] = (result != 0).astype(int)

    return pattern_df

def indicators(df):

    df_std = df.copy()
    df_std.columns = [c.lower() for c in df_std.columns]

    ohlcv = {
        'open': df_std.get('open'),
        'high': df_std.get('high'),
        'low': df_std.get('low'),
        'close': df_std.get('close'),
        'volume': df_std.get('volume')
    }

    #indicator_list = [f for f in dir(talib) if not f.startswith("CDL") and not f.startswith("_")]
    indicator_list = [
        f for f in dir(talib)
        if not f.startswith("CDL") and not f.startswith("_") and f not in ["wraps", "wrapped_func"]
        ]

    df_list = []  # store all indicator columns as separate DataFrames

    for name in indicator_list:
        func = getattr(talib, name)
        try:
            if 'close' in ohlcv and ohlcv['close'] is not None:
                result = func(ohlcv['close'].values.astype(float))
            else:
                continue

            # If function returns tuple, add each output separately
            if isinstance(result, tuple):
                for i, arr in enumerate(result):
                    col_name = f"{name}_{i}"
                    temp_df = pd.DataFrame(arr, index=df.index, columns=[col_name])
                    df_list.append(temp_df)
            else:
                temp_df = pd.DataFrame(result, index=df.index, columns=[name])
                df_list.append(temp_df)
        except:
            continue

    # Concatenate all columns at once
    if df_list:
        indicator_df = pd.concat(df_list, axis=1)
    else:
        indicator_df = pd.DataFrame(index=df.index)

    return indicator_df
