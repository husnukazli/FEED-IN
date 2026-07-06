import streamlit as st
import json

st.set_page_config(layout="wide", page_title="Consolation Milli Takım Belirleme")

# --- PROFESYONEL CSS ---
st.markdown("""
    <style>
    .match-box {
        border: 1px solid #4a4a4a;
        padding: 5px;
        border-radius: 4px;
        background-color: #f9f9f9;
        font-size: 10px;
        width: 140px;
        margin-bottom: 5px;
    }
    .col-wrapper {
        display: flex;
        flex-direction: column;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎾 Consolation Milli Takım Belirleme")

# --- DURUM YÖNETİMİ ---
if 'data' not in st.session_state:
    st.session_state.data = {
        'Erkekler': {'players': [f"Oyuncu {i}" for i in range(1, 17)], 'res': {}, 'scores': {}, 'schedule_data': {}},
        'Kadınlar': {'players': [f"Oyuncu {i}" for i in range(1, 17)], 'res': {}, 'scores': {}, 'schedule_data': {}}
    }

active_cat = st.radio("Turnuva Kategorisi:", ["Erkekler", "Kadınlar"], horizontal=True)
cat_data = st.session_state.data[active_cat]

# --- VERİ YÖNETİMİ ---
with st.expander("💾 Veri Yönetimi"):
    col_save, col_load = st.columns(2)
    col_save.download_button("Tüm Veriyi Kaydet (JSON)", data=json.dumps(st.session_state.data), file_name="turnuva_verisi.json")
    uploaded_file = col_load.file_uploader("Dosyayı Yükle", type="json")
    if uploaded_file and col_load.button("Yüklenen Veriyi Uygula"):
        st.session_state.data = json.load(uploaded_file)
        st.rerun()

# --- MAÇ KARTI FONKSİYONU ---
def draw_match(m_id, p1, p2, label):
    st.session_state[f"match_players_{active_cat}_{m_id}"] = (p1, p2)
    st.markdown(f"**{label}**")
    
    # Skor ve Kazanan Girişi
    p1_v = p1 if p1 else "..."
    p2_v = p2 if p2 else "..."
    st.markdown(f'<div class="match-box">{p1_v}<br>{p2_v}</div>', unsafe_allow_html=True)
    
    if p1 and p2:
        current_winner = cat_data['res'].get(m_id, {}).get("w", "-")
        options = ["-", p1, p2]
        idx = options.index(current_winner) if current_winner in options else 0
        winner = st.selectbox(f"W ({m_id})", options, index=idx, key=f"sel_{active_cat}_{m_id}", label_visibility="collapsed")
        score = st.text_input(f"Skor ({m_id})", value=cat_data['scores'].get(m_id, ""), key=f"score_{active_cat}_{m_id}", label_visibility="collapsed")
        cat_data['scores'][m_id] = score
        
        if winner != "-":
            cat_data['res'][m_id] = {"w": winner, "l": (p2 if winner == p1 else p1)}
            return winner, (p2 if winner == p1 else p1)
    return None, None

def spacer(h):
    st.markdown(f'<div style="height:{h}px;"></div>', unsafe_allow_html=True)

# --- TABLAR ---
tab_ana, tab_teselli, tab_siralama, tab_program = st.tabs(["🏆 Ana Tablo", "🔄 Teselli", "📊 Sıralama", "📅 Maç Programı"])

p = cat_data['players']

with tab_ana:
    c1, c2, c3, c4 = st.columns(4)
    # R1 (8 Maç)
    with c1:
        m_r1 = {i: draw_match(f"MR1_{i}", p[i*2], p[i*2+1], f"R1-M{i+1}") for i in range(8)}
    # ÇF (4 Maç - R1'lerin arasına hizalandı)
    with c2:
        spacer(50) 
        m_qf = {}
        for i in range(4):
            m_qf[i] = draw_match(f"MQF_{i}", m_r1[i*2][0], m_r1[i*2+1][0], f"ÇF-M{i+1}")
            spacer(180)
    # YF (2 Maç - ÇF'lerin arasına hizalandı)
    with c3:
        spacer(240)
        m_sf = {}
        for i in range(2):
            m_sf[i] = draw_match(f"MSF_{i}", m_qf[i*2][0], m_qf[i*2+1][0], f"YF-M{i+1}")
            spacer(580)
    # FİNAL
    with c4:
        spacer(550)
        draw_match("FINAL_MAIN", m_sf[0][0], m_sf[1][0], "FİNAL")

with tab_teselli:
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        c_r1 = {i: draw_match(f"CR1_{i}", m_r1[i*2][1], m_r1[i*2+1][1], f"T-R1 M{i+1}") for i in range(4)}
    with c2:
        spacer(50)
        qf_losers = [m_qf[i][1] for i in range(4)][::-1]
        c_r2 = {i: draw_match(f"CR2_{i}", c_r1[i][0], qf_losers[i], f"T-R2 M{i+1}") for i in range(4)}
    with c3:
        spacer(200)
        c_r3 = {i: draw_match(f"CR3_{i}", c_r2[i*2][0], c_r2[i*2+1][0], f"T-R3 M{i+1}") for i in range(2)}
    with c4:
        spacer(400)
        c_r4 = {i: draw_match(f"CR4_{i}", c_r3[i][0], m_sf[i][1], f"T-YF M{i+1}") for i in range(2)}
    with c5:
        spacer(550)
        draw_match("FINAL_TESELLI", c_r4[0][0], c_r4[1][0], "Teselli Finali")
    
    st.divider()
    st.markdown("### 🥉 Klasman")
    k1, k2 = st.columns(2)
    with k1: draw_match("MATCH_7_8", c_r3[0][1] if c_r3[0] else None, c_r3[1][1] if c_r3[1] else None, "7.-8.'lik")
    with k2: draw_match("MATCH_5_6", c_r4[0][1] if c_r4[0] else None, c_r4[1][1] if c_r4[1] else None, "5.-6.'lık")

with tab_siralama:
    st.header("Sıralama")
    res = cat_data['res']
    rankings = [("1.", "FINAL_MAIN", "w"), ("2.", "FINAL_MAIN", "l"), ("3.", "FINAL_TESELLI", "w"), ("4.", "FINAL_TESELLI", "l")]
    for r, m, k in rankings:
        if m in res: st.write(f"{r} {res[m].get(k)}")

with tab_program:
    st.header("📅 Maç Programı")
    def edit_prog(matches, day):
        st.subheader(day)
        cols = st.columns([1, 2, 2, 1, 1, 1])
        cols[0].write("Maç"); cols[1].write("P1"); cols[2].write("P2"); cols[3].write("Saat"); cols[4].write("Kort"); cols[5].write("Skor")
        for m_id, label in matches:
            p1, p2 = st.session_state.get(f"match_players_{active_cat}_{m_id}", ("-", "-"))
            d = cat_data['schedule_data'].get(m_id, {"s": "", "k": "", "sk": ""})
            c = st.columns([1, 2, 2, 1, 1, 1])
            c[0].write(label)
            c[1].write(p1); c[2].write(p2)
            cat_data['schedule_data'][m_id] = {
                "s": c[3].text_input("Saat", d.get("s", ""), key=f"t_{m_id}", label_visibility="collapsed"),
                "k": c[4].text_input("Kort", d.get("k", ""), key=f"c_{m_id}", label_visibility="collapsed"),
                "sk": c[5].text_input("Skor", d.get("sk", ""), key=f"s_{m_id}", label_visibility="collapsed")
            }
    
    edit_prog([(f"CR1_{i}", f"T-R1 M{i+1}") for i in range(4)] + [(f"CR2_{i}", f"T-R2 M{i+1}") for i in range(4)], "1. GÜN")
    edit_prog([(f"CR3_{i}", f"T-R3 M{i+1}") for i in range(2)] + [("MATCH_7_8", "7.-8.'lik Maçı")] + [(f"CR4_{i}", f"T-YF M{i+1}") for i in range(2)], "2. GÜN")
    edit_prog([("FINAL_TESELLI", "Teselli Finali"), ("MATCH_5_6", "5.-6.'lık Maçı")], "3. GÜN")
