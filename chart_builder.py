# chart_builder.py
import plotly.graph_objs as go
from indicator import macd, supertrend, keltner_channel, zigzag, swing_high_low, stockstick

def build_chart(df, indicators=None, volume=True):
    fig = go.Figure()

    # -----------------------
    # Price candlestick
    # -----------------------
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'], name='Price'
    ))

    # -----------------------
    # Volume as secondary panel
    # -----------------------
    if volume and 'Volume' in df.columns:
        vol_scale = (df['Close'].max() - df['Close'].min()) / df['Volume'].max()
        fig.add_trace(go.Bar(
            x=df.index,
            y=df['Volume']*vol_scale + df['Close'].min(),
            name='Volume', marker_color='lightblue'
        ))

    # -----------------------
    # Apply Indicators
    # -----------------------
    if indicators:
        for ind in indicators:
            ind_lower = ind.lower()
            if ind_lower == 'macd':
                macd_df = macd(df)
                fig.add_trace(go.Scatter(x=df.index, y=macd_df['MACD'], name='MACD'))
                fig.add_trace(go.Scatter(x=df.index, y=macd_df['Signal'], name='MACD Signal'))
            elif ind_lower == 'supertrend':
                st = supertrend(df)
                # Plot Supertrend as green/red markers on price
                st_price = df['Close'].where(st, None)
                fig.add_trace(go.Scatter(x=df.index, y=st_price, mode='lines', name='Supertrend', line=dict(color='green')))
            elif ind_lower == 'keltner':
                kc = keltner_channel(df)
                fig.add_trace(go.Scatter(x=df.index, y=kc['KC_upper'], name='Keltner Upper', line=dict(dash='dash')))
                fig.add_trace(go.Scatter(x=df.index, y=kc['KC_lower'], name='Keltner Lower', line=dict(dash='dash')))
            elif ind_lower == 'zigzag':
                zz = zigzag(df)
                fig.add_trace(go.Scatter(x=df.index[:len(zz)], y=zz, mode='lines+markers', name='ZigZag'))
            elif ind_lower == 'swing':
                sh, sl = swing_high_low(df)
                fig.add_trace(go.Scatter(x=sh.index, y=sh.values, mode='markers', name='Swing High', marker=dict(color='red', size=8)))
                fig.add_trace(go.Scatter(x=sl.index, y=sl.values, mode='markers', name='Swing Low', marker=dict(color='green', size=8)))
            elif ind_lower == 'stockstick':
                ss = stockstick(df)
                fig.add_trace(go.Scatter(x=df.index, y=ss, mode='lines', name='Stockstick'))

    fig.update_layout(xaxis_rangeslider_visible=False, height=600)
    return fig.to_html(full_html=False)
