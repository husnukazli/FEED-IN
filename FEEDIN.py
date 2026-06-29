import streamlit as st
import pandas as pd
import json
import datetime

st.set_page_config(layout="wide", page_title="Consolation Milli Takım Belirleme")
st.title("🎾 Consolation Milli Takım Belirleme")

# --- DURUM YÖNETİMİ ---
if 'players' not in st.session_state:
    st.session_state.players = [f"Oyuncu {i}" for i in range(1, 17)]
if 'res' not in st.session_state: st.session_state.res = {}
if 'scores' not in st.session_state: st.session_state.scores = {}
if 'schedule_data' not in st.session_state: st.session_state.schedule_data = {} # Saat/Kort verisi için

# --- OYUNCU GİRİŞİ ---
st.subheader("👥 Oyuncu Listesini Düzenle")
txt = st.text_area("16 Oyuncu girin (Her satıra bir isim):", value="\n".join(st.session_state.players), height=100)
if st.button("Listeyi Güncelle"):
    st.session_state.players = [p.strip() for p in txt.splitlines() if p.strip()]
    st.rerun()

st.divider()

# --- KAYDET / YÜKLE ---
with st.expander("⚙️ Veri Yönetimi (Kaydet / Yükle / Dışa Aktar)"):
    col_save, col_load = st.columns(2)
    # Schedule verisini de JSON içine dahil ediyoruz
    data_to_save = json.dumps({
        "res": st.session_state.res, 
        "scores": st.session_state.scores, 
        "players": st.session_state.players,
        "schedule_data": st.session_state.schedule_data
    })
    col_save.download_button("Dosyayı Kaydet (JSON)", data=data_to_save, file_name="turnuva_verisi.json")
    
    uploaded_file = col_load.file_uploader("Dosyayı Geri Yükle", type="json")
    if uploaded_file is not None:
        if col_load.button("Yüklenen Veriyi Sisteme Uygula"):
            data = json.load(uploaded_file)
            st.session_state.res = data.get('res', {})
            st.session_state.scores = data.get('scores', {})
            st.session_state.players = data.get('players', [])
            st.session_state.schedule_data = data.get('schedule_data', {})
            st.rerun()

def match_card(m_id, p1, p2, label):
    st.session_state[f"match_players_{m_id}"] = (p1, p2)
    st.markdown(f"**{label}**")
    name1 = p1 if p1 else "⏳ Bekleniyor"
    name2 = p2 if p2 else "⏳ Bekleniyor"
    st.markdown(f"""<div style="border: 1px solid #ccc; padding: 5px; border-radius: 5px; margin-bottom: 5px; font-size: 14px;">{name1} vs {name2}</div>""", unsafe_allow_html=True)
    
    if p1 and p2:
        current_winner = st.session_state.res.get(m_id, {}).get("w", "-")
        options = ["-", p1, p2]
        idx = options.index(current_winner) if current_winner in options else 0
        winner = st.selectbox(f"Kazanan ({m_id})", options, index=idx, key=f"sel_{m_id}", label_visibility="collapsed")
        score = st.text_input(f"Skor ({m_id})", value=st.session_state.scores.get(m_id, ""), key=f"score_{m_id}", label_visibility="collapsed")
        st.session_state.scores[m_id] = score
        if winner != "-":
            loser = p2 if winner == p1 else p1
            st.session_state.res[m_id] = {"w": winner, "l": loser}
            return winner, loser
    return None, None

# --- TAB'LAR ---
tab_ana, tab_teselli, tab_siralama, tab_program = st.tabs(["🏆 Ana Tablo", "🔄 Teselli", "📊 Sıralama", "📅 Maç Programı"])

p = st.session_state.players

# ANA TABLO
with tab_ana:
    col1, col2, col3 = st.columns(3)
    with col1:
        m_r1 = {i: match_card(f"MR1_{i}", p[i*2], p[i*2+1], f"Ana R1-M{i+1}") for i in range(8)}
    with col2:
        m_qf = {i: match_card(f"MQF_{i}", m_r1[i*2][0], m_r1[i*2+1][0], f"Ana ÇF-M{i+1}") for i in range(4)}
    with col3:
        m_sf = {i: match_card(f"MSF_{i}", m_qf[i*2][0], m_qf[i*2+1][0], f"Ana YF-M{i+1}") for i in range(2)}
        res_main = match_card("FINAL_MAIN", m_sf[0][0], m_sf[1][0], "BÜYÜK FİNAL")

# TESELLİ
with tab_teselli:
    c_col1, c_col2, c_col3, c_col4 = st.columns(4)
    with c_col1:
        c_r1 = {i: match_card(f"CR1_{i}", m_r1[i*2][1], m_r1[i*2+1][1], f"T-R1 M{i+1}") for i in range(4)}
    with c_col2:
        qf_losers_reversed = [m_qf[3][1], m_qf[2][1], m_qf[1][1], m_qf[0][1]]
        c_r2 = {i: match_card(f"CR2_{i}", c_r1[i][0], qf_losers_reversed[i], f"T-R2 M{i+1}") for i in range(4)}
    with c_col3:
        c_r3 = {i: match_card(f"CR3_{i}", c_r2[i*2][0], c_r2[i*2+1][0], f"T-R3 M{i+1}") for i in range(2)}
        res_78 = match_card("MATCH_7_8", c_r3[0][1], c_r3[1][1], "7.-8.'lik Maçı")
    with c_col4:
        c_r4 = {i: match_card(f"CR4_{i}", c_r3[i][0], m_sf[i][1], f"T-YF M{i+1}") for i in range(2)}
        res_final_teselli = match_card("FINAL_TESELLI", c_r4[0][0], c_r4[1][0], "Teselli Finali")
        res_56 = match_card("MATCH_5_6", c_r4[0][1], c_r4[1][1], "5.-6.'lık Maçı")

# SIRALAMA
with tab_siralama:
    st.header("Milli Takım Belirleme Sıralaması")
    res = st.session_state.res
    rows = []
    rankings = [("1.", "FINAL_MAIN", "w"), ("2.", "FINAL_MAIN", "l"), ("3.", "FINAL_TESELLI", "w"), ("4.", "FINAL_TESELLI", "l"), ("5.", "MATCH_5_6", "w"), ("6.", "MATCH_5_6", "l"), ("7.", "MATCH_7_8", "w"), ("8.", "MATCH_7_8", "l")]
    for rank, m_id, key in rankings:
        if m_id in res:
            name = res[m_id][key]
            st.write(f"{rank} {name}")
            rows.append({"Derece": rank, "Oyuncu": name})

# MAÇ PROGRAMI (İnteraktif Giriş)
with tab_program:
    st.header("📅 Gün Bazlı Maç Programı")
    
    def edit_day_schedule(matches, day_name):
        st.subheader(f"🗓️ {day_name}")
        # Başlıklar
        cols = st.columns([2, 2, 2, 1, 1])
        cols[0].write("**Maç**")
        cols[1].write("**Oyuncu 1**")
        cols[2].write("**Oyuncu 2**")
        cols[3].write("**Saat**")
        cols[4].write("**Kort**")
        
        for m_id, label in matches:
            p1, p2 = st.session_state.get(f"match_players_{m_id}", ("⏳", "⏳"))
            
            # Verileri çek
            data = st.session_state.schedule_data.get(m_id, {"saat": "", "kort": ""})
            
            c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 1, 1])
            c1.write(label)
            c2.write(p1)
            c3.write(p2)
            
            # Giriş alanları
            new_saat = c4.text_input("Saat", value=data["saat"], key=f"time_{m_id}", label_visibility="collapsed")
            new_kort = c5.text_input("Kort", value=data["kort"], key=f"court_{m_id}", label_visibility="collapsed")
            
            # Veriyi güncelle
            st.session_state.schedule_data[m_id] = {"saat": new_saat, "kort": new_kort}

    edit_day_schedule([(f"CR1_{i}", f"T-R1 M{i+1}") for i in range(4)] + [(f"CR2_{i}", f"T-R2 M{i+1}") for i in range(4)], "1. GÜN")
    edit_day_schedule([(f"CR3_{i}", f"T-R3 M{i+1}") for i in range(2)] + [("MATCH_7_8", "7.-8.'lik Maçı")] + [(f"CR4_{i}", f"T-YF M{i+1}") for i in range(2)], "2. GÜN")
    edit_day_schedule([("FINAL_TESELLI", "Teselli Finali"), ("MATCH_5_6", "5.-6.'lık Maçı")], "3. GÜN")
