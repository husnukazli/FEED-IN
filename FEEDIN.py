import streamlit as st

st.set_page_config(layout="wide", page_title="Turnuva Fikstürü")
st.title("🎾 Şeffaf Eşleşmeli 16'lı Fikstür")

# --- DURUM YÖNETİMİ ---
if 'players' not in st.session_state:
    st.session_state.players = [f"Oyuncu {i}" for i in range(1, 17)]
if 'results' not in st.session_state:
    st.session_state.results = {} # {match_id: {"w": winner, "l": loser}}

# Görünürlük odaklı maç kartı fonksiyonu
def match_card(m_id, p1, p2, label):
    # Dış çerçeve
    st.markdown(f"""
    <div style="border: 2px solid #ddd; padding: 10px; border-radius: 5px; margin-bottom: 10px; background-color: #f9f9f9;">
        <h5 style="margin:0; font-size: 14px;">{label}</h5>
        <hr style="margin: 5px 0;">
        <div style="font-weight: bold; font-size: 16px;">
            {p1 if p1 else "⏳ Bekleniyor..."} <br>
            <span style="font-size: 12px; font-weight: normal;">vs</span> <br>
            {p2 if p2 else "⏳ Bekleniyor..."}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Seçim alanı (Eğer oyuncular belli ise aktif olur)
    if p1 and p2:
        winner = st.selectbox(f"Kazananı Seç ({label})", ["-", p1, p2], key=f"sel_{m_id}", label_visibility="collapsed")
        if winner != "-":
            loser = p2 if winner == p1 else p1
            st.session_state.results[m_id] = {"w": winner, "l": loser}
            return winner, loser
    
    return None, None

# --- TABLAR ---
tab_p, tab_main, tab_cons = st.tabs(["👥 Oyuncular", "🏆 Ana Tablo", "🔄 Teselli & Feed-In"])

with tab_p:
    txt = st.text_area("16 Oyuncu girin:", value="\n".join(st.session_state.players), height=350)
    if st.button("Oyuncuları Kaydet"):
        st.session_state.players = [p.strip() for p in txt.splitlines() if p.strip()][:16]
        st.rerun()

p = st.session_state.players

# --- ANA TABLO ---
with tab_main:
    col1, col2, col3, col4 = st.columns(4)
    # R1 (8 maç)
    mr1 = {i: match_card(f"MR1_{i}", p[i*2], p[i*2+1], f"Maç {i+1}") for i in range(8)}
    
    with col2:
        st.subheader("Çeyrek Final")
        mqf = {i: match_card(f"MQF_{i}", mr1[i*2][0], mr1[i*2+1][0], f"ÇF {i+1}") for i in range(4)}
    
    with col3:
        st.subheader("Yarı Final")
        msf = {i: match_card(f"MSF_{i}", mqf[i*2][0], mqf[i*2+1][0], f"YF {i+1}") for i in range(2)}
        
    with col4:
        st.subheader("Final")
        match_card("MF", msf[0][0], msf[1][0], "BÜYÜK FİNAL")

# --- CONSOLATION (KADEMELİ) ---
with tab_cons:
    st.info("Ana tablodan elenenler buraya otomatik gelir.")
    c1, c2, c3, c4 = st.columns(4)
    
    # R1 Kaybedenleri -> Teselli R1
    with c1:
        st.subheader("Teselli R1")
        cr1 = {i: match_card(f"CR1_{i}", mr1[i*2][1], mr1[i*2+1][1], f"T-R1 {i+1}") for i in range(4)}
    
    # QF Kaybedenleri -> Teselli QF (TERSTEN SIRALAMA)
    with c2:
        st.subheader("Teselli ÇF")
        qf_losers_reversed = [mqf[i][1] for i in range(3, -1, -1)]
        c_qf = {i: match_card(f"CQF_{i}", cr1[i][0], qf_losers_reversed[i], f"T-ÇF {i+1}") for i in range(4)}
        
    # SF Kaybedenleri -> Teselli YF (Kritik Ekleme)
    with c3:
        st.subheader("Teselli YF")
        sf_losers = [msf[0][1], msf[1][1]]
        c_sf = {
            0: match_card("CSF_0", c_qf[0][0], sf_losers[0], "T-YF 1"),
            1: match_card("CSF_1", c_qf[1][0], sf_losers[1], "T-YF 2")
        }
    
    # Final
    with c4:
        st.subheader("Teselli Finali")
        match_card("CF", c_sf[0][0], c_sf[1][0], "Teselli Şampiyonu")
