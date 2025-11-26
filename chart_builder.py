# chart_builder.py
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def build_chart(df, indicators, symbol="Stock"):
    """
    Build Plotly chart with main OHLC + optional subplots for indicators.
    Inject JS to toggle each indicator dynamically.
    """
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.7, 0.3],
        vertical_spacing=0.05,
        subplot_titles=(f"{symbol} Price", "Indicators")
    )

    # --- Main chart: OHLC + MA ---
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'], name='OHLC'
    ), row=1, col=1)

    # MA on main chart
    for ma in ['SMA20', 'SMA50']:
        if ma in indicators:
            fig.add_trace(go.Scatter(
                x=df.index, y=indicators[ma],
                mode='lines', name=ma
            ), row=1, col=1)

    # --- Subplot for MACD/RSI/SuperTrend ---
    indicator_row = 2
    for ind_name in ['MACD', 'RSI', 'SuperTrend']:
        if ind_name in indicators:
            data = indicators[ind_name]
            if isinstance(data, pd.DataFrame):
                for col in data.columns:
                    fig.add_trace(go.Scatter(
                        x=df.index, y=data[col],
                        mode='lines', name=f"{ind_name}-{col}",
                        visible=False  # Start hidden, toggle later
                    ), row=indicator_row, col=1)
            else:
                fig.add_trace(go.Scatter(
                    x=df.index, y=data,
                    mode='lines', name=ind_name,
                    visible=False
                ), row=indicator_row, col=1)

    # --- Layout ---
    fig.update_layout(
        height=700,
        showlegend=True,
        title=f"{symbol} Chart with Indicators",
        xaxis_rangeslider_visible=False
    )

    # --- Inject JS for toggle buttons ---
    toggle_script = """
    <script>
    function toggleIndicator(indName) {
        var gd = document.querySelectorAll('.js-plotly-plot')[0];
        var update = {visible: []};
        gd.data.forEach(function(trace) {
            if(trace.name.includes(indName)) {
                trace.visible = !trace.visible;
            }
        });
        Plotly.redraw(gd);
    }
    </script>
    <div style="margin-top:10px;">
        <button onclick="toggleIndicator('MACD')">Toggle MACD</button>
        <button onclick="toggleIndicator('RSI')">Toggle RSI</button>
        <button onclick="toggleIndicator('SuperTrend')">Toggle SuperTrend</button>
    </div>
    """

    chart_html = fig.to_html(full_html=False, include_plotlyjs='cdn') + toggle_script
    return chart_html
