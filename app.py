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

# Using Gradio Blocks so we can define the custom API endpoint "/fetch_data"
with gr.Blocks() as app:
    # Just a dummy UI for testing (optional)
    gr.HTML("<h3>Backend Master API</h3>")

# Expose the fetch_data function as the /fetch_data API endpoint
app.predict(fetch_data, inputs=["text", "text"], outputs="html", api_name="/fetch_data")

if __name__ == "__main__":
    app.launch()
