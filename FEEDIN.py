import streamlit as st
import json

st.set_page_config(layout="wide", page_title="Turnuva Fikstürü")

# --- PROFESYONEL CSS ---
st.markdown("""
    <style>
    /* Turnuva Tablosu Konteynırı */
    .bracket-container {
        display: flex;
        flex-direction: row;
        gap: 15px;
        align-items: flex-start;
        padding: 10px;
    }
    /* Sütunlar dikeyde hizalanır */
    .col-bracket {
        display: flex;
        flex-direction: column;
        justify-content: space-around;
        height: 800px; /* Sabit yükseklik, dikey simetriyi sağlar */
        width: 180px;
    }
    /* Maç Kartı */
    .match-card {
        border: 1px solid #333;
        padding: 5px;
        background: #fff;
        border-radius: 2px;
        font-size: 10px;
        margin: 5px 0;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎾 Profesyonel Turnuva Fikstürü")

# --- DURUM YÖNETİMİ ---
if 'data' not in st.session_state:
    st.session_state.data = {
        'Erkekler': {'players': [f"Oyuncu {i}" for i in range(1, 17)], 'res': {}, 'scores': {}, 'schedule_data': {}},
        'Kadınlar': {'players': [f"Oyuncu {i}" for i in range(1, 17)], 'res': {}, 'scores': {}, 'schedule_data': {}}
    }

active_cat = st.radio("Kategori:", ["Erkekler", "Kadınlar"], horizontal=True)
cat_data = st.session_state.data[active_cat]

# --- VERİ YÖNETİMİ ---
with st.expander("💾 Veri Yönetimi"):
    col_save, col_load = st.columns(2)
    col_save.download_button("Kaydet (JSON)", data=json.dumps(st.session_state.data), file_name="turnuva.json")
    uploaded = col_load.file_uploader("Yükle", type="json")
    if uploaded and col_load.button("Uygula"):
        st.session_state.data = json.load(uploaded)
        st.rerun()

# --- MAÇ KARTI FONKSİYONU ---
def draw_match_box(m_id, p1, p2, label):
    st.session_state[f"match_players_{active_cat}_{m_id}"] = (p1, p2)
    st.markdown(f"**{label}**")
    p1_val = p1 if p1 else "..."
    p2_val = p2 if p2 else "..."
    
    # Görünüm
    st.markdown(f'<div class="match-card">{p1_val}<br>{p2_val}</div>', unsafe_allow_html=True)
    
    # Girişler
    if p1 and p2:
        res = cat_data['res'].get(m_id, {})
        options = ["-", p1, p2]
        current = res.get("w", "-")
        winner = st.selectbox(f"W-{m_id}", options, index=options.index(current) if current in options else 0, key=f"sel_{active_cat}_{m_id}", label_visibility="collapsed")
        score = st.text_input(f"S-{m_id}", value=cat_data['scores'].get(m_id, ""), key=f"score_{active_cat}_{m_id}", label_visibility="collapsed")
        
        cat_data['scores'][m_id] = score
        if winner != "-":
            cat_data['res'][m_id] = {"w": winner, "l": (p2 if winner == p1 else p1)}
    return cat_data['res'].get(m_id, {}).get("w"), cat_data['res'].get(m_id, {}).get("l")

# --- TABS ---
tab_ana, tab_teselli = st.tabs(["🏆 Ana Tablo", "🔄 Teselli"])

p = cat_data['players']

with tab_ana:
    cols = st.columns(4)
    # R1
    with cols[0]:
        m_r1 = {i: draw_match_box(f"MR1_{i}", p[i*2], p[i*2+1], f"R1-M{i+1}") for i in range(8)}
    # ÇF
    with cols[1]:
        m_qf = {i: draw_match_box(f"MQF_{i}", m_r1[i*2][0], m_r1[i*2+1][0], f"ÇF-M{i+1}") for i in range(4)}
    # YF
    with cols[2]:
        m_sf = {i: draw_match_box(f"MSF_{i}", m_qf[i*2][0], m_qf[i*2+1][0], f"YF-M{i+1}") for i in range(2)}
    # FİNAL
    with cols[3]:
        draw_match_box("FINAL_MAIN", m_sf[0][0], m_sf[1][0], "FİNAL")

with tab_teselli:
    cols = st.columns(5)
    # T-R1
    with cols[0]:
        c_r1 = {i: draw_match_box(f"CR1_{i}", m_r1[i*2][1], m_r1[i*2+1][1], f"T-R1 M{i+1}") for i in range(4)}
    # T-R2
    with cols[1]:
        qf_losers_rev = [m_qf[3][1], m_qf[2][1], m_qf[1][1], m_qf[0][1]]
        c_r2 = {i: draw_match_box(f"CR2_{i}", c_r1[i][0], qf_losers_rev[i], f"T-R2 M{i+1}") for i in range(4)}
    # T-R3
    with cols[2]:
        c_r3 = {i: draw_match_box(f"CR3_{i}", c_r2[i*2][0], c_r2[i*2+1][0], f"T-R3 M{i+1}") for i in range(2)}
    # T-YF
    with cols[3]:
        c_r4 = {i: draw_match_box(f"CR4_{i}", c_r3[i][0], m_sf[i][1], f"T-YF M{i+1}") for i in range(2)}
    # T-FİNAL
    with cols[4]:
        draw_match_box("FINAL_TESELLI", c_r4[0][0], c_r4[1][0], "Teselli Finali")

    st.divider()
    st.subheader("🥉 Klasman Maçları")
    k1, k2 = st.columns(2)
    with k1: draw_match_box("MATCH_7_8", c_r3[0][1] if c_r3[0] else None, c_r3[1][1] if c_r3[1] else None, "7.-8.'lik")
    with k2: draw_match_box("MATCH_5_6", c_r4[0][1] if c_r4[0] else None, c_r4[1][1] if c_r4[1] else None, "5.-6.'lık")
