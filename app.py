import gradio as gr

def fetch_data(symbol, req_type):
    # Here you can add real logic to fetch stock data
    # For now, returning a prefabricated HTML string using inputs
    html_response = f"""
    <html>
      <head><title>Stock Data for {symbol}</title></head>
      <body>
        <h1>Data Request</h1>
        <p>Symbol: {symbol}</p>
        <p>Request Type: {req_type}</p>
        <p>This is a static HTML response from backend for demonstration.</p>
      </body>
    </html>
    """
    return html_response


iface=  gr.Interface(
        fn=fetch_data,
        inputs=[
            gr.Textbox(label="Stock Symbol", value='PNB'),
            gr.Textbox(label="req Type ", value='info')
        ],

        outputs=gr.JSON(label="Collected Stock Data"),
        title="Stock Data API (Full)",
        description="Fetch data fromnse and yfinance",
    
        api_name="fetch_data"
    )
if __name__ == "__main__":
    iface.launch(server_name="0.0.0.0", server_port=7860)