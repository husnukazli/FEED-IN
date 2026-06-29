import streamlit as st
import pandas as pd
import json
import io

st.set_page_config(layout="wide", page_title="Consolation Milli Takım Belirleme")
st.title("🎾 Consolation Milli Takım Belirleme")

# --- DURUM YÖNETİMİ ---
if 'players' not in st.session_state:
    st.session_state.players = [f"Oyuncu {i}" for i in range(1, 17)]
if 'res' not in st.session_state: st.session_state.res = {}
if 'scores' not in st.session_state: st.session_state.scores = {}

# --- KAYDET / YÜKLE / EXPORT ---
with st.expander("⚙️ Veri Yönetimi (Kaydet / Yükle / Dışa Aktar)"):
    col_save, col_load = st.columns(2)
    # Kaydet
    data_to_save = json.dumps({"res": st.session_state.res, "scores": st.session_state.scores, "players": st.session_state.players})
    col_save.download_button("Dosyayı Kaydet (JSON)", data=data_to_save, file_name="turnuva_verisi.json")
    
    # Yükle
    uploaded_file = col_load.file_uploader("Dosyayı Geri Yükle", type="json")
    if uploaded_file:
        data = json.load(uploaded_file)
        st.session_state.res = data['res']
        st.session_state.scores = data['scores']
        st.session_state.players = data['players']
        st.rerun()

def match_card(m_id, p1, p2, label):
    st.markdown(f"**{label}**")
    name1 = p1 if p1 else "⏳ Bekleniyor"
    name2 = p2 if p2 else "⏳ Bekleniyor"
    
    # Görsel Kart
    st.markdown(f"""<div style="border: 1px solid #ccc; padding: 5px; border-radius: 5px; margin-bottom: 5px; font-size: 14px;">{name1} vs {name2}</div>""", unsafe_allow_html=True)
    
    winner, loser = None, None
    if p1 and p2:
        # Kazanan seçimi
        winner = st.selectbox(f"Kazanan ({m_id})", ["-", p1, p2], key=f"sel_{m_id}", label_visibility="collapsed")
        # Skor girişi
        score = st.text_input(f"Skor ({m_id})", value=st.session_state.scores.get(m_id, ""), key=f"score_{m_id}", label_visibility="collapsed")
        st.session_state.scores[m_id] = score
        
        if winner != "-":
            loser = p2 if winner == p1 else p1
            st.session_state.res[m_id] = {"w": winner, "l": loser}
            return winner, loser
    return None, None

# --- TAB'LAR ---
tab_ana, tab_teselli, tab_siralama = st.tabs(["🏆 Ana Tablo", "🔄 Teselli", "📊 Milli Takım Belirleme Sıralaması"])

# OYUNCU GİRİŞİ (Sadece Ana Tablo sekmesinde kalsın)
p = st.session_state.players

with tab_ana:
    col1, col2, col3 = st.columns(3)
    with col1:
        m_r1 = {i: match_card(f"MR1_{i}", p[i*2], p[i*2+1], f"Ana R1-M{i+1}") for i in range(8)}
    with col2:
        m_qf = {i: match_card(f"MQF_{i}", m_r1[i*2][0], m_r1[i*2+1][0], f"Ana ÇF-M{i+1}") for i in range(4)}
    with col3:
        m_sf = {i: match_card(f"MSF_{i}", m_qf[i*2][0], m_qf[i*2+1][0], f"Ana YF-M{i+1}") for i in range(2)}
        res_main = match_card("FINAL_MAIN", m_sf[0][0], m_sf[1][0], "BÜYÜK FİNAL")

with tab_teselli:
    c_col1, c_col2, c_col3, c_col4 = st.columns(4)
    with c_col1:
        st.write("### T-R1")
        c_r1 = {i: match_card(f"CR1_{i}", m_r1[i*2][1], m_r1[i*2+1][1], f"R1 Kayb. {i+1}") for i in range(4)}
    with c_col2:
        st.write("### T-R2 (Ters Sıralı)")
        qf_losers_reversed = [m_qf[3][1], m_qf[2][1], m_qf[1][1], m_qf[0][1]]
        c_r2 = {i: match_card(f"CR2_{i}", c_r1[i][0], qf_losers_reversed[i], f"ÇF Kayb. ile {i+1}") for i in range(4)}
    with c_col3:
        st.write("### T-R3")
        c_r3 = {i: match_card(f"CR3_{i}", c_r2[i*2][0], c_r2[i*2+1][0], f"T-Yarı {i+1}") for i in range(2)}
        res_78 = match_card("MATCH_7_8", c_r3[0][1], c_r3[1][1], "7.-8.'lik Maçı")
    with c_col4:
        st.write("### T-R4 (Yarı Final)")
        c_r4 = {i: match_card(f"CR4_{i}", c_r3[i][0], m_sf[i][1], f"YF Kayb. ile {i+1}") for i in range(2)}
        res_final_teselli = match_card("FINAL_TESELLI", c_r4[0][0], c_r4[1][0], "Teselli Finali (3.-4.)")
        res_56 = match_card("MATCH_5_6", c_r4[0][1], c_r4[1][1], "5.-6.'lık Maçı")

with tab_siralama:
    st.header("Milli Takım Belirleme Sıralaması")
    res = st.session_state.res
    rows = []
    
    rankings = [
        ("1.", "FINAL_MAIN", "w"), ("2.", "FINAL_MAIN", "l"),
        ("3.", "FINAL_TESELLI", "w"), ("4.", "FINAL_TESELLI", "l"),
        ("5.", "MATCH_5_6", "w"), ("6.", "MATCH_5_6", "l"),
        ("7.", "MATCH_7_8", "w"), ("8.", "MATCH_7_8", "l")
    ]
    
    for rank, m_id, key in rankings:
        if m_id in res:
            name = res[m_id][key]
            st.write(f"{rank} {name}")
            rows.append({"Derece": rank, "Oyuncu": name})
    
    if rows:
        df = pd.DataFrame(rows)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Sıralamayı Excel (.csv) İndir", data=csv, file_name="siralama.csv", mime="text/csv")
