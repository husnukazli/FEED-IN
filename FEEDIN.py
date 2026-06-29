
import streamlit as st

st.set_page_config(page_title="Turnuva Sistemi", layout="wide")
st.title("🎾 16'lı Kademeli (Cascading) Turnuva Sistemi")

# --- DURUM YÖNETİMİ ---
if 'players' not in st.session_state:
    st.session_state.players = [f"Oyuncu {i}" for i in range(1, 17)]
if 'winners' not in st.session_state: st.session_state.winners = {}
if 'scores' not in st.session_state: st.session_state.scores = {}

# Yardımcı fonksiyon: Maç kartı
def match_card(m_id, p1, p2, label):
    st.markdown(f"**{label}**")
    if not p1 or not p2:
        st.write("⏳ *Bekleniyor...*")
        return None, None
    
    # Skor ve kazanan seçimi
    options = ["-", p1, p2]
    current = st.session_state.winners.get(m_id, "-")
    idx = options.index(current) if current in options else 0
    
    w = st.selectbox(f"Kazanan ({m_id})", options, index=idx, key=f"sel_{m_id}", label_visibility="collapsed")
    score = st.text_input("Skor", value=st.session_state.scores.get(m_id, ""), key=f"score_{m_id}", label_visibility="collapsed")
    
    if w != "-":
        l = p2 if w == p1 else p1
        st.session_state.winners[m_id] = w
        st.session_state.scores[m_id] = score
        return w, l
    return None, None

# --- SEKMELER ---
tab_players, tab_main, tab_cons = st.tabs(["👥 Oyuncular", "🏆 Ana Tablo", "🔄 Consolation (Feed-In)"])

with tab_players:
    txt = st.text_area("16 Oyuncu girin (Alt alta):", value="\n".join(st.session_state.players), height=350)
    if st.button("Oyuncuları Kaydet"):
        st.session_state.players = [p.strip() for p in txt.splitlines() if p.strip()][:16]
        st.rerun()

p = st.session_state.players

# --- ANA TABLO ---
with tab_main:
    col1, col2, col3, col4 = st.columns(4)
    # R1: 8 Maç
    m_r1_w, m_r1_l = {}, {}
    with col1:
        st.subheader("R1 (16'lı)")
        for i in range(8):
            m_r1_w[i], m_r1_l[i] = match_card(f"MR1_{i}", p[i*2], p[i*2+1], f"Maç {i+1}")
    
    # QF: 4 Maç
    m_qf_w, m_qf_l = {}, {}
    with col2:
        st.subheader("Çeyrek Final")
        for i in range(4):
            m_qf_w[i], m_qf_l[i] = match_card(f"MQF_{i}", m_r1_w.get(i*2), m_r1_w.get(i*2+1), f"ÇF {i+1}")

    # SF: 2 Maç
    m_sf_w, m_sf_l = {}, {}
    with col3:
        st.subheader("Yarı Final")
        for i in range(2):
            m_sf_w[i], m_sf_l[i] = match_card(f"MSF_{i}", m_qf_w.get(i*2), m_qf_w.get(i*2+1), f"YF {i+1}")

    # Final
    with col4:
        st.subheader("Final")
        winner, loser = match_card("MF", m_sf_w.get(0), m_sf_w.get(1), "ŞAMPİYONLUK")

# --- CONSOLATION (TESELLİ) ---
with tab_cons:
    st.info("Ana tablodan elenenler buraya aktarılır.")
    c_col1, c_col2, c_col3, c_col4 = st.columns(4)
    
    # 1. Tur: Ana tablo R1 kaybedenleri
    c_r1_w, c_r1_l = {}, {}
    with c_col1:
        st.subheader("Teselli R1")
        for i in range(4):
            c_r1_w[i], c_r1_l[i] = match_card(f"CR1_{i}", m_r1_l.get(i*2), m_r1_l.get(i*2+1), f"T-R1 Maç {i+1}")
            
    # 2. Tur: Feed-In (TERSTEN SIRALAMA)
    # Mantık: Teselli R1 kazananları vs Ana Tablo ÇF kaybedenleri (Tersten)
    c_qf_w, c_qf_l = {}, {}
    with c_col2:
        st.subheader("Feed-In (Çeyrek Final)")
        # m_qf_l listesini tersine çeviriyoruz (4, 3, 2, 1)
        qf_losers_reversed = [m_qf_l.get(3), m_qf_l.get(2), m_qf_l.get(1), m_qf_l.get(0)]
        for i in range(4):
            c_qf_w[i], c_qf_l[i] = match_card(f"CQF_{i}", c_r1_w.get(i), qf_losers_reversed[i], f"T-ÇF Maç {i+1}")

    # 3. Tur: Yarı Final (Teselli QF kazananları vs Ana Tablo YF kaybedenleri)
    c_sf_w, c_sf_l = {}, {}
    with c_col3:
        st.subheader("Teselli Yarı Final")
        # Basit eşleştirme: QF kazananları kendi aralarında
        for i in range(2):
            c_sf_w[i], c_sf_l[i] = match_card(f"CSF_{i}", c_qf_w.get(i*2), c_qf_w.get(i*2+1), f"T-YF Maç {i+1}")
    
    # Final ve Klasman
    with c_col4:
        st.subheader("Klasman Maçları")
        # 5.-6. Lık
        winner56, loser56 = match_card("C_5_6", c_sf_w.get(0), c_sf_w.get(1), "5. - 6. Lık Maçı")
        
        # 7.-8. Lik
        winner78, loser78 = match_card("C_7_8", c_sf_l.get(0), c_sf_l.get(1), "7. - 8. Lik Maçı")
