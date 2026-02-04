# svg_charts.py

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


# =====================================================
# PRICE + VOLUME + MA
# =====================================================

def price_volume_chart(df, title):
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

    # Grid + Y axis
    for i in range(6):
        y = PAD_T + i * PRICE_H / 5
        price = pmax - i * (pmax - pmin) / 5
        svg.line(PAD_L, y, W - PAD_R, y, "#eee")
        svg.text(5, y + 4, f"{price:.0f}")

    step = (W - PAD_L - PAD_R) / len(df)
    cw = step * 0.6

    ma20, ma50 = [], []

    for i, r in enumerate(df.itertuples()):
        x = PAD_L + i * step + step / 2
        o, h, l, c = r.Open, r.High, r.Low, r.Close
        color = "#2ca02c" if c >= o else "#d62728"

        svg.line(x, yp(h), x, yp(l), color)
        svg.rect(x - cw/2, yp(max(o, c)), cw,
                 max(abs(yp(o) - yp(c)), 1), color)

        svg.rect(x - cw/2, yv(r.Volume), cw,
                 VOL_Y + VOL_H - yv(r.Volume), color)

        if not r.MA20 != r.MA20:
            ma20.append(f"{x},{yp(r.MA20)}")
        if not r.MA50 != r.MA50:
            ma50.append(f"{x},{yp(r.MA50)}")

    if ma20:
        svg.raw(f'<polyline fill="none" stroke="#1f77b4" stroke-width="2" '
                f'points="{" ".join(ma20)}"/>')
    if ma50:
        svg.raw(f'<polyline fill="none" stroke="#ff7f0e" stroke-width="2" '
                f'points="{" ".join(ma50)}"/>')

    return svg.render()


# =====================================================
# RSI CHART
# =====================================================

def rsi_chart(df):
    W, H = 1200, 180
    PAD = 40

    svg = SVG(W, H)
    svg.text(20, 20, "RSI (14)", size=14)

    rsi = df["RSI"]
    step = (W - 2*PAD) / len(rsi)

    pts = []
    for i, v in enumerate(rsi):
        x = PAD + i * step
        y = H - PAD - (v / 100) * (H - 2*PAD)
        pts.append(f"{x},{y}")

    svg.raw(f'<polyline fill="none" stroke="#6a5acd" stroke-width="2" '
            f'points="{" ".join(pts)}"/>')

    svg.line(PAD, H/2, W-PAD, H/2, "#ccc")
    svg.text(W-60, H/2 - 5, "50")

    return svg.render()


# =====================================================
# MACD CHART
# =====================================================

def macd_chart(df):
    W, H = 1200, 220
    PAD = 40
    svg = SVG(W, H)
    svg.text(20, 20, "MACD", size=14)

    macd = df["MACD"]
    signal = df["MACD_SIGNAL"]

    vals = list(macd) + list(signal)
    vmin, vmax = min(vals), max(vals)

    def y(v): return H - PAD - (v - vmin)/(vmax-vmin) * (H - 2*PAD)

    step = (W - 2*PAD) / len(macd)

    mpts, spts = [], []
    for i in range(len(macd)):
        x = PAD + i * step
        mpts.append(f"{x},{y(macd.iloc[i])}")
        spts.append(f"{x},{y(signal.iloc[i])}")

    svg.raw(f'<polyline fill="none" stroke="#2ca02c" stroke-width="2" '
            f'points="{" ".join(mpts)}"/>')
    svg.raw(f'<polyline fill="none" stroke="#d62728" stroke-width="2" '
            f'points="{" ".join(spts)}"/>')

    return svg.render()
