import html as _html
from geometry import compute_main_bracket, compute_consolation_bracket, BOX_W, BOX_H

def _esc(s):
    return _html.escape(str(s)) if s else ""

def _box_svg(x, top, mid, label, match_no, p1, p2, winner, score, p2_kaynak=None):
    p1n = _esc(p1) if p1 else "Bekleniyor..."
    if p2:
        p2n = _esc(p2)
    else:
        p2n = _esc(f"Bekleniyor... ({p2_kaynak})") if p2_kaynak else "Bekleniyor..."
    b1 = "font-weight:700;" if (winner and p1 and winner == p1) else "fill:#333;"
    b2 = "font-weight:700;" if (winner and p2 and winner == p2) else "fill:#333;"
    title = f'<title>{_esc(score)}</title>' if score else ""
    
    # Kutu başlığı (FC-YF1 · M24 vb.) için açık mavi (#eaf4ff) ve üst köşeleri yuvarlatılmış özel zemin
    header_bg = f'<path d="M {x+1} {top+6} Q {x+1} {top+1} {x+6} {top+1} L {x+BOX_W-6} {top+1} Q {x+BOX_W-1} {top+1} {x+BOX_W-1} {top+6} L {x+BOX_W-1} {top+25} L {x+1} {top+25} Z" fill="#eaf4ff"/>'
    
    return f'''
    <g>{title}
        <rect x="{x}" y="{top}" width="{BOX_W}" height="{BOX_H}" rx="6" fill="#fff" stroke="#b8b8b8" stroke-width="1.2"/>
        {header_bg}
    </g>
    <text x="{x+12}" y="{top+18}" font-size="11.5" font-weight="bold" fill="#0056b3">{label} · M{match_no}</text>
    <line x1="{x}" y1="{top+25}" x2="{x+BOX_W}" y2="{top+25}" stroke="#c4ddf5" stroke-width="1.2"/>
    <text x="{x+12}" y="{top+44}" font-size="16" style="{b1}">{p1n}</text>
    <text x="{x+12}" y="{top+61}" font-size="16" style="{b2}">{p2n}</text>'''

def _connector(x1, y1, x2, y2, y3, x4, xm=None):
    if xm is None:
        xm = (x1 + x4) / 2
    return f'''
    <line x1="{x1}" y1="{y1}" x2="{xm}" y2="{y1}" stroke="#b0b0b0" stroke-width="1.5"/>
    <line x1="{x1}" y1="{y2}" x2="{xm}" y2="{y2}" stroke="#b0b0b0" stroke-width="1.5"/>
    <line x1="{xm}" y1="{y1}" x2="{xm}" y2="{y2}" stroke="#b0b0b0" stroke-width="1.5"/>
    <line x1="{xm}" y1="{y3}" x2="{x4}" y2="{y3}" stroke="#b0b0b0" stroke-width="1.5"/>'''

def render_main_bracket_svg(state):
    g = compute_main_bracket()
    X_R1, X_QF, X_SF, X_F = 10, 200, 390, 580
    parts = []
    for i, m in enumerate(g["r1"]):
        d = state[m["id"]]
        parts.append(_box_svg(X_R1, m["top"], m["center"], "AT-R1", i+1, d["p1"], d["p2"], d["winner"], d["score"]))
    for j, m in enumerate(g["qf"]):
        d = state[m["id"]]
        parts.append(_box_svg(X_QF, m["top"], m["center"], "AT-ÇF", j+9, d["p1"], d["p2"], d["winner"], d["score"]))
        r1a, r1b = g["r1"][2*j], g["r1"][2*j+1]
        parts.append(_connector(X_R1+BOX_W, r1a["center"], X_R1+BOX_W, r1b["center"], m["center"], X_QF))
    for k, m in enumerate(g["sf"]):
        d = state[m["id"]]
        parts.append(_box_svg(X_SF, m["top"], m["center"], "AT-YF", k+13, d["p1"], d["p2"], d["winner"], d["score"]))
        qfa, qfb = g["qf"][2*k], g["qf"][2*k+1]
        parts.append(_connector(X_QF+BOX_W, qfa["center"], X_QF+BOX_W, qfb["center"], m["center"], X_SF))
    d = state["FINAL_MAIN"]
    parts.append(_box_svg(X_F, g["final"]["top"], g["final"]["center"], "AT-FİNAL", 15, d["p1"], d["p2"], d["winner"], d["score"]))
    parts.append(_connector(X_SF+BOX_W, g["sf"][0]["center"], X_SF+BOX_W, g["sf"][1]["center"], g["final"]["center"], X_F))

    svg_h = g["height"]
    return f'<div style="overflow-x:auto; -webkit-overflow-scrolling:touch; border:1px solid #eee; border-radius:8px;"><svg viewBox="0 0 760 {svg_h}" width="760" height="{svg_h}">{"".join(parts)}</svg></div>'

def render_consolation_bracket_svg(state):
    main = compute_main_bracket()
    g = compute_consolation_bracket(main)
    X_R1, X_CF, X_YF1, X_YF2, X_F = 10, 200, 390, 580, 770
    parts = []
    for j, m in enumerate(g["t_r1"]):
        d = state[m["id"]]
        parts.append(_box_svg(X_R1, m["top"], m["center"], "FC-R1", j+16, d["p1"], d["p2"], d["winner"], d["score"]))
    for i, m in enumerate(g["t_cf"]):
        d = state[m["id"]]
        parts.append(_box_svg(X_CF, m["top"], m["center"], "FC-ÇF", i+20, d["p1"], d["p2"], d["winner"], d["score"]))
        r1 = g["t_r1"][i]
        parts.append(f'<line x1="{X_R1+BOX_W}" y1="{r1["center"]}" x2="{X_CF}" y2="{m["center"]}" stroke="#b0b0b0" stroke-width="1.5"/>')
    for k, m in enumerate(g["t_yf1"]):
        d = state[m["id"]]
        parts.append(_box_svg(X_YF1, m["top"], m["center"], "FC-YF1", k+24, d["p1"], d["p2"], d["winner"], d["score"]))
        a, b = g["t_cf"][2*k], g["t_cf"][2*k+1]
        parts.append(_connector(X_CF+BOX_W, a["center"], X_CF+BOX_W, b["center"], m["center"], X_YF1))
    for k, m in enumerate(g["t_yf2"]):
        d = state[m["id"]]
        parts.append(_box_svg(X_YF2, m["top"], m["center"], "FC-YF2", k+26, d["p1"], d["p2"], d["winner"], d["score"], p2_kaynak=f"M{k+13} Kaybedeni"))
        yf1 = g["t_yf1"][k]
        parts.append(f'<line x1="{X_YF1+BOX_W}" y1="{yf1["center"]}" x2="{X_YF2}" y2="{m["center"]}" stroke="#b0b0b0" stroke-width="1.5"/>')

    labels = [("FINAL_TESELLI", "FC-3/4", 28, g["final_teselli"]),
              ("MATCH_5_6", "FC-5/6", 29, g["m56"]),
              ("MATCH_7_8", "FC-7/8", 30, g["m78"])]
    for mid, lbl, no, m in labels:
        d = state[mid]
        parts.append(_box_svg(X_F, m["top"], m["center"], lbl, no, d["p1"], d["p2"], d["winner"], d["score"]))

    a, b = g["t_yf2"][0], g["t_yf2"][1]
    parts.append(_connector(X_YF2+BOX_W, a["center"], X_YF2+BOX_W, b["center"], g["final_teselli"]["center"], X_F))
    parts.append(_connector(X_YF2+BOX_W, a["center"], X_YF2+BOX_W, b["center"], g["m56"]["center"], X_F))
    a1, b1 = g["t_yf1"][0], g["t_yf1"][1]
    parts.append(_connector(X_YF1+BOX_W, a1["center"], X_YF1+BOX_W, b1["center"], g["m78"]["center"], X_F, xm=X_YF1+BOX_W+15))

    svg_h = max(main["height"], g["m78"]["top"] + BOX_H + 20)
    return f'<div style="overflow-x:auto; -webkit-overflow-scrolling:touch; border:1px solid #eee; border-radius:8px;"><svg viewBox="0 0 940 {svg_h}" width="940" height="{svg_h}">{"".join(parts)}</svg></div>'
