"""
Bracket durumu hesaplama motoru.
Orijinal koddaki match_card() cagri sirasindaki p1/p2 turetme mantigini
BIREBIR izler, ama Streamlit arayuzune bagli degildir -- sadece veri uretir.
Hem SVG hem PDF ciziciler bu fonksiyonun ciktisini kullanir, boylece
ekran ve PDF ayni veriden beslenir, asla birbirinden sapmaz.
"""

def _res(cat_data, m_id):
    r = cat_data['res'].get(m_id)
    if not r:
        return None, None
    return r.get('w'), r.get('l')


def compute_bracket_state(cat_data):
    """
    Donen sozluk: match_id -> {p1, p2, winner, loser, score}
    Orijinal koddaki AYNI besleme sirasini izler:
      R1 (oyuncu listesinden) -> QF -> SF -> FINAL_MAIN
      T-R1 (R1 kaybedenleri)  -> T-CF (T-R1 kazananlari + ters sirali QF kaybedenleri)
      -> T-YF1 -> T-YF2 (+ SF kaybedenleri) -> FINAL_TESELLI / MATCH_5_6 / MATCH_7_8
    """
    players = cat_data['players']
    state = {}

    def put(m_id, p1, p2):
        w, l = _res(cat_data, m_id)
        state[m_id] = {
            "p1": p1, "p2": p2,
            "winner": w, "loser": l,
            "score": cat_data['scores'].get(m_id, ""),
        }
        
        # ÇİFT WO (Hepsi WO) DURUMU İÇİN ÖZEL KONTROL:
        # Eğer iki oyuncu da gelmemişse, bu maçın hem kazananı hem kaybedeni "Hepsi WO" olarak
        # alt tablolara (Teselli ve sonraki turlara) iletilmeli.
        if w == "Hepsi WO":
            return ("Hepsi WO", "Hepsi WO")
            
        # Normal şartlarda kazanan w ise, kaybedeni p1 ve p2 arasından bul
        return (w, p2 if w == p1 else (p1 if w == p2 else None)) if w else (None, None)

    # --- Ana tablo ---
    r1_out = []
    for i in range(8):
        p1, p2 = players[i * 2], players[i * 2 + 1]
        r1_out.append(put(f"MR1_{i}", p1, p2))

    qf_out = []
    for j in range(4):
        p1, _ = r1_out[2 * j]
        p2, _ = r1_out[2 * j + 1]
        qf_out.append(put(f"MQF_{j}", p1, p2))

    sf_out = []
    for k in range(2):
        p1, _ = qf_out[2 * k]
        p2, _ = qf_out[2 * k + 1]
        sf_out.append(put(f"MSF_{k}", p1, p2))

    p1, _ = sf_out[0]
    p2, _ = sf_out[1]
    put("FINAL_MAIN", p1, p2)

    # --- Teselli (consolation) tablosu ---
    t_r1_out = []
    for j in range(4):
        _, l1 = r1_out[2 * j]
        _, l2 = r1_out[2 * j + 1]
        t_r1_out.append(put(f"CR1_{j}", l1, l2))

    qf_losers_reversed = [qf_out[3][1], qf_out[2][1], qf_out[1][1], qf_out[0][1]]
    t_cf_out = []
    for i in range(4):
        w_prev, _ = t_r1_out[i]
        t_cf_out.append(put(f"CR2_{i}", w_prev, qf_losers_reversed[i]))

    t_yf1_out = []
    for k in range(2):
        p1, _ = t_cf_out[2 * k]
        p2, _ = t_cf_out[2 * k + 1]
        t_yf1_out.append(put(f"CR3_{k}", p1, p2))

    t_yf2_out = []
    for k in range(2):
        w_prev, _ = t_yf1_out[k]
        _, sf_loser = sf_out[k]
        t_yf2_out.append(put(f"CR4_{k}", w_prev, sf_loser))

    p1, _ = t_yf2_out[0]; p2, _ = t_yf2_out[1]
    put("FINAL_TESELLI", p1, p2)

    _, l1 = t_yf2_out[0]; _, l2 = t_yf2_out[1]
    put("MATCH_5_6", l1, l2)

    _, l1 = t_yf1_out[0]; _, l2 = t_yf1_out[1]
    put("MATCH_7_8", l1, l2)

    return state
