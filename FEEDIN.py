import streamlit as st

st.set_page_config(layout="wide", page_title="Profesyonel Turnuva Fikstürü")
st.title("🎾 16'lı Kademeli (Cascading) Teselli Fikstürü")

# --- DURUM YÖNETİMİ ---
if 'players' not in st.session_state: st.session_state.players = [f"Oyuncu {i}" for i in range(1, 17)]
if 'matches' not in st.session_state: st.session_state.matches = {}

def get_match(m_id): return st.session_state.matches.get(m_id, {"winner": None, "loser": None})

def match_box(m_id, p1, p2, label):
    st.markdown(f"**{label}**")
    name1 = p1 if p1 else "⏳ Bekleniyor"
    name2 = p2 if p2 else "⏳ Bekleniyor"
    
    # Eşleşme gösterimi
    col_a, col_b = st.columns(2)
    col_a.write(f"1: {name1}")
    col_b.write(f"2: {name2}")
    
    winner = None
    if p1 and p2:
        winner = st.selectbox(f"Kazanan ({m_id})", ["Seçilmedi", p1, p2], key=f"sel_{m_id}")
        if winner != "Seçilmedi":
            loser = p2 if winner == p1 else p1
            st.session_state.matches[m_id] = {"winner": winner, "loser": loser}
            return winner, loser
    return None, None

# --- TAB'LAR ---
tab1, tab2, tab3 = st.tabs(["👥 Oyuncular", "🏆 Ana Tablo", "🔄 Consolation (Teselli)"])

with tab1:
    txt = st.text_area("16 Oyuncu girin (Alt alta):", value="\n".join(st.session_state.players), height=350)
    if st.button("Oyuncuları Kaydet"): st.session_state.players = txt.splitlines()[:16]

p = st.session_state.players

# --- ANA TABLO ---
with tab2:
    st.subheader("Ana Tablo İlerlemesi")
    # R1 (8 maç)
    m_r1 = {i: match_box(f"M_R1_{i}", p[i*2], p[i*2+1], f"Ana R1-Maç {i+1}") for i in range(8)}
    # QF (4 maç)
    m_qf = {i: match_box(f"M_QF_{i}", m_r1[i*2][0], m_r1[i*2+1][0], f"Ana ÇF-Maç {i+1}") for i in range(4)}
    # SF (2 maç)
    m_sf = {i: match_box(f"M_SF_{i}", m_qf[i*2][0], m_qf[i*2+1][0], f"Ana YF-Maç {i+1}") for i in range(2)}
    # Final (1 maç)
    m_f = match_box("M_F", m_sf[0][0], m_sf[1][0], "BÜYÜK FİNAL")

# --- CONSOLATION (KADEMELİ) ---
with tab3:
    st.subheader("Consolation (Her turda beslenen tablo)")
    
    # 1. Aşama: R1 Kaybedenleri (8 kişi -> 4 maç)
    c_r1 = {i: match_box(f"C_R1_{i}", m_r1[i*2][1], m_r1[i*2+1][1], f"Teselli R1-Maç {i+1}") for i in range(4)}
    
    # 2. Aşama: C_R1 Kazananları + QF Kaybedenleri (4+4 = 8 kişi -> 4 maç)
    # Burada Ana tablodan QF kaybedenlerini içeri alıyoruz (Feed-in)
    c_r2 = {}
    for i in range(4):
        p1 = c_r1[i][0]
        p2 = m_qf[i][1] # Ana tablodan gelen taze kaybeden
        c_r2[i] = match_box(f"C_R2_{i}", p1, p2, f"Teselli R2-Maç {i+1}")

    # 3. Aşama: C_R2 Kazananları + SF Kaybedenleri (4+2 = 6 kişi -> 3 maç)
    # SF kaybedenleri burada devreye giriyor
    c_sf = {}
    # 1. Yarı final: C_R2[0] ve C_R2[1] kazananları kendi aralarında
    c_sf[0] = match_box("C_SF_0", c_r2[0][0], c_r2[1][0], "Teselli YF 1")
    # 2. Yarı final: C_R2[2] ve C_R2[3] kazananları kendi aralarında
    c_sf[1] = match_box("C_SF_1", c_r2[2][0], c_r2[3][0], "Teselli YF 2")
    # 3. Yarı final (Kalanlar): SF kaybedenleri doğrudan buraya "besleniyor"
    c_sf[2] = match_box("C_SF_2", m_sf[0][1], m_sf[1][1], "Teselli Ekstra Maç")

    # Final
    st.subheader("Teselli Şampiyonluğu")
    match_box("C_FINAL", c_sf[0][0], c_sf[1][0], "Teselli Finali")
