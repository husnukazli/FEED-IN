import streamlit as st
import json

st.set_page_config(layout="wide", page_title="Consolation Milli Takım Belirleme")
st.title("🎾 Consolation Milli Takım Belirleme")

# --- YARDIMCI FONKSİYONLAR ---
def spacer(height_px):
    st.markdown(f'<div style="height:{height_px}px;"></div>', unsafe_allow_html=True)

# --- KATEGORİ VE DURUM YÖNETİMİ ---
if 'data' not in st.session_state:
    st.session_state.data = {
        'Erkekler': {'players': [f"Oyuncu {i}" for i in range(1, 17)], 'res': {}, 'scores': {}, 'schedule_data': {}},
        'Kadınlar': {'players': [f"Oyuncu {i}" for i in range(1, 17)], 'res': {}, 'scores': {}, 'schedule_data': {}}
    }

active_cat = st.radio("Turnuva Kategorisi Seçiniz:", ["Erkekler", "Kadınlar"], horizontal=True)
cat_data = st.session_state.data[active_cat]

# --- VERİ YÖNETİMİ ---
with st.expander("⚙️ Veri Yönetimi"):
    col_save, col_load = st.columns(2)
    data_to_save = json.dumps(st.session_state.data)
    col_save.download_button("Tüm Veriyi Kaydet (JSON)", data=data_to_save, file_name="tum_turnuva_verisi.json")
    uploaded_file = col_load.file_uploader("Dosyayı Geri Yükle", type="json")
    if uploaded_file is not None and col_load.button("Yüklenen Veriyi Uygula"):
        st.session_state.data = json.load(uploaded_file)
        st.rerun()

# --- FONKSİYON (Daha kompakt tasarım) ---
def match_card(m_id, p1, p2, label):
    st.session_state[f"match_players_{active_cat}_{m_id}"] = (p1, p2)
    st.markdown(f"<small><b>{label}</b></small>", unsafe_allow_html=True)
    name1 = p1 if p1 else "..."
    name2 = p2 if p2 else "..."
    st.markdown(f"""<div style="border: 1px solid #aaa; padding: 2px; border-radius: 3px; margin-bottom: 8px; font-size: 11px;">{name1}<br>{name2}</div>""", unsafe_allow_html=True)
    
    if p1 and p2:
        current_winner = cat_data['res'].get(m_id, {}).get("w", "-")
        options = ["-", p1, p2]
        idx = options.index(current_winner) if current_winner in options else 0
        winner = st.selectbox(f"Win ({m_id})", options, index=idx, key=f"sel_{active_cat}_{m_id}", label_visibility="collapsed")
        score = st.text_input(f"Skor ({m_id})", value=cat_data['scores'].get(m_id, ""), key=f"score_{active_cat}_{m_id}", label_visibility="collapsed")
        cat_data['scores'][m_id] = score
        if winner != "-":
            loser = p2 if winner == p1 else p1
            cat_data['res'][m_id] = {"w": winner, "l": loser}
            return winner, loser
    return None, None

# --- TAB'LAR ---
tab_ana, tab_teselli, tab_siralama, tab_program = st.tabs(["🏆 Ana Tablo", "🔄 Teselli", "📊 Sıralama", "📅 Maç Programı"])

p = cat_data['players']

# ANA TABLO (GÜNCELLENMİŞ 4 SÜTUNLU PİRAMİT)
with tab_ana:
    st.subheader(f"👥 {active_cat} - Oyuncu Listesi")
    txt = st.text_area("16 Oyuncu girin:", value="\n".join(p), height=70)
    if st.button("Listeyi Güncelle"):
        cat_data['players'] = [name.strip() for name in txt.splitlines() if name.strip()]
        st.rerun()
    st.divider()
    
    # 4 Sütunlu yapı: R1 -> ÇF -> YF -> FİNAL
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
    
    with c1:
        m_r1 = {i: match_card(f"MR1_{i}", p[i*2], p[i*2+1], f"R1-M{i+1}") for i in range(8)}
    
    with c2:
        spacer(30)
        m_qf = {}
        for i in range(4):
            m_qf[i] = match_card(f"MQF_{i}", m_r1[i*2][0], m_r1[i*2+1][0], f"ÇF-M{i+1}")
            spacer(110) # ÇF maçları arası boşluk
            
    with c3:
        spacer(100)
        m_sf = {}
        for i in range(2):
            m_sf[i] = match_card(f"MSF_{i}", m_qf[i*2][0], m_qf[i*2+1][0], f"YF-M{i+1}")
            spacer(250)
            
    with c4:
        spacer(240)
        res_main = match_card("FINAL_MAIN", m_sf[0][0], m_sf[1][0], "FİNAL")

# ... (Tab_teselli, Tab_siralama ve Tab_program kısımları aynı mantıkla kalabilir) ...
with tab_teselli:
    st.info("Teselli tablosu mantığı ana tablodan gelen mağlup oyunculara göre otomatik çalışmaya devam eder.")
    # ... mevcut teselli kodunuz ...

with tab_siralama:
    st.header("Sıralama")
    # ... mevcut sıralama kodunuz ...

with tab_program:
    st.header("Maç Programı")
    # ... mevcut program kodunuz ...
