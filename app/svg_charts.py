# svg_charts.py

class SVG:
    def __init__(self, width, height, bg="white"):
        self.w = width
        self.h = height
        self.bg = bg
        self.e = []

    def line(self, x1, y1, x2, y2, stroke="#444", w=1):
        self.e.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{stroke}" stroke-width="{w}"/>'
        )

    def rect(self, x, y, w, h, fill):
        self.e.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"/>'
        )

    def text(self, x, y, t, size=11, color="#333", anchor="start"):
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


# =========================================================
# CANDLESTICK + VOLUME + MA
# =========================================================

def candlestick_with_volume(df, title=""):
    W, H = 1200, 520

    PAD_L = 70
    PAD_R = 30
    PAD_T = 40
    PAD_B = 120

    PRICE_H = H - PAD_T - PAD_B
    VOL_H = 80
    VOL_Y = PAD_T + PRICE_H + 20

    svg = SVG(W, H)

    prices = df["High"].tolist() + df["Low"].tolist()
    pmin, pmax = min(prices), max(prices)
    vmax = df["Volume"].max()

    def yp(p):
        return PAD_T + (pmax - p) / (pmax - pmin) * PRICE_H

    def yv(v):
        return VOL_Y + VOL_H - (v / vmax) * VOL_H

    # ---- Title ----
    svg.text(W / 2, 24, title, size=16, anchor="middle")

    # ---- Grid + Price Axis ----
    for i in range(6):
        y = PAD_T + i * PRICE_H / 5
        price = pmax - i * (pmax - pmin) / 5
        svg.line(PAD_L, y, W - PAD_R, y, "#eee")
        svg.text(5, y + 4, f"{price:.0f}")

    svg.line(PAD_L, PAD_T, PAD_L, PAD_T + PRICE_H, "#444")
    svg.line(PAD_L, PAD_T + PRICE_H, W - PAD_R, PAD_T + PRICE_H, "#444")

    step = (W - PAD_L - PAD_R) / len(df)
    cw = step * 0.6

    ma20_pts = []
    ma50_pts = []

    for i, r in enumerate(df.itertuples()):
        x = PAD_L + i * step + step / 2

        o, h, l, c = r.Open, r.High, r.Low, r.Close
        color = "#2ca02c" if c >= o else "#d62728"

        # Wick
        svg.line(x, yp(h), x, yp(l), color)

        # Body
        top = yp(max(o, c))
        bh = abs(yp(o) - yp(c))
        svg.rect(x - cw / 2, top, cw, max(bh, 1), color)

        # Volume
        svg.rect(x - cw / 2, yv(r.Volume), cw,
                 VOL_Y + VOL_H - yv(r.Volume), color)

        if not r.MA20 != r.MA20:
            ma20_pts.append(f"{x},{yp(r.MA20)}")
        if not r.MA50 != r.MA50:
            ma50_pts.append(f"{x},{yp(r.MA50)}")

        svg.raw(
            f"<title>{r.DateStr} "
            f"O:{o:.2f} H:{h:.2f} L:{l:.2f} C:{c:.2f} "
            f"V:{int(r.Volume)}</title>"
        )

    # ---- MA Lines ----
    if ma20_pts:
        svg.raw(
            f'<polyline fill="none" stroke="#1f77b4" stroke-width="2" '
            f'points="{" ".join(ma20_pts)}"/>'
        )
        svg.text(W - 180, 50, "MA20", color="#1f77b4")

    if ma50_pts:
        svg.raw(
            f'<polyline fill="none" stroke="#ff7f0e" stroke-width="2" '
            f'points="{" ".join(ma50_pts)}"/>'
        )
        svg.text(W - 180, 70, "MA50", color="#ff7f0e")

    return svg.render()
