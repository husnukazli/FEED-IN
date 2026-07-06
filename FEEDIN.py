import streamlit as st
import json

st.set_page_config(layout="wide", page_title="Consolation Milli Takım Belirleme", initial_sidebar_state="collapsed")

# --- URL PARAMETRESİ İLE SALT OKUNUR (READ-ONLY) KONTROLÜ ---
# URL sonuna ?view=true eklenirse sistem sadece izleme moduna geçer
query_params = st.query_params
is_read_only = query_params.get("view", ["false"]) == "true"

# --- ÖZEL CSS (Ağaç Simetrisi ve PDF Çıktısı İçin) ---
st.markdown("""
<style>
/* Fikstür Kart Tasarımı */
.match-card {
    border: 1px solid #1f77b4;
    border-radius: 6px;
    padding: 6px;
    margin-bottom: 5px;
    background-color: #f8f9fa;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
}
.match-label { font-size: 11px; font-weight: bold; color: #1f77b4; border-bottom: 1px solid #ddd; margin-bottom: 4px; padding-bottom: 2px; }
.player-name { font-size: 13px; font-weight: 500; color: #333; padding: 2px 0; }
.player-separator { border-top: 1px dashed #ccc; margin: 2px 0; }

/* PDF ve Yazdırma (Print) Ayarları */
@media print {
    /* İstenmeyen elementleri gizle */
    header, footer, .stExpander, .no-print, [data-testid="stSidebar"], .stRadio { display: none !important; }
    /* Fikstürün yan yana kalmasını sağla, alta atmasını engelle */
    [data-testid="stHorizontalBlock"] { display: flex !important; flex-wrap: nowrap !important; }
    [data-testid="column"] { flex: 1 1 0% !important; min-width: 0 !important; display: block !important; }
    /* Renkleri PDF'e zorla bas */
    * { -webkit-print-color-adjust: exact !important; color-adjust: exact !important; }
    .match-card { page-break-inside: avoid; border: 1px solid #000; background-color: #eee !important; }
}
</style>
""", unsafe_allow_html=True)

st.title("🎾 Consolation Milli Takım Belirleme")

# Admin panelinde paylaşım linkini göster
if not is_read_only:
    st.info("🔗 **Hakem/İzleyici Paylaşım Linki:** Sayfa URL'nizin sonuna `?view=true` ekleyerek bu paneli dışarıya 'Salt Okunur' (Müdahale edilemez) olarak paylaşabilirsiniz.")

# --- YARDIMCI FONKSİYONLAR ---
def spacer(height_px):
    st.markdown(f'<div style="height:{height_px}px;"></div>', unsafe_allow_html=True)

def print_button():
    st.markdown("""
    <div class="no-print" style="text-align: right;">
        <button onclick="window.print()" style="padding: 8px 15px; background-color: #1f77b4; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold;">🖨️ Bu Sayfayı PDF Kaydet / Yazdır</button>
    </div>
    """, unsafe_allow_html=True)

# --- VERİ YÖNETİMİ ---
if 'data' not in st.session_state:
    st.session_state.data = {
        'Erkekler': {'players': [f"Oyuncu {i}" for i in range(1, 17)], 'res': {}, 'scores': {}, 'schedule_data': {}},
        'Kadınlar': {'players': [f"Oyuncu {i}" for i in range(1, 17)], 'res': {}, 'scores': {}, 'schedule_data': {}}
    }

if not is_read_only:
    active_cat = st.radio("Turnuva Kategorisi Seçiniz:", ["Erkekler", "Kadınlar"], horizontal=True, key="cat_sel")
else:
    active_cat = st.selectbox("Turnuva Kategorisi:", ["Erkekler", "Kadınlar"], key="cat_sel_ro")
    
cat_data = st.session_state.data[active_cat]

if not is_read_only:
    with st.expander("⚙️ Veri Yönetimi ve Yedekleme", expanded=False):
        col_save, col_load = st.columns(2)
        data_to_save = json.dumps(st.session_state.data)
        col_save.download_button("Tüm Veriyi Kaydet (JSON)", data=data_to_save, file_name="turnuva_verisi.json")
        uploaded_file = col_load.file_uploader("Dosyayı Geri Yükle", type="json")
        if uploaded_file and col_load.button("Yüklenen Veriyi Uygula"):
            st.session_state.data = json.load(uploaded_file)
            st.rerun()

# --- MAÇ KARTI (GÜNCELLENDİ: SALT OKUNUR DESTEKLİ) ---
def match_card(m_id, p1, p2, label):
    st.session_state[f"match_players_{active_cat}_{m_id}"] = (p1, p2)
    
    name1 = p1 if p1 else "Bekleniyor..."
    name2 = p2 if p2 else "Bekleniyor..."
    
    # Skor ve Kazananı okuma
    current_winner = cat_data['res'].get(m_id, {}).get("w", "-")
    current_score = cat_data['scores'].get(m_id, "")
    
    # HTML Kart
    card_html = f"""
    <div class="match-card">
        <div class="match-label">{label}</div>
        <div class="player-name" style="font-weight: {'bold' if current_winner == p1 and p1 else 'normal'};">{name1}</div>
        <div class="player-separator"></div>
        <div class="player-name" style="font-weight: {'bold' if current_winner == p2 and p2 else 'normal'};">{name2}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
    
    # Eğer İzleyici modundaysa (is_read_only), skor girme alanlarını gizle, sadece sonucu göster
    if is_read_only:
        if current_winner != "-":
            st.markdown(f"<div style='text-align:center; font-size:12px; color:green;'><b>K:</b> {current_winner} <br> <b>Skor:</b> {current_score}</div>", unsafe_allow_html=True)
        return current_winner if current_winner != "-" else None, p2 if current_winner == p1 else (p1 if current_winner == p2 else None)
    
    # Admin Modu (Skor Girişi Açık)
    if p1 and p2:
        options = ["-", p1, p2]
        idx = options.index(current_winner) if current_winner in options else 0
        
        c_win, c_score = st.columns([1.2, 1])
        winner = c_win.selectbox("Kazanan", options, index=idx, key=f"sel_{active_cat}_{m_id}", label_visibility="collapsed")
        score = c_score.text_input("Skor", value=current_score, key=f"score_{active_cat}_{m_id}", label_visibility="collapsed", placeholder="Skor")
        
        cat_data['scores'][m_id] = score
        if winner != "-":
            loser = p2 if winner == p1 else p1
            cat_data['res'][m_id] = {"w": winner, "l": loser}
            return winner, loser
    return None, None

# --- TAB'LAR ---
tab_ana, tab_teselli, tab_siralama, tab_program = st.tabs(["🏆 Ana Tablo", "🔄 Teselli", "📊 Sıralama", "📅 Maç Programı"])
p = cat_data['players']

# ==========================================
# 1. ANA TABLO (Kusursuz Simetri)
# ==========================================
with tab_ana:
    print_button()
    if not is_read_only:
        with st.expander("👥 Oyuncu Listesi (Esame Hiyerarşisine Göre)", expanded=False):
            txt = st.text_area("16 Oyuncu girin (1. Seribaşı en üstte):", value="\n".join(p), height=150)
            if st.button("Listeyi Güncelle"):
                cat_data['players'] = [name.strip() for name in txt.splitlines() if name.strip()]
                st.rerun()
    st.divider()
    
    c1, c2, c3, c4 = st.columns([1.2, 1.2, 1.2, 1.2])
    m_r1, m_qf, m_sf = {}, {}, {}
    
    # Yatay Eksen Boşluğu Değeri (Maç 4 ile 5 arasını ayırmak için)
    axis_gap = 60 

    with c1: # Son 16
        st.markdown("<h5 style='text-align: center;'>Son 16</h5>", unsafe_allow_html=True)
        for i in range(4): # Üst grup
            m_r1[i] = match_card(f"MR1_{i}", p[i*2], p[i*2+1], f"R1-M{i+1}")
        spacer(axis_gap) # SİMETRİ EKSENİ
        for i in range(4, 8): # Alt grup
            m_r1[i] = match_card(f"MR1_{i}", p[i*2], p[i*2+1], f"R1-M{i+1}")
            
    with c2: # Çeyrek Final
        st.markdown("<h5 style='text-align: center;'>Çeyrek Final</h5>", unsafe_allow_html=True)
        spacer(30); m_qf[0] = match_card(f"MQF_0", m_r1[0][0], m_r1[1][0], "ÇF-M1")
        spacer(80); m_qf[1] = match_card(f"MQF_1", m_r1[2][0], m_r1[3][0], "ÇF-M2")
        spacer(axis_gap + 50) # SİMETRİ EKSENİ
        m_qf[2] = match_card(f"MQF_2", m_r1[4][0], m_r1[5][0], "ÇF-M3")
        spacer(80); m_qf[3] = match_card(f"MQF_3", m_r1[6][0], m_r1[7][0], "ÇF-M4")
            
    with c3: # Yarı Final
        st.markdown("<h5 style='text-align: center;'>Yarı Final</h5>", unsafe_allow_html=True)
        spacer(110); m_sf[0] = match_card("MSF_0", m_qf[0][0], m_qf[1][0], "YF-M1")
        spacer(axis_gap + 200) # SİMETRİ EKSENİ
        m_sf[1] = match_card("MSF_1", m_qf[2][0], m_qf[3][0], "YF-M2")
            
    with c4: # Final
        st.markdown("<h5 style='text-align: center;'>Final</h5>", unsafe_allow_html=True)
        spacer(290)
        res_main = match_card("FINAL_MAIN", m_sf[0][0], m_sf[1][0], "🏆 ŞAMPİYONLUK FİNALİ")

# ==========================================
# 2. TESELLİ (5 Sütunlu Tam Dallanma + Klasman)
# ==========================================
with tab_teselli:
    print_button()
    st.markdown("<h4 style='text-align: center;'>Teselli (Consolation) Tablosu</h4>", unsafe_allow_html=True)
    tc1, tc2, tc3, tc4, tc5 = st.columns([1, 1, 1, 1, 1])
    c_r1, c_r2, c_r3, c_r4 = {}, {}, {}, {}

    with tc1: # T-R1
        st.markdown("<h6 style='text-align: center;'>T-Son 16</h6>", unsafe_allow_html=True)
        for i in range(2): c_r1[i] = match_card(f"CR1_{i}", m_r1[i*2][1], m_r1[i*2+1][1], f"T-R1 M{i+1}")
        spacer(axis_gap) # Simetri ekseni
        for i in range(2, 4): c_r1[i] = match_card(f"CR1_{
