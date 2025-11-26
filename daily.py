
import yfinance as yf
import pandas as pd
from ta_indi_pat import patterns, indicators
from common import html_card, wrap_html

def fetch_daily(symbol, max_rows=200):
    """
    Fetch daily OHLCV data, calculate indicators + patterns,
    return 3 scrollable HTML tables with toggle buttons.
    """
    try:
        # --- Fetch daily data ---
        df = yf.download(symbol + ".NS", period="1y", interval="1d").round(2)
        df.columns=["Close",	"High",	"Low",	"Open",	"Volume"]
        if df.empty:
            return html_card("Error", f"No daily data found for {symbol}")

        df.reset_index(inplace=True)  # make Date a column

        # --- Limit rows for display ---
        df_display = df.head(max_rows)

        # --- Generate indicators and patterns ---
        indicator_df = indicators(df_display)
        pattern_df = patterns(df_display)

        # --- Convert to HTML tables ---
        df_html = df_display.to_html(classes="table table-striped table-bordered", index=False)
        indicator_html = indicator_df.to_html(classes="table table-striped table-bordered", index=False)
        pattern_html = pattern_df.to_html(classes="table table-striped table-bordered", index=False)

        # --- Wrap each table in scrollable div ---
        scrollable_template = '<div style="overflow-x:auto; overflow-y:auto; max-height:400px; border:1px solid #ccc; padding:5px; margin-bottom:10px;">{}</div>'
        df_html = scrollable_template.format(df_html)
        indicator_html = scrollable_template.format(indicator_html)
        pattern_html = scrollable_template.format(pattern_html)

        # --- HTML buttons for toggling ---
        toggle_script = """
        <script>
        function toggleTable(id){
            var tbl = document.getElementById(id);
            if(tbl.style.display === "none"){
                tbl.style.display = "block";
            } else {
                tbl.style.display = "none";
            }
        }
        </script>
        """

        # --- Build buttons and tables ---
        content = f"""
        <h2>{symbol} - Daily Data</h2>

        <button onclick="toggleTable('ohlcv_table')">Toggle OHLCV</button>
        <button onclick="toggleTable('indicator_table')">Toggle Indicators</button>
        <button onclick="toggleTable('pattern_table')">Toggle Patterns</button>

        {toggle_script}

        <div id="ohlcv_table">{html_card("OHLCV Data", df_html)}</div>
        <div id="indicator_table">{html_card("Indicators", indicator_html)}</div>
        <div id="pattern_table">{html_card("Patterns", pattern_html)}</div>
        """

        return wrap_html(content, title=f"{symbol} Daily Data")

    except Exception as e:
        return html_card("Error", str(e))
