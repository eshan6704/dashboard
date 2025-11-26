# chart_builder.py
import plotly.graph_objs as go
from indicator import (
    calc_macd, calc_rsi, calc_supertrend,
    calc_stochastic, calc_keltner, calc_zigzag,
    calc_swings
)

def build_chart(df):
    fig = go.Figure()

    # =============================
    # MAIN PRICE PANEL
    # =============================
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"],
        name="Price", yaxis="y"
    ))

    # Volume
    fig.add_trace(go.Bar(
        x=df.index, y=df["Volume"], name="Volume", yaxis="y2", opacity=0.3
    ))

    # =============================
    # INDICATORS
    # =============================
    rsi = calc_rsi(df)
    macd = calc_macd(df)
    st = calc_supertrend(df)
    stoch = calc_stochastic(df)
    kc = calc_keltner(df)
    zig = calc_zigzag(df)
    sw = calc_swings(df)

    # RSI Panel
    fig.add_trace(go.Scatter(x=df.index, y=rsi["RSI"], name="RSI", yaxis="y3"))

    # MACD Panel
    fig.add_trace(go.Scatter(x=df.index, y=macd["MACD"], name="MACD", yaxis="y4"))
    fig.add_trace(go.Scatter(x=df.index, y=macd["Signal"], name="Signal", yaxis="y4"))
    fig.add_trace(go.Bar(x=df.index, y=macd["Histogram"], name="Hist", yaxis="y4"))

    # Supertrend
    fig.add_trace(go.Scatter(x=df.index, y=st["Supertrend"], name="Supertrend", yaxis="y"))

    # Stoch
    fig.add_trace(go.Scatter(x=df.index, y=stoch["STOCH_K"], name="STOCH_K", yaxis="y5"))
    fig.add_trace(go.Scatter(x=df.index, y=stoch["STOCH_D"], name="STOCH_D", yaxis="y5"))

    # Keltner
    fig.add_trace(go.Scatter(x=df.index, y=kc["KC_UP"], name="KC UP", yaxis="y"))
    fig.add_trace(go.Scatter(x=df.index, y=kc["KC_MID"], name="KC MID", yaxis="y"))
    fig.add_trace(go.Scatter(x=df.index, y=kc["KC_LOW"], name="KC LOW", yaxis="y"))

    # ZigZag
    fig.add_trace(go.Scatter(x=df.index, y=zig["ZIGZAG"], name="ZIGZAG", yaxis="y"))

    # Swings
    fig.add_trace(go.Scatter(x=df.index, y=sw["SWING_HIGH"], name="Swing High", yaxis="y"))
    fig.add_trace(go.Scatter(x=df.index, y=sw["SWING_LOW"], name="Swing Low", yaxis="y"))

    # =============================
    # LAYOUT
    # =============================
    fig.update_layout(
        height=1200,
        xaxis=dict(domain=[0, 1], rangeslider=dict(visible=False)),
        yaxis=dict(domain=[0.55, 1]),       # Price
        yaxis2=dict(domain=[0.45, 0.55]),   # Volume
        yaxis3=dict(domain=[0.30, 0.45]),   # RSI
        yaxis4=dict(domain=[0.15, 0.30]),   # MACD
        yaxis5=dict(domain=[0.00, 0.15]),   # Stochastic
        showlegend=True
    )

    return fig.to_html(full_html=False)
