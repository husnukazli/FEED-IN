import streamlit as st

st.set_page_config(page_title="Turnuva Sistemi", layout="wide")
st.title("🎾 16'lı Kademeli (Cascading) Feed-In Turnuva")

# Durum yönetimi
if 'players' not in st.session_state: st.session_state.players = [f"Oyuncu {i}" for i in range(1, 17)]
if 'res' not in st.session_state: st.session_state.res = {} # {maç_id: (kazanan, kaybeden)}

def get_match_res(m_id): return st.session_state.res.get(m_id, (None, None))

def match_widget(m_id, p1, p2, label):
    st.markdown(f"**{label}**")
    if not p1 or not p2:
        st.info("⏳ Bekleniyor...")
        return None, None
    
    # Skor ve kazanan seçimi
    winner = st.selectbox(f"Kazanan ({m_id})", ["Seçilmedi", p1, p2], key=f"sel_{m_id}")
    if winner != "Seçilmedi":
        loser = p2 if winner == p1 else p1
        st.session_state.res[m_id] = (winner, loser)
        return winner, loser
    return None, None

# --- TAB'LAR ---
tab1, tab2, tab3 = st.tabs(["👥 Oyuncular", "🏆 Ana Tablo", "🔄 Consolation (Teselli)"])

with tab1:
    txt = st.text_area("16 Oyuncu girin:", value="\n".join(st.session_state.players), height=350)
    if st.button("Kaydet"): st.session_state.players = txt.splitlines()[:16]

# --- ANA TABLO MANTIĞI ---
p = st.session_state.players
with tab2:
    col1, col2, col3 = st.columns(3)
    
    # Round 1
    m_r1 = {}
    with col1:
        for i in range(8):
            w, l = match_widget(f"M_R1_{i}", p[i*2], p[i*2+1], f"Maç {i+1}")
            m_r1[i] = (w, l)
    
    # QF
    m_qf = {}
    with col2:
        for i in range(4):
            w, l = match_widget(f"M_QF_{i}", m_r1[i*2][0], m_r1[i*2+1][0], f"ÇF {i+1}")
            m_qf[i] = (w, l)
            
    # SF
    m_sf = {}
    with col3:
        for i in range(2):
            w, l = match_widget(f"M_SF_{i}", m_qf[i*2][0], m_qf[i*2+1][0], f"YF {i+1}")
            m_sf[i] = (w, l)

# --- CONSOLATION (TESELLİ) MANTIĞI ---
with tab3:
    col_c1, col_c2, col_c3 = st.columns(3)
    
    # 1. Aşama: R1 Kaybedenleri kendi arasında
    c_r1 = {}
    with col_c1:
        st.subheader("Teselli 1. Tur")
        for i in range(4):
            # M_R1_0 ve M_R1_1 kaybedenleri vs M_R1_2 ve M_R1_3 kaybedenleri gibi...
            # Basit eşleştirme: 8 kaybedeni 4 maça sokuyoruz
            p1 = m_r1[i*2][1] if m_r1[i*2][0] else None
            p2 = m_r1[i*2+1][1] if m_r1[i*2+1][0] else None
            w, l = match_widget(f"C_R1_{i}", p1, p2, f"Teselli R1 - Maç {i+1}")
            c_r1[i] = (w, l)

    # 2. Aşama: Consolation Kazananları vs Ana Tablo ÇF Kaybedenleri
    c_sf = {}
    with col_c2:
        st.subheader("Teselli Yarı Final")
        for i in range(2):
            # Burası kritik: Konsolasyon kazananı ile Ana Tablo ÇF kaybedeni buluşuyor
            # Örn: C_R1_0 kazananı ile M_QF_0 kaybedeni
            cons_winner = c_r1[i*2][0] if c_r1[i*2][0] else None
            main_qf_loser = m_qf[i*2][1] if m_qf[i*2][0] else None
            w, l = match_widget(f"C_SF_{i}", cons_winner, main_qf_loser, f"Teselli YF {i+1}")
            c_sf[i] = (w, l)
            
    # 3. Aşama: Teselli Finali (5.-6.lık maçı)
    with col_c3:
        st.subheader("Teselli Finali (5.-6.)")
        p1 = c_sf[0][0] if c_sf[0][0] else None
        p2 = c_sf[1][0] if c_sf[1][0] else None
        winner, loser = match_widget("C_FINAL", p1, p2, "Büyük Final")
        if winner: st.success(f"Teselli Şampiyonu: {winner}")
