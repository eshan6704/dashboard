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
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{stroke}" stroke-width="{w}"/>'
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
            f'<svg width="{self.w}" height="{self.h}" '
            f'style="background:{self.bg};border:1px solid #ccc">'
            + "".join(self.e) +
            "</svg>"
        )

# ----------------------
# Price + Volume + MA + X-axis + Support/Resistance + Patterns
# ----------------------
def price_volume_chart(df, title, pattern_highlight=True, support_res=True):
    W, H = 1200, 520
    PAD_L, PAD_R, PAD_T, PAD_B = 70, 30, 40, 120
    PRICE_H = H - PAD_T - PAD_B
    VOL_H = 80
    VOL_Y = PAD_T + PRICE_H + 20

    svg = SVG(W, H)
    svg.text(W/2, 25, title, size=16, anchor="middle")

    prices = df["High"].tolist() + df["Low"].tolist()
    pmin, pmax = min(prices), max(prices)
    vmax = df["Volume"].max()

    def yp(p): return PAD_T + (pmax - p) / (pmax - pmin) * PRICE_H
    def yv(v): return VOL_Y + VOL_H - (v / vmax) * VOL_H

    # Price grid
    for i in range(6):
        y = PAD_T + i*PRICE_H/5
        price = pmax - i*(pmax - pmin)/5
        svg.line(PAD_L, y, W-PAD_R, y, "#eee")
        svg.text(5, y+4, f"{price:.0f}")

    # Axes
    svg.line(PAD_L, PAD_T, PAD_L, PAD_T+PRICE_H, "#444")
    svg.line(PAD_L, PAD_T+PRICE_H, W-PAD_R, PAD_T+PRICE_H, "#444")

    step = (W - PAD_L - PAD_R)/len(df)
    cw = step*0.6

    ma20_pts, ma50_pts = [], []

    # Support / Resistance
    if support_res:
        sup = df["Low"].tail(20).min()
        res = df["High"].tail(20).max()
        svg.line(PAD_L, yp(sup), W-PAD_R, yp(sup), "#00f", w=1)
        svg.text(W-PAD_R-60, yp(sup)-2, "Support", color="#00f")
        svg.line(PAD_L, yp(res), W-PAD_R, yp(res), "#f00", w=1)
        svg.text(W-PAD_R-60, yp(res)-2, "Resistance", color="#f00")

    # Candles + Volume + Patterns
    for i, r in enumerate(df.itertuples()):
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
        svg.rect(x-cw/2, yv(r.Volume), cw, VOL_Y+VOL_H - yv(r.Volume), color)

        # MA points
        if not math.isnan(r.MA20):
            ma20_pts.append(f"{x},{yp(r.MA20)}")
        if not math.isnan(r.MA50):
            ma50_pts.append(f"{x},{yp(r.MA50)}")

        # Patterns (simple examples)
        if pattern_highlight:
            if c>o and (h-c)<(c-o)*0.1: # simple bullish hammer
                svg.rect(x-cw/2-1, top-2, cw+2, bh+4, "none")
            elif o>c and (h-o)<(o-c)*0.1: # simple bearish hammer
                svg.rect(x-cw/2-1, top-2, cw+2, bh+4, "none")

        # Tooltip
        svg.raw(f"<title>{r.DateStr} O:{o:.2f} H:{h:.2f} L:{l:.2f} C:{c:.2f} V:{int(r.Volume)}</title>")

    # MA lines
    if ma20_pts:
        svg.raw(f'<polyline fill="none" stroke="#1f77b4" stroke-width="2" points="{" ".join(ma20_pts)}"/>')
    if ma50_pts:
        svg.raw(f'<polyline fill="none" stroke="#ff7f0e" stroke-width="2" points="{" ".join(ma50_pts)}"/>')

    # X-axis labels (show first, mid, last 6)
    n_labels = 6
    interval = max(1,len(df)//n_labels)
    for idx in range(0,len(df), interval):
        r = df.iloc[idx]
        x = PAD_L + idx*step + step/2
        svg.text(x, PAD_T+PRICE_H+VOL_H+20, r.DateStr, size=11, anchor="middle")

    return svg.render()

# ----------------------
# RSI Chart with X-axis
# ----------------------
def rsi_chart(df):
    W,H = 1200,180
    PAD = 40
    svg = SVG(W,H)
    svg.text(20,20,"RSI (14)",size=14)

    rsi = df["RSI"]
    step = (W - 2*PAD)/len(rsi)
    pts = []
    for i,v in enumerate(rsi):
        x = PAD + i*step
        y = H - PAD - (v/100)*(H-2*PAD)
        pts.append(f"{x},{y}")
    svg.raw(f'<polyline fill="none" stroke="#6a5acd" stroke-width="2" points="{" ".join(pts)}"/>')

    # X-axis labels
    n_labels = 6
    interval = max(1,len(df)//n_labels)
    for idx in range(0,len(df),interval):
        r = df.iloc[idx]
        x = PAD + idx*step
        svg.text(x,H-PAD+15,r.DateStr,size=11,anchor="middle")
    svg.line(PAD,H-PAD,W-PAD,H-PAD,"#444")
    # Horizontal 50 line
    y50 = H - PAD - (50/100)*(H-2*PAD)
    svg.line(PAD,y50,W-PAD,y50,"#ccc")
    svg.text(W-60,y50-5,"50")
    return svg.render()

# ----------------------
# MACD Chart with X-axis
# ----------------------
def macd_chart(df):
    W,H=1200,220
    PAD=40
    svg = SVG(W,H)
    svg.text(20,20,"MACD",size=14)

    macd = df["MACD"]
    signal = df["MACD_SIGNAL"]
    vals = list(macd)+list(signal)
    vmin,vmax = min(vals),max(vals)
    def y(v): return H-PAD-(v-vmin)/(vmax-vmin)*(H-2*PAD)
    step = (W-2*PAD)/len(macd)
    mpts,spts=[],[]
    for i in range(len(macd)):
        x=PAD+i*step
        mpts.append(f"{x},{y(macd.iloc[i])}")
        spts.append(f"{x},{y(signal.iloc[i])}")
    svg.raw(f'<polyline fill="none" stroke="#2ca02c" stroke-width="2" points="{" ".join(mpts)}"/>')
    svg.raw(f'<polyline fill="none" stroke="#d62728" stroke-width="2" points="{" ".join(spts)}"/>')

    # X-axis labels
    n_labels = 6
    interval = max(1,len(df)//n_labels)
    for idx in range(0,len(df),interval):
        r = df.iloc[idx]
        x = PAD + idx*step
        svg.text(x,H-PAD+15,r.DateStr,size=11,anchor="middle")
    svg.line(PAD,H-PAD,W-PAD,H-PAD,"#444")
    return svg.render()
