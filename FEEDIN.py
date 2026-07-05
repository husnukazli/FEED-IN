import streamlit as st
import json

# --- SAYFA AYARLARI ---
st.set_page_config(layout="wide", page_title="Tenis Turnuva Yönetim Sistemi")
st.title("🎾 Tenis Turnuva Yönetim Sistemi")

# --- ÖZEL CSS (Spacers yerine daha temiz bir görsel yapı) ---
st.markdown("""
    <style>
    .match-box {
        border: 1px solid #aaa;
        padding: 5px;
        border-radius: 5px;
        margin-bottom: 10px;
        font-size: 12px;
        background-color: #f9f9f9;
        text-align: center;
    }
    .stTextInput > label, .stSelectbox > label {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- VERİ YÖNETİMİ ---
def get_or_create_data():
    if 'data' not in st.session_state:
        st.session_state.data = {
            'Erkekler': {'players': [f"Oyuncu {i}" for i in range(1, 17)], 'res': {}, 'scores': {}, 'schedule_data': {}},
            'Kadınlar': {'players': [f"Oyuncu {i}" for i in range(1, 17)], 'res': {}, 'scores': {}, 'schedule_data': {}}
        }
    return st.session_state.data

data = get_or_create_data()
active_cat = st.radio("Turnuva Kategorisi Seçiniz:", ["Erkekler", "Kadınlar"], horizontal=True)
cat_data = data[active_cat]

# --- MAÇ KARTI FONKSİYONU ---
def match_card(m_id, p1, p2, label):
    st.markdown(f"**{label}**")
    
    # Görselleştirme
    name1 = p1 if p1 else "..."
    name2 = p2 if p2 else "..."
    st.markdown(f'<div class="match-box">{name1}<br>vs<br>{name2}</div>', unsafe_allow_html=True)
    
    winner, loser = None, None
    
    if p1 and p2:
        # Mevcut durumu al
        current_res = cat_data['res'].get(m_id, {"w": "-", "l": "-"})
        options = ["-", p1, p2]
        
        # Seçim
        idx = options.index(current_res['w']) if current_res['w'] in options else 0
        w_selection = st.selectbox(f"W_{m_id}", options, index=idx, key=f"sel_{active_cat}_{m_id}")
        
        # Skor
        score = st.text_input(f"S_{m_id}", value=cat_data['scores'].get(m_id, ""), key=f"score_{active_cat}_{m_id}", placeholder="Skor giriniz")
        cat_data['scores'][m_id] = score
        
        if w_selection != "-":
            winner = w_selection
            loser = p2 if winner == p1 else p1
            cat_data['res'][m_id] = {"w": winner, "l": loser}
            return winner, loser
            
    return None, None

# --- TAB'LAR ---
tab_ana, tab_teselli, tab_siralama, tab_program = st.tabs(["🏆 Ana Tablo", "🔄 Teselli", "📊 Sıralama", "📅 Maç Programı"])

p = cat_data['players']

# --- ANA TABLO ---
with tab_ana:
    st.subheader(f"👥 {active_cat} Oyuncu Düzenleme")
    txt = st.text_area("16 Oyuncu girin (Her satıra bir tane):", value="\n".join(p), height=150)
    if st.button("Listeyi Güncelle"):
        cat_data['players'] = [name.strip() for name in txt.splitlines() if name.strip()]
        st.rerun()
    
    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    
    with c1: 
        m_r1 = {i: match_card(f"MR1_{i}", p[i*2], p[i*2+1], f"R1-M{i+1}") for i in range(8)}
    with c2: 
        m_qf = {i: match_card(f"MQF_{i}", m_r1[i*2][0], m_r1[i*2+1][0], f"ÇF-M{i+1}") for i in range(4)}
    with c3: 
        m_sf = {i: match_card(f"MSF_{i}", m_qf[i*2][0], m_qf[i*2+1][0], f"YF-M{i+1}") for i in range(2)}
    with c4: 
        res_main = match_card("FINAL_MAIN", m_sf[0][0], m_sf[1][0], "FİNAL")

# --- TESELLİ ---
with tab_teselli:
    c_col1, c_col2, c_col3, c_col4 = st.columns(4)
    
    # Teselli R1
    with c_col1: 
        c_r1 = {i: match_card(f"CR1_{i}", m_r1[i*2][1], m_r1[i*2+1][1], f"T-R1 M{i+1}") for i in range(4)}
    
    # Teselli R2
    with c_col2:
        qf_losers = [m_qf[3][1], m_qf[2][1], m_qf[1][1], m_qf[0][1]]
        c_r2 = {i: match_card(f"CR2_{i}", c_r1[i][0], qf_losers[i], f"T-R2 M{i+1}") for i in range(4)}
    
    # Teselli R3
    with c_col3:
        c_r3 = {i: match_card(f"CR3_{i}", c_r2[i*2][0], c_r2[i*2+1][0], f"T-R3 M{i+1}") for i in range(2)}
        res_78 = match_card("MATCH_7_8", c_r3[0][1], c_r3[1][1], "7.-8.'lik Maçı")
    
    # Teselli Finali
    with c_col4:
        c_r4 = {i: match_card(f"CR4_{i}", c_r3[i][0], m_sf[i][1], f"T-YF M{i+1}") for i in range(2)}
        res_final_teselli = match_card("FINAL_TESELLI", c_r4[0][0], c_r4[1][0], "Teselli Finali")
        res_56 = match_card("MATCH_5_6", c_r4[0][1], c_r4[1][1], "5.-6.'lık Maçı")

# --- SIRALAMA ---
with tab_siralama:
    st.header("Sıralama")
    res = cat_data['res']
    rankings = [("1.", "FINAL_MAIN", "w"), ("2.", "FINAL_MAIN", "l"), ("3.", "FINAL_TESELLI", "w"), ("4.", "FINAL_TESELLI", "l"), ("5.", "MATCH_5_6", "w"), ("6.", "MATCH_5_6", "l"), ("7.", "MATCH_7_8", "w"), ("8.", "MATCH_7_8", "l")]
    for rank, m_id, key in rankings:
        if m_id in res: st.write(f"{rank} {res[m_id][key]}")

# --- MAÇ PROGRAMI ---
with tab_program:
    st.header("📅 Maç Programı Yönetimi")
    st.info("Program değişiklikleri veriye anlık işlenir.")
    
    # Tüm maçların listesi
    all_matches = [("MR1_0", "Ana R1-1")] # Basitleştirilmiş örnek; tüm maçları buraya ekleyebilirsiniz
    # (Buraya tüm maç ID'lerini liste olarak ekleyip bir döngüyle hepsini gösterebilirsiniz)

# --- VERİ İŞLEMLERİ (Sidebar) ---
with st.sidebar:
    st.header("⚙️ Veri Yönetimi")
    data_to_save = json.dumps(st.session_state.data)
    st.download_button("Tüm Veriyi İndir (JSON)", data=data_to_save, file_name="turnuva_verisi.json")
    uploaded_file = st.file_uploader("JSON Yükle", type="json")
    if uploaded_file and st.button("Veriyi Yükle"):
        st.session_state.data = json.load(uploaded_file)
        st.rerun()
