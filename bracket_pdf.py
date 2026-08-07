import html as _html
from geometry import compute_main_bracket, compute_consolation_bracket, BOX_H

BOX_W = 195

def _set_font(pdf, font_family, bold, size):
    pdf.set_font(font_family, 'B' if bold else "", size)

def _draw_box(pdf, scale, ox, oy, x, top, label, match_no, p1, p2, winner, to_pdf_text, font_family, score="", bg_color=None):
    if p1 == "Hepsi WO": p1 = "Çift W/O" 
    if p2 == "Hepsi WO": p2 = "Çift W/O"
    
    bx, by = ox + x * scale, oy + top * scale
    bw, bh = BOX_W * scale, BOX_H * scale
    
    pdf.set_fill_color(255, 255, 255)
    pdf.set_draw_color(160, 160, 160)
    pdf.rect(bx, by, bw, bh, 'DF')

    if bg_color:
        pdf.set_fill_color(*bg_color)
        pdf.rect(bx, by, bw, bh * 0.3, 'F')

    _set_font(pdf, font_family, True, 8)  
    pdf.set_xy(bx + 1.5, by + 1.5)
    pdf.set_text_color(50, 50, 50)  
    pdf.cell(bw - 3, 4, to_pdf_text(f"{label} - M{match_no}"), ln=0)
    
    name1 = to_pdf_text(p1) if p1 else to_pdf_text("Bekleniyor...")
    name2 = to_pdf_text(p2) if p2 else to_pdf_text("Bekleniyor...")
    
    # Hepsi WO ise isimleri gri yaz, yoksa kazananı kalın yaz
    if winner == "Hepsi WO":
        pdf.set_text_color(140, 140, 140)
        _set_font(pdf, font_family, False, 9) 
        pdf.set_xy(bx + 1.5, by + bh * 0.40)
        pdf.cell(bw - 3, 5, name1, ln=0)
        pdf.set_xy(bx + 1.5, by + bh * 0.68)
        pdf.cell(bw - 3, 5, name2, ln=0)
    else:
        pdf.set_text_color(0, 0, 0)
        _set_font(pdf, font_family, bool(winner and p1 and winner == p1), 9) 
        pdf.set_xy(bx + 1.5, by + bh * 0.40)
        pdf.cell(bw - 3, 5, name1, ln=0)
        
        _set_font(pdf, font_family, bool(winner and p2 and winner == p2), 9) 
        pdf.set_xy(bx + 1.5, by + bh * 0.68)
        pdf.cell(bw - 3, 5, name2, ln=0)
    
    if score:
        _set_font(pdf, font_family, True, 8)
        pdf.set_text_color(80, 80, 80)
        pdf.set_xy(bx, by + bh + 0.5)
        pdf.cell(bw, 4, to_pdf_text(score), ln=0, align='C')

def _draw_dashed_line(pdf, x1, y1, x2, y2, dash_length=1.5, space_length=1.5):
    import math
    dist = math.hypot(x2 - x1, y2 - y1)
    if dist == 0: return
    dashes = int(dist / (dash_length + space_length))
    for i in range(dashes):
        start_x = x1 + (x2 - x1) * (i * (dash_length + space_length)) / dist
        start_y = y1 + (y2 - y1) * (i * (dash_length + space_length)) / dist
        end_x = x1 + (x2 - x1) * (i * (dash_length + space_length) + dash_length) / dist
        end_y = y1 + (y2 - y1) * (i * (dash_length + space_length) + dash_length) / dist
        pdf.line(start_x, start_y, end_x, end_y)

def _draw_connector(pdf, scale, ox, oy, x1, y1, y2, y3, x4, xm=None, dashed=False):
    pdf.set_draw_color(176, 176, 176)
    if xm is None: xm = (x1 + x4) / 2
    def pt(x, y): return (ox + x * scale, oy + y * scale)
    a = pt(x1, y1); b = pt(xm, y1); c = pt(xm, y2); d = pt(x1, y2); e = pt(xm, y3); f = pt(x4, y3)
    if dashed:
        _draw_dashed_line(pdf, a[0], a[1], b[0], b[1])
        _draw_dashed_line(pdf, d[0], d[1], c[0], c[1])
        _draw_dashed_line(pdf, b[0], b[1], c[0], c[1])
        _draw_dashed_line(pdf, e[0], e[1], f[0], f[1])
    else:
        pdf.line(*a, *b); pdf.line(*d, *c); pdf.line(*b, *c); pdf.line(*e, *f)

def draw_bracket_page(pdf, state, section, cat_name, to_pdf_text, font_family, page_w=297, page_h=210):
    main = compute_main_bracket()
    _set_font(pdf, font_family, True, 13)
    pdf.set_xy(10, 8)
    pdf.cell(0, 8, to_pdf_text(f"{cat_name} - {'Ana Tablo' if section == 'main' else 'FEED IN Tablosu'}"), ln=True)

    ox, oy = 10, 20
    avail_w, avail_h = page_w - 20, page_h - 30
    bg_main, bg_cons = ((255, 240, 246), (243, 240, 255)) if cat_name == "Kadınlar" else ((234, 244, 255), (232, 245, 233))

    if section == "main":
        svg_w, svg_h = 880, main["height"]
        scale = min(avail_w / svg_w, avail_h / svg_h)
        X_R1, X_QF, X_SF, X_F = 10, 230, 450, 670

        for i, m in enumerate(main["r1"]):
            d = state.get(m["id"], {}); _draw_box(pdf, scale, ox, oy, X_R1, m["top"], "AT-R1", i + 1, d.get("p1"), d.get("p2"), d.get("winner"), to_pdf_text, font_family, d.get("score", ""), bg_main)
        for j, m in enumerate(main["qf"]):
            d = state.get(m["id"], {}); _draw_box(pdf, scale, ox, oy, X_QF, m["top"], "AT-ÇF", j + 9, d.get("p1"), d.get("p2"), d.get("winner"), to_pdf_text, font_family, d.get("score", ""), bg_main)
            a, b = main["r1"][2*j], main["r1"][2*j+1]; _draw_connector(pdf, scale, ox, oy, X_R1+BOX_W, a["center"], b["center"], m["center"], X_QF)
        for k, m in enumerate(main["sf"]):
            d = state.get(m["id"], {}); _draw_box(pdf, scale, ox, oy, X_SF, m["top"], "AT-YF", k + 13, d.get("p1"), d.get("p2"), d.get("winner"), to_pdf_text, font_family, d.get("score", ""), bg_main)
            a, b = main["qf"][2*k], main["qf"][2*k+1]; _draw_connector(pdf, scale, ox, oy, X_QF+BOX_W, a["center"], b["center"], m["center"], X_SF)
        d = state.get("FINAL_MAIN", {})
        _draw_box(pdf, scale, ox, oy, X_F, main["final"]["top"], "AT-FİNAL", 15, d.get("p1"), d.get("p2"), d.get("winner"), to_pdf_text, font_family, d.get("score", ""), bg_main)
        _draw_connector(pdf, scale, ox, oy, X_SF+BOX_W, main["sf"][0]["center"], main["sf"][1]["center"], main["final"]["center"], X_F)

    else:
        g = compute_consolation_bracket(main)
        toplam_y = main["height"]
        grup_h = (3 * BOX_H) + 80
        scale = min(avail_w / 1100, avail_h / max(toplam_y, (toplam_y - grup_h) / 2 + grup_h + 30))
        X_R1, X_CF, X_YF1, X_YF2, X_F = 10, 230, 450, 670, 890

        for j, m in enumerate(g["t_r1"]):
            d = state.get(m["id"], {}); _draw_box(pdf, scale, ox, oy, X_R1, m["top"], "FC-R1", j + 16, d.get("p1"), d.get("p2"), d.get("winner"), to_pdf_text, font_family, d.get("score", ""), bg_cons)
        for i, m in enumerate(g["t_cf"]):
            d = state.get(m["id"], {}); _draw_box(pdf, scale, ox, oy, X_CF, m["top"], "FC-ÇF", i + 20, d.get("p1"), d.get("p2"), d.get("winner"), to_pdf_text, font_family, d.get("score", ""), bg_cons)
            pdf.set_draw_color(176, 176, 176); pdf.line(ox+(X_R1+BOX_W)*scale, oy+g["t_r1"][i]["center"]*scale, ox+X_CF*scale, oy+m["center"]*scale)
        for k, m in enumerate(g["t_yf1"]):
            d = state.get(m["id"], {}); _draw_box(pdf, scale, ox, oy, X_YF1, m["top"], "FC-YF1", k + 24, d.get("p1"), d.get("p2"), d.get("winner"), to_pdf_text, font_family, d.get("score", ""), bg_cons)
            a, b = g["t_cf"][2*k], g["t_cf"][2*k+1]; _draw_connector(pdf, scale, ox, oy, X_CF+BOX_W, a["center"], b["center"], m["center"], X_YF1)
        for k, m in enumerate(g["t_yf2"]):
            d = state.get(m["id"], {}); _draw_box(pdf, scale, ox, oy, X_YF2, m["top"], "FC-YF2", k + 26, d.get("p1"), d.get("p2"), d.get("winner"), to_pdf_text, font_family, d.get("score", ""), bg_cons)
            pdf.set_draw_color(176, 176, 176); pdf.line(ox+(X_YF1+BOX_W)*scale, oy+g["t_yf1"][k]["center"]*scale, ox+X_YF2*scale, oy+m["center"]*scale)

        baslangic_y = (toplam_y - grup_h) / 2
        pos_3_4, pos_5_6, pos_7_8 = baslangic_y, baslangic_y + BOX_H + 40, baslangic_y + (2 * (BOX_H + 40))

        d_34 = state.get("FINAL_TESELLI", {})
        _draw_box(pdf, scale, ox, oy, X_F, pos_3_4, "FC-3/4", 28, d_34.get("p1"), d_34.get("p2"), d_34.get("winner"), to_pdf_text, font_family, d_34.get("score", ""), bg_cons)
        d_56 = state.get("MATCH_5_6", {})
        _draw_box(pdf, scale, ox, oy, X_F, pos_5_6, "FC-5/6", 29, d_56.get("p1"), d_56.get("p2"), d_56.get("winner"), to_pdf_text, font_family, d_56.get("score", ""), bg_cons)
        d_78 = state.get("MATCH_7_8", {})
        _draw_box(pdf, scale, ox, oy, X_F, pos_7_8, "FC-7/8", 30, d_78.get("p1"), d_78.get("p2"), d_78.get("winner"), to_pdf_text, font_family, d_78.get("score", ""), bg_cons)

        a, b = g["t_yf2"][0], g["t_yf2"][1]
        _draw_connector(pdf, scale, ox, oy, X_YF2+BOX_W, a["center"], b["center"], pos_3_4 + (BOX_H/2), X_F, xm=X_YF2+BOX_W+20)
        _draw_connector(pdf, scale, ox, oy, X_YF2+BOX_W, a["center"], b["center"], pos_5_6 + (BOX_H/2), X_F, xm=X_YF2+BOX_W+10, dashed=True)
        a1, b1 = g["t_yf1"][0], g["t_yf1"][1]
        _draw_connector(pdf, scale, ox, oy, X_YF1+BOX_W, a1["center"], b1["center"], pos_7_8 + (BOX_H/2), X_F, xm=X_YF1+BOX_W+10, dashed=True)

def generate_bracket_pdf(cat_data, cat_name, FPDF, to_pdf_text, font_yuklendi):
    from bracket_engine import compute_bracket_state
    state = compute_bracket_state(cat_data)
    font_family = "ArialTR" if font_yuklendi else "Arial"
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.set_auto_page_break(False)
    pdf.add_page(); draw_bracket_page(pdf, state, "main", cat_name, to_pdf_text, font_family)
    pdf.add_page(); draw_bracket_page(pdf, state, "consolation", cat_name, to_pdf_text, font_family)
    return bytes(pdf.output())
