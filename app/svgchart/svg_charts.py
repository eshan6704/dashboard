# svg_charts.py
import math

class SVG:
    def __init__(self, width, height, bg="white"):
        self.w = width
        self.h = height
        self.bg = bg
        self.e = []

    def line(self, x1, y1, x2, y2, stroke="#333", w=1):
        self.e.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{w}"/>'
        )

    def rect(self, x, y, w, h, fill):
        self.e.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"/>'
        )

    def text(self, x, y, t, size=11, color="#111", anchor="start"):
        self.e.append(
            f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" '
            f'text-anchor="{anchor}" font-family="Arial">{t}</text>'
        )

    def raw(self, s):
        self.e.append(s)

    def render(self):
        return (
            f'<svg width="{self.w}" height="{self.h}" style="background:{self.bg};border:1px solid #ccc">'
            + "".join(self.e) +
            "</svg>"
        )

# -----------------------------------
# Main Candlestick + Volume chart
# -----------------------------------
def candlestick_chart(df, title="Price & Volume"):
    W, H = 1200, 520
    PAD_L, PAD_R, PAD_T, PAD_B = 70, 30, 40, 120
    VOL_H = 100
    VOL_Y = PAD_T + (H-PAD_T-PAD_B-VOL_H)
    svg = SVG(W,H)
    svg.text(W/2,25,title,16,"#111","middle")

    prices = df["High"].tolist()+df["Low"].tolist()
    pmin, pmax = min(prices), max(prices)
    vmax = df["Volume"].max()

    def yp(p): return PAD_T + (pmax-p)/(pmax-pmin)*(H-PAD_T-PAD_B-VOL_H)
    def yv(v): return VOL_Y + VOL_H - (v/vmax)*VOL_H

    # Draw horizontal price grid
    for i in range(6):
        y = PAD_T + i*(H-PAD_T-PAD_B-VOL_H)/5
        price = pmax - i*(pmax-pmin)/5
        svg.line(PAD_L, y, W-PAD_R, y, "#eee")
        svg.text(5, y+4, f"{price:.2f}")

    # Axes
    svg.line(PAD_L, PAD_T, PAD_L, H-PAD_B, "#444")
    svg.line(PAD_L, H-PAD_B-VOL_H, W-PAD_R, H-PAD_B-VOL_H, "#444")  # volume axis

    step = (W-PAD_L-PAD_R)/len(df)
    cw = step*0.6

    # Highest / Lowest lines
    high = df["High"].max()
    low = df["Low"].min()
    svg.line(PAD_L, yp(high), W-PAD_R, yp(high), "#f00", 2)
    svg.text(W-PAD_R-60, yp(high)-2,"High","#f00")
    svg.line(PAD_L, yp(low), W-PAD_R, yp(low), "#00f", 2)
    svg.text(W-PAD_R-60, yp(low)-2,"Low","#00f")

    # Draw candles + volume
    for i,r in enumerate(df.itertuples()):
        x = PAD_L + i*step + step/2
        o,h,l,c = r.Open,r.High,r.Low,r.Close
        color = "#2ca02c" if c>=o else "#d62728"
        # Wick
        svg.line(x, yp(h), x, yp(l), color)
        # Body
        top = yp(max(o,c))
        bh = max(abs(yp(o)-yp(c)),1)
        svg.rect(x-cw/2, top, cw, bh, color)
        # Volume
        svg.rect(x-cw/2, yv(r.Volume), cw, VOL_Y+VOL_H-yv(r.Volume), color)
        # Tooltip
        svg.raw(f'<title>{r.DateStr} O:{o:.2f} H:{h:.2f} L:{l:.2f} C:{c:.2f} V:{int(r.Volume)}</title>')

    # X-axis labels
    n_labels = 6
    interval = max(1,len(df)//n_labels)
    for idx in range(0,len(df),interval):
        r=df.iloc[idx]
        x=PAD_L+idx*step+step/2
        svg.text(x,H-PAD_B+20,r.DateStr,11,"#111","middle")

    return svg.render()

# -----------------------------------
# Line chart (for weekly/monthly)
# -----------------------------------
def line_chart(df,column="Close",title="Line Chart"):
    W,H=1200,220
    PAD=50
    svg=SVG(W,H)
    svg.text(W/2,20,title,16,"#111","middle")

    vals=df[column]
    ymin,ymax=min(vals),max(vals)
    def y(v): return PAD + (ymax-v)/(ymax-ymin)*(H-2*PAD)
    step=(W-2*PAD)/len(vals)

    pts=[]
    for i,v in enumerate(vals):
        x=PAD+i*step
        pts.append(f"{x},{y(v)}")
    svg.raw(f'<polyline fill="none" stroke="#1f77b4" stroke-width="2" points="{" ".join(pts)}"/>')

    # X-axis
    n_labels=6
    interval=max(1,len(df)//n_labels)
    for idx in range(0,len(df),interval):
        r=df.iloc[idx]
        x=PAD+idx*step
        svg.text(x,H-PAD+15,r.DateStr,11,"#111","middle")
    svg.line(PAD,H-PAD,W-PAD,H-PAD,"#444")

    # Y-axis
    for i in range(6):
        yval = PAD + i*(H-2*PAD)/5
        val = ymax - i*(ymax-ymin)/5
        svg.line(PAD,yval,PAD-5,yval,"#444")
        svg.text(5,yval+4,f"{val:.2f}")

    return svg.render()

# -----------------------------------
# RSI Chart
# -----------------------------------
def rsi_chart(df):
    W,H=1200,180
    PAD=40
    svg=SVG(W,H)
    svg.text(20,20,"RSI (14)",14,"#111")

    rsi=df["RSI"]
    step=(W-2*PAD)/len(rsi)
    pts=[]
    for i,v in enumerate(rsi):
        x=PAD+i*step
        y=H-PAD-(v/100)*(H-2*PAD)
        pts.append(f"{x},{y}")
    svg.raw(f'<polyline fill="none" stroke="#6a5acd" stroke-width="2" points="{" ".join(pts)}"/>')

    # 50 line
    y50=H-PAD-(50/100)*(H-2*PAD)
    svg.line(PAD,y50,W-PAD,y50,"#ccc")
    svg.text(W-60,y50-5,"50")

    # X-axis labels
    n_labels=6
    interval=max(1,len(df)//n_labels)
    for idx in range(0,len(df),interval):
        r=df.iloc[idx]
        x=PAD+idx*step
        svg.text(x,H-PAD+15,r.DateStr,11,"#111","middle")
    svg.line(PAD,H-PAD,W-PAD,H-PAD,"#444")

    return svg.render()

# -----------------------------------
# MACD chart with histogram
# -----------------------------------
def macd_chart(df):
    W,H=1200,220
    PAD=40
    svg=SVG(W,H)
    svg.text(20,20,"MACD",14,"#111")

    macd=df["MACD"]
    signal=df["MACD_SIGNAL"]
    hist=macd-signal

    vmin,vmax=min(list(macd)+list(signal)+list(hist)),max(list(macd)+list(signal)+list(hist))
    def y(v): return H-PAD-(v-vmin)/(vmax-vmin)*(H-2*PAD)
    step=(W-2*PAD)/len(macd)

    # MACD and signal lines
    mpts,spts=[],[]
    for i in range(len(macd)):
        x=PAD+i*step
        mpts.append(f"{x},{y(macd.iloc[i])}")
        spts.append(f"{x},{y(signal.iloc[i])}")
    svg.raw(f'<polyline fill="none" stroke="#2ca02c" stroke-width="2" points="{" ".join(mpts)}"/>')
    svg.raw(f'<polyline fill="none" stroke="#d62728" stroke-width="2" points="{" ".join(spts)}"/>')

    # Histogram
    cw = step*0.6
    for i,hv in enumerate(hist):
        x=PAD+i*step
        y0=y(0)
        yv=y(hv)
        color="#2ca02c" if hv>=0 else "#d62728"
        svg.rect(x-cw/2,min(y0,yv),cw,abs(yv-y0),color)

    # X-axis
    n_labels=6
    interval=max(1,len(df)//n_labels)
    for idx in range(0,len(df),interval):
        r=df.iloc[idx]
        x=PAD+idx*step
        svg.text(x,H-PAD+15,r.DateStr,11,"#111","middle")
    svg.line(PAD,H-PAD,W-PAD,H-PAD,"#444")

    return svg.render()
