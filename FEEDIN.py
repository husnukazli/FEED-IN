import streamlit as st

st.set_page_config(layout="wide", page_title="Turnuva Sistemi")
st.title("🎾 Profesyonel 16'lı Kademeli (Cascading) Turnuva")

# Durum yönetimi
if 'players' not in st.session_state:
    st.session_state.players = [f"Oyuncu {i}" for i in range(1, 17)]
if 'res' not in st.session_state: st.session_state.res = {}

def get_match_res(m_id):
    return st.session_state.res.get(m_id, {"w": None, "l": None})

def match_card(m_id, p1, p2, label):
    st.markdown(f"**{label}**")
    name1 = p1 if p1 else "⏳ Bekleniyor"
    name2 = p2 if p2 else "⏳ Bekleniyor"
    
    # Görsel Kart
    st.markdown(f"""
    <div style="border: 1px solid #ccc; padding: 8px; border-radius: 5px; margin-bottom: 10px;">
        {name1} vs {name2}
    </div>
    """, unsafe_allow_html=True)
    
    if p1 and p2:
        winner = st.selectbox(f"Kazanan ({m_id})", ["-", p1, p2], key=f"sel_{m_id}", label_visibility="collapsed")
        if winner != "-":
            loser = p2 if winner == p1 else p1
            st.session_state.res[m_id] = {"w": winner, "l": loser}
            return winner, loser
    return None, None

# 1. Oyuncu Girişi
with st.expander("👥 16 Oyuncu Listesi"):
    txt = st.text_area("Oyuncuları girin:", value="\n".join(st.session_state.players), height=150)
    if st.button("Kaydet"):
        st.session_state.players = [p.strip() for p in txt.splitlines() if p.strip()]
        st.rerun()
p = st.session_state.players

# 2. ANA TABLO
st.subheader("🏆 Ana Tablo")
col1, col2, col3 = st.columns(3)
with col1:
    m_r1 = {i: match_card(f"MR1_{i}", p[i*2], p[i*2+1], f"Ana R1-M{i+1}") for i in range(8)}
with col2:
    m_qf = {i: match_card(f"MQF_{i}", m_r1[i*2][0], m_r1[i*2+1][0], f"Ana ÇF-M{i+1}") for i in range(4)}
with col3:
    m_sf = {i: match_card(f"MSF_{i}", m_qf[i*2][0], m_qf[i*2+1][0], f"Ana YF-M{i+1}") for i in range(2)}

# 3. CONSOLATION (TESELLİ)
st.divider()
st.subheader("🔄 Teselli (Consolation) Akışı")

# R1 ve R2
c_col1, c_col2, c_col3, c_col4 = st.columns(4)

with c_col1:
    st.write("### T-R1")
    c_r1 = {i: match_card(f"CR1_{i}", m_r1[i*2][1], m_r1[i*2+1][1], f"R1 Kayb. {i+1}") for i in range(4)}

with c_col2:
    st.write("### T-R2")
    c_r2 = {i: match_card(f"CR2_{i}", c_r1[i][0], m_qf[i][1], f"ÇF Kayb. ile {i+1}") for i in range(4)}

# R3 (7.-8. lik belirlenir)
with c_col3:
    st.write("### T-R3")
    c_r3 = {i: match_card(f"CR3_{i}", c_r2[i*2][0], c_r2[i*2+1][0], f"Yarı Final {i+1}") for i in range(2)}
    st.write("**7.-8.'lik Maçı:**")
    match_card("MATCH_7_8", c_r3[0][1], c_r3[1][1], "Maç")

# R4 (Final ve 5.-6. lık belirlenir)
with c_col4:
    st.write("### T-R4 (Yarı Final)")
    c_r4 = {i: match_card(f"CR4_{i}", c_r3[i][0], m_sf[i][1], f"YF Kayb. ile {i+1}") for i in range(2)}
    
    st.write("**Teselli Finali (3.-4.):**")
    match_card("FINAL_TESELLI", c_r4[0][0], c_r4[1][0], "Final")
    
    st.write("**5.-6.'lık Maçı:**")
    match_card("MATCH_5_6", c_r4[0][1], c_r4[1][1], "Maç")
