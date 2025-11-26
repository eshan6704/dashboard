import plotly.graph_objects as go
from plotly.subplots import make_subplots

def build_chart(df, indicators):
    """
    df: OHLCV DataFrame
    indicators: dict returned from indicater.py
    Returns Plotly HTML with embedded JS to enable/disable indicators
    """
    fig = make_subplots(rows=6, cols=1,
                        shared_xaxes=True,
                        row_heights=[0.5,0.2,0.2,0.2,0.2,0.2],
                        vertical_spacing=0.02,
                        subplot_titles=["Price", "Volume", "MACD", "RSI", "SuperTrend", "ZigZag/Swing"])

    # ---------------- Price Candlestick ----------------
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'],
        name='Price', row=1, col=1
    ))

    # Moving Averages on main chart
    for ma in ['MA10','MA50','MA200']:
        fig.add_trace(go.Scatter(
            x=df.index, y=indicators[ma],
            name=ma, visible='legendonly', row=1, col=1
        ))

    # Volume subplot
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', row=2, col=1))

    # MACD subplot
    fig.add_trace(go.Scatter(x=df.index, y=indicators['MACD']['macd'], name='MACD', visible='legendonly', row=3, col=1))
    fig.add_trace(go.Scatter(x=df.index, y=indicators['MACD']['signal'], name='MACD Signal', visible='legendonly', row=3, col=1))
    fig.add_trace(go.Bar(x=df.index, y=indicators['MACD']['hist'], name='MACD Hist', visible='legendonly', row=3, col=1))

    # RSI subplot
    fig.add_trace(go.Scatter(x=df.index, y=indicators['RSI'], name='RSI', visible='legendonly', row=4, col=1))

    # SuperTrend subplot
    fig.add_trace(go.Scatter(x=df.index, y=indicators['SUPERTREND'], name='SuperTrend', visible='legendonly', row=5, col=1))

    # ZigZag/Swing subplot
    fig.add_trace(go.Scatter(x=df.index, y=indicators['ZIGZAG'], name='ZigZag', visible='legendonly', row=6, col=1))
    fig.add_trace(go.Scatter(x=df.index, y=indicators['SWING'], name='Swing', visible='legendonly', row=6, col=1))

    fig.update_layout(
        height=1000,
        xaxis_rangeslider_visible=False,
        legend=dict(itemclick="toggleothers"),
        title="Stock Chart with Indicators"
    )

    html_chart = fig.to_html(full_html=False, include_plotlyjs=True)

    # Inject JS to enable/disable indicators dynamically
    script = """
    <script>
    document.querySelectorAll('.legendtoggle').forEach(item=>{
        item.addEventListener('click', e=>{
            console.log('Toggle indicator:', e);
        });
    });
    </script>
    """

    return html_chart + script
