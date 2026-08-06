import html as _html
from geometry import compute_main_bracket, compute_consolation_bracket, BOX_H

# YENİ TASARIM: Kutu genişliğini 160'tan 195'e çıkararak uzun isimlere yer açtık!
BOX_W = 195

def _esc(s):
    return _html.escape(str(s)) if s else ""

def _box_svg(x, top, mid, label, match_no, p1, p2, winner, score, bg_color, line_color, text_color, p2_kaynak=None):
    p1n = _esc(p1) if p1 else "Bekleniyor..."
    if p2:
        p2n = _esc(p2)
    else:
        p2n = _esc(f"Bekleniyor... ({p2_kaynak})") if p2_kaynak else "Bekleniyor..."
    b1 = "font-weight:700;" if (winner and p1 and winner == p1) else "fill:#333;"
    b2 = "font-weight:700;" if (winner and p2 and winner == p2) else "fill:#333;"
    title = f'<title>{_esc(score)}</title>' if score else ""
    
    header_bg = f'<path d="M {x+1} {top+6} Q {x+1} {top+1} {x+6} {top+1} L {x+BOX_W-6} {top+1} Q {x+BOX_W-1} {top+1} {x+BOX_W-1} {top+6} L {x+BOX_W-1} {top+25} L {x+1} {top+25} Z" fill="{bg_color}"/>'
    score_html = f'<text x="{x + BOX_W/2}" y="{top + BOX_H + 14}" font-size="12.5" font-weight="bold" fill="#d9534f" text-anchor="middle">{_esc(score)}</text>' if score else ""
    
    return f'<g>{title}<rect x="{x}" y="{top}" width="{BOX_W}" height="{BOX_H}" rx="6" fill="#fff" stroke="#b8b8b8" stroke-width="1.2"/>{header_bg}</g><text x="{x+12}" y="{top+18}" font-size="11.5" font-weight="bold" fill="{text_color}">{label} · M{match_no}</text><line x1="{x}" y1="{top+25}" x2="{x+BOX_W}" y2="{top+25}" stroke="{line_color}" stroke-width="1.2"/><text x="{x+12}" y="{top+44}" font-size="16" style="{b1}">{p1n}</text><text x="{x+12}" y="{top+61}" font-size="16" style="{b2}">{p2n}</text>{score_html}'

# Düz veya Kesik (Dashed) çizgi çizebilen Akıllı Bağlantı Motoru
def _connector(x1, y1, x2, y2, y3, x4, xm=None, dash=""):
    if xm is None:
        xm = (x1 + x4) / 2
    d_str = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{xm}" y2="{y1}" stroke="#b0b0b0" stroke-width="1.5"{d_str}/><line x1="{x1}" y1="{y2}" x2="{xm}" y2="{y2}" stroke="#b0b0b0" stroke-width="1.5"{d_str}/><line x1="{xm}" y1="{y1}" x2="{xm}" y2="{y2}" stroke="#b0b0b0" stroke-width="1.5"{d_str}/><line x1="{xm}" y1="{y3}" x2="{x4}" y2="{y3}" stroke="#b0b0b0" stroke-width="1.5"{d_str}/>'

def render_main_bracket_svg(state, cat_name="Erkekler"):
    if cat_name == "Kadınlar":
        bg_color, line_color, text_color = "#fff0f6", "#ffc9c9", "#a61e4d" 
    else:
        bg_color, line_color, text_color = "#eaf4ff", "#c4ddf5", "#0056b3" 

    g = compute_main_bracket()
    
    # Yeni genişliğe göre X koordinatları
    X_R1, X_QF, X_SF, X_F = 10, 230, 450, 670
    
    parts = []
    for i, m in enumerate(g["r1"]):
        d = state.get(m["id"], {})
        parts.append(_box_svg(X_R1, m["top"], m["center"], "AT-R1", i+1, d.get("p1"), d.get("p2"), d.get("winner"), d.get("score", ""), bg_color, line_color, text_color))
    for j, m in enumerate(g["qf"]):
        d = state.get(m["id"], {})
        parts.append(_box_svg(X_QF, m["top"], m["center"], "AT-ÇF", j+9, d.get("p1"), d.get("p2"), d.get("winner"), d.get("score", ""), bg_color, line_color, text_color))
        r1a, r1b = g["r1"][2*j], g["r1"][2*j+1]
        parts.append(_connector(X_R1+BOX_W, r1a["center"], X_R1+BOX_W, r1b["center"], m["center"], X_QF))
    for k, m in enumerate(g["sf"]):
        d = state.get(m["id"], {})
        parts.append(_box_svg(X_SF, m["top"], m["center"], "AT-YF", k+13, d.get("p1"), d.get("p2"), d.get("winner"), d.get("score", ""), bg_color, line_color, text_color))
        qfa, qfb = g["qf"][2*k], g["qf"][2*k+1]
        parts.append(_connector(X_QF+BOX_W, qfa["center"], X_QF+BOX_W, qfb["center"], m["center"], X_SF))
    d = state.get("FINAL_MAIN", {})
    parts.append(_box_svg(X_F, g["final"]["top"], g["final"]["center"], "AT-FİNAL", 15, d.get("p1"), d.get("p2"), d.get("winner"), d.get("score", ""), bg_color, line_color, text_color))
    parts.append(_connector(X_SF+BOX_W, g["sf"][0]["center"], X_SF+BOX_W, g["sf"][1]["center"], g["final"]["center"], X_F))

    svg_h = g["height"] + 20 
    return f'<div style="overflow-x:auto; -webkit-overflow-scrolling:touch; border:1px solid #eee; border-radius:8px;"><svg viewBox="0 0 880 {svg_h}" width="880" height="{svg_h}">{"".join(parts)}</svg></div>'

def render_consolation_bracket_svg(state, cat_name="Erkekler"):
    if cat_name == "Kadınlar":
        bg_color, line_color, text_color = "#f3f0ff", "#d0bfff", "#5f3dc4" 
    else:
        bg_color, line_color, text_color = "#e8f5e9", "#b2f2bb", "#2b8a3e" 

    main = compute_main_bracket()
    g = compute_consolation_bracket(main)
    
    # Yeni genişliğe göre X koordinatları
    X_R1, X_CF, X_YF1, X_YF2, X_F = 10, 230, 450, 670, 890
    
    parts = []
    for j, m in enumerate(g["t_r1"]):
        d = state.get(m["id"], {})
        parts.append(_box_svg(X_R1, m["top"], m["center"], "FC-R1", j+16, d.get("p1"), d.get("p2"), d.get("winner"), d.get("score", ""), bg_color, line_color, text_color))
    for i, m in enumerate(g["t_cf"]):
        d = state.get(m["id"], {})
        parts.append(_box_svg(X_CF, m["top"], m["center"], "FC-ÇF", i+20, d.get("p1"), d.get("p2"), d.get("winner"), d.get("score", ""), bg_color, line_color, text_color))
        r1 = g["t_r1"][i]
        parts.append(f'<line x1="{X_R1+BOX_W}" y1="{r1["center"]}" x2="{X_CF}" y2="{m["center"]}" stroke="#b0b0b0" stroke-width="1.5"/>')
    for k, m in enumerate(g["t_yf1"]):
        d = state.get(m["id"], {})
        parts.append(_box_svg(X_YF1, m["top"], m["center"], "FC-YF1", k+24, d.get("p1"), d.get("p2"), d.get("winner"), d.get("score", ""), bg_color, line_color, text_color))
        a, b = g["t_cf"][2*k], g["t_cf"][2*k+1]
        parts.append(_connector(X_CF+BOX_W, a["center"], X_CF+BOX_W, b["center"], m["center"], X_YF1))
    for k, m in enumerate(g["t_yf2"]):
        d = state.get(m["id"], {})
        parts.append(_box_svg(X_YF2, m["top"], m["center"], "FC-YF2", k+26, d.get("p1"), d.get("p2"), d.get("winner"), d.get("score", ""), bg_color, line_color, text_color, p2_kaynak=f"M{k+13} Kaybedeni"))
        yf1 = g["t_yf1"][k]
        # YF1'den YF2'ye giden Katı Çizgi (Kazananlar)
        parts.append(f'<line x1="{X_YF1+BOX_W}" y1="{yf1["center"]}" x2="{X_YF2}" y2="{m["center"]}" stroke="#b0b0b0" stroke-width="1.5"/>')

    # --- 3/4, 5/6, 7/8 MAÇLARINI MERKEZE VE ALT ALTA HİZALAMA ---
    toplam_yukseklik = main["height"]
    mac_sayisi = 3
    ara_bosluk = 40
    grup_yuksekligi = (mac_sayisi * BOX_H) + ((mac_sayisi - 1) * ara_bosluk)
    baslangic_y = (toplam_yukseklik - grup_yuksekligi) / 2
    
    pos_3_4 = baslangic_y
    pos_5_6 = baslangic_y + BOX_H + ara_bosluk
    pos_7_8 = baslangic_y + (2 * (BOX_H + ara_bosluk))

    d_34 = state.get("FINAL_TESELLI", {})
    parts.append(_box_svg(X_F, pos_3_4, pos_3_4 + (BOX_H/2), "FC-3/4", 28, d_34.get("p1"), d_34.get("p2"), d_34.get("winner"), d_34.get("score", ""), bg_color, line_color, text_color))

    d_56 = state.get("MATCH_5_6", {})
    parts.append(_box_svg(X_F, pos_5_6, pos_5_6 + (BOX_H/2), "FC-5/6", 29, d_56.get("p1"), d_56.get("p2"), d_56.get("winner"), d_56.get("score", ""), bg_color, line_color, text_color))

    d_78 = state.get("MATCH_7_8", {})
    parts.append(_box_svg(X_F, pos_7_8, pos_7_8 + (BOX_H/2), "FC-7/8", 30, d_78.get("p1"), d_78.get("p2"), d_78.get("winner"), d_78.get("score", ""), bg_color, line_color, text_color))

    # --- BAĞLANTI ÇİZGİLERİNİ GÜNCELLEME (Kayıpsız ve Çakışmasız Geçişler) ---
    a, b = g["t_yf2"][0], g["t_yf2"][1]
    
    # 1. FC-3/4 maçına KATI çizgi (M26 ve M27 KAZANANLARI) - Normal yolundan gidiyor
    parts.append(_connector(X_YF2+BOX_W, a["center"], X_YF2+BOX_W, b["center"], pos_3_4 + (BOX_H/2), X_F, xm=X_YF2+BOX_W+20))
    
    # 2. FC-5/6 maçına KESİK çizgi (M26 ve M27 KAYBEDENLERİ) - Katı çizginin altından ayrılıyor
    parts.append(_connector(X_YF2+BOX_W, a["center"], X_YF2+BOX_W, b["center"], pos_5_6 + (BOX_H/2), X_F, xm=X_YF2+BOX_W+10, dash="5"))

    # 3. FC-7/8 maçına KESİK çizgi (M24 ve M25 KAYBEDENLERİ) 
    # M26/M27 sütununa çarpmamak için iki sütunun tam ortasından dikey aşağı iner ve alt boşluktan geçer
    a1, b1 = g["t_yf1"][0], g["t_yf1"][1]
    parts.append(_connector(X_YF1+BOX_W, a1["center"], X_YF1+BOX_W, b1["center"], pos_7_8 + (BOX_H/2), X_F, xm=X_YF1+BOX_W+10, dash="5"))

    svg_h = max(main["height"], pos_7_8 + BOX_H + 30) 
    return f'<div style="overflow-x:auto; -webkit-overflow-scrolling:touch; border:1px solid #eee; border-radius:8px;"><svg viewBox="0 0 1100 {svg_h}" width="1100" height="{svg_h}">{"".join(parts)}</svg></div>'
