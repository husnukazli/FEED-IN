import streamlit as st
import json

st.set_page_config(layout="wide", page_title="Consolation Milli Takım Belirleme", initial_sidebar_state="collapsed")

# --- URL PARAMETRESİ İLE SALT OKUNUR (READ-ONLY) KONTROLÜ ---
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
    header, footer, .stExpander, .no-print, [data-testid="stSidebar"], .stRadio { display: none !important; }
    [data-testid="stHorizontalBlock"] { display: flex !important; flex-wrap: nowrap !important; }
    [data-testid="column"] { flex: 1 1 0% !important; min-width: 0 !important; display: block !important; }
    * { -webkit-print-color-adjust: exact !important; color-adjust: exact !important; }
    .match-card { page-break-inside: avoid; border: 1px solid #000; background-color: #eee !important; }
}
</style>
""", unsafe_allow_html=True)

st.title("🎾 Consolation Milli Takım Belirleme")

if not is_read_only:
    st.info("🔗 **Hakem/İzleyici Paylaşım Linki:** Sayfa URL'nizin sonuna `?view=true` ekleyerek bu paneli dışarıya 'Salt Okunur' olarak paylaşabilirsiniz.")

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

# --- MAÇ KARTI ---
def match_card(m_id, p1, p2, label):
    st.session_state[f"match_players_{active_cat}_{m_id}"] = (p1, p2)
    
    name1 = p1 if p1 else "Bekleniyor..."
    name2 = p2 if p2 else "Bekleniyor..."
    
    current_winner = cat_data['res'].get(m_id, {}).get("w", "-")
    current_score = cat_data['scores'].get(m_id, "")
    
    card_html = f"""
    <div class="match-card">
        <div class="match-label">{label}</div>
        <div class="player-name" style="font-weight: {'bold' if current_winner == p1 and p1 else 'normal'};">{name1}</div>
        <div class="player-separator"></div>
        <div class="player-name" style="font-weight: {'bold' if current_winner == p2 and p2 else 'normal'};">{name2}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
    
    if is_read_only:
        if current_winner != "-":
            st.markdown(f"<div style='text-align:center; font-size:12px; color:green;'><b>K:</b> {current_winner} <br> <b>Skor:</b> {current_score}</div>", unsafe_allow_html=True)
        return current_winner if current_winner != "-" else None, p2 if current_winner == p1 else (p1 if current_winner == p2 else None)
    
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
# 1. ANA TABLO
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
    axis_gap = 60 

    with c1: 
        st.markdown("<h5 style='text-align: center;'>Son 16</h5>", unsafe_allow_html=True)
        for i in range(4): 
            m_r1[i] = match_card(f"MR1_{i}", p[i*2], p[i*2+1], f"R1-M{i+1}")
        spacer(axis_gap) 
        for i in range(4, 8): 
            m_r1[i] = match_card(f"MR1_{i}", p[i*2], p[i*2+1], f"R1-M{i+1}")
            
    with c2: 
        st.markdown("<h5 style='text-align: center;'>Çeyrek Final</h5>", unsafe_allow_html=True)
        spacer(30)
        m_qf[0] = match_card(f"MQF_0", m_r1[0][0], m_r1[1][0], "ÇF-M1")
        spacer(80)
        m_qf[1] = match_card(f"MQF_1", m_r1[2][0], m_r1[3][0], "ÇF-M2")
        spacer(axis_gap + 50) 
        m_qf[2] = match_card(f"MQF_2", m_r1[4][0], m_r1[5][0], "ÇF-M3")
        spacer(80)
        m_qf[3] = match_card(f"MQF_3", m_r1[6][0], m_r1[7][0], "ÇF-M4")
            
    with c3: 
        st.markdown("<h5 style='text-align: center;'>Yarı Final</h5>", unsafe_allow_html=True)
        spacer(110)
        m_sf[0] = match_card("MSF_0", m_qf[0][0], m_qf[1][0], "YF-M1")
        spacer(axis_gap + 200) 
        m_sf[1] = match_card("MSF_1", m_qf[2][0], m_qf[3][0], "YF-M2")
            
    with c4: 
        st.markdown("<h5 style='text-align: center;'>Final</h5>", unsafe_allow_html=True)
        spacer(290)
        res_main = match_card("FINAL_MAIN", m_sf[0][0], m_sf[1][0], "🏆 ŞAMPİYONLUK FİNALİ")

# ==========================================
# 2. TESELLİ
# ==========================================
with tab_teselli:
    print_button()
    st.markdown("<h4 style='text-align: center;'>Teselli (Consolation) Tablosu</h4>", unsafe_allow_html=True)
    tc1, tc2, tc3, tc4, tc5 = st.columns([1, 1, 1, 1, 1])
    c_r1, c_r2, c_r3, c_r4 = {}, {}, {}, {}

    with tc1: 
        st.markdown("<h6 style='text-align: center;'>T-Son 16</h6>", unsafe_allow_html=True)
        for i in range(2): 
            c_r1[i] = match_card(f"CR1_{i}", m_r1[i*2][1], m_r1[i*2+1][1], f"T-R1 M{i+1}")
        spacer(axis_gap) 
        for i in range(2, 4): 
            c_r1[i] = match_card(f"CR1_{i}", m_r1[i*2][1], m_r1[i*2+1][1], f"T-R1 M{i+1}")
        
    with tc2: 
        st.markdown("<h6 style='text-align: center;'>T-Çeyrek Final</h6>", unsafe_allow_html=True)
        qf_losers_reversed = [m_qf[3][1], m_qf[2][1], m_qf[1][1], m_qf[0][1]]
        for i in range(2): 
            c_r2[i] = match_card(f"CR2_{i}", c_r1[i][0], qf_losers_reversed[i], f"T-R2 M{i+1}")
        spacer(axis_gap)
        for i in range(2, 4): 
            c_r2[i] = match_card(f"CR2_{i}", c_r1[i][0], qf_losers_reversed[i], f"T-R2 M{i+1}")

    with tc3: 
        st.markdown("<h6 style='text-align: center;'>T-Yarı Final 1</h6>", unsafe_allow_html=True)
        spacer(40)
        c_r3[0] = match_card("CR3_0", c_r2[0][0], c_r2[1][0], "T-R3 M1")
        spacer(axis_gap + 70)
        c_r3[1] = match_card("CR3_1", c_r2[2][0], c_r2[3][0], "T-R3 M2")

    with tc4: 
        st.markdown("<h6 style='text-align: center;'>T-Yarı Final 2</h6>", unsafe_allow_html=True)
        spacer(60)
        c_r4[0] = match_card("CR4_0", c_r3[0][0], m_sf[0][1], "T-YF M1")
        spacer(axis_gap + 110)
        c_r4[1] = match_card("CR4_1", c_r3[1][0], m_sf[1][1], "T-YF M2")

    with tc5: 
        st.markdown("<h6 style='text-align: center;'>Teselli Finali</h6>", unsafe_allow_html=True)
        spacer(220)
        res_final_teselli = match_card("FINAL_TESELLI", c_r4[0][0], c_r4[1][0], "🥉 3.-4.'LÜK")

    st.divider()
    st.markdown("<h5 style='text-align: center;'>Klasman Belirleme Maçları</h5>", unsafe_allow_html=True)
    klasman_col1, klasman_col2, _ = st.columns([1.5, 1.5, 1])
    with klasman_col1:
        res_56 = match_card("MATCH_5_6", c_r4[0][1], c_r4[1][1], "5. VE 6.'LIK MAÇI")
    with klasman_col2:
        res_78 = match_card("MATCH_7_8", c_r3[0][1], c_r3[1][1], "7. VE 8.'LİK MAÇI")

# ==========================================
# 3. SIRALAMA
# ==========================================
with tab_siralama:
    print_button()
    st.header(f"🇹🇷 {active_cat} Milli Takım Sıralaması")
    res = cat_data['res']
    rankings = [("1.", "FINAL_MAIN", "w", "#FFD700"), ("2.", "FINAL_MAIN", "l", "#C0C0C0"), 
                ("3.", "FINAL_TESELLI", "w", "#cd7f32"), ("4.", "FINAL_TESELLI", "l", "#f8f9fa"), 
                ("5.", "MATCH_5_6", "w", "#f8f9fa"), ("6.", "MATCH_5_6", "l", "#f8f9fa"), 
                ("7.", "MATCH_7_8", "w", "#f8f9fa"), ("8.", "MATCH_7_8", "l", "#f8f9fa")]
    
    st.markdown("<div style='max-width: 500px;'>", unsafe_allow_html=True)
    for rank, m_id, key, color in rankings:
        player_name = res[m_id][key] if m_id in res and key in res[m_id] else "Belli Değil"
        st.markdown(f"<div style='padding: 10px; margin-bottom: 5px; border: 1px solid #ccc; border-radius: 5px; background-color: {color}; font-size: 16px;'><b>{rank}</b> {player_name}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 4. MAÇ PROGRAMI
# ==========================================
with tab_program:
    print_button()
    st.header("📅 Ortak Maç Programı")
    
    if not is_read_only:
        col_gun, col_filtre = st.columns(2)
        secilen_gun = col_gun.radio("🗓️ Günü Seçin:", ["Tüm Günler", "1. GÜN", "2. GÜN", "3. GÜN"], horizontal=True, key="gun_sel")
        tablo_filtresi = col_filtre.radio("🔍 Fikstür Filtresi:", ["Tümü", "Sadece Ana Tablo", "Sadece Teselli"], horizontal=True, key="filt_sel")
    else:
        secilen_gun = "Tüm Günler"
        tablo_filtresi = "Tümü"
        st.info("📅 Güncel Maç Programı Listesi (Salt Okunur)")
    
    st.divider()

    for cat in ['Erkekler', 'Kadınlar']:
        st.subheader(f"--- {cat} Turnuvası ---")
        
        def edit_day_schedule(matches, day_name):
            filtered_matches = []
            for m_id, label in matches:
                is_consolation = m_id.startswith("CR") or "TESELLI" in m_id or "5_6" in m_id or "7_8" in m_id
                if tablo_filtresi == "Sadece Ana Tablo" and is_consolation: continue
                if tablo_filtresi == "Sadece Teselli" and not is_consolation: continue
                filtered_matches.append((m_id, label))
            
            if not filtered_matches: return

            if secilen_gun in ["Tüm Günler", day_name]:
                st.markdown(f"<h4 class='no-print'>🗓️ {day_name}</h4>", unsafe_allow_html=True)
                h1, h2, h3, h4, h5, h6 = st.columns([1.5, 2, 2, 1, 1, 1])
                h1.markdown("**Maç**"); h2.markdown("**Oyuncu 1**"); h3.markdown("**Oyuncu 2**"); h4.markdown("**Saat**"); h5.markdown("**Kort**"); h6.markdown("**Skor**")
                st.markdown("<div style='margin-top:-10px; margin-bottom:10px; border-bottom:1px solid #ddd;'></div>", unsafe_allow_html=True)
                
                for m_id, label in filtered_matches:
                    p1, p2 = st.session_state.get(f"match_players_{cat}_{m_id}", ("⏳", "⏳"))
                    winner = st.session_state.data[cat]['res'].get(m_id, {}).get("w", None)
                    p1_display = f"🏆 **{p1}**" if winner and p1 == winner else p1
                    p2_display = f"🏆 **{p2}**" if winner and p2 == winner else p2
                    data = st.session_state.data[cat]['schedule_data'].get(m_id, {"saat": "", "kort": "", "skor": ""})
                    
                    c1, c2, c3, c4, c5, c6 = st.columns([1.5, 2, 2, 1, 1, 1])
                    c1.write(label); c2.write(p1_display); c3.write(p2_display)
                    
                    if is_read_only:
                        c4.write(data.get("saat", "-"))
                        c5.write(data.get("kort", "-"))
                        c6.write(data.get("skor", "-"))
                    else:
                        new_saat = c4.text_input("Saat", value=data.get("saat", ""), key=f"time_{cat}_{m_id}", label_visibility="collapsed", placeholder="Örn: 10:00")
                        new_kort = c5.text_input("Kort", value=data.get("kort", ""), key=f"court_{cat}_{m_id}", label_visibility="collapsed", placeholder="Kort 1")
                        new_skor = c6.text_input("Skor", value=data.get("skor", ""), key=f"prog_score_{cat}_{m_id}", label_visibility="collapsed")
                        st.session_state.data[cat]['schedule_data'][m_id] = {"saat": new_saat, "kort": new_kort, "skor": new_skor}
                st.markdown("<br>", unsafe_allow_html=True)

        gun1_maclari = [(f"MR1_{i}", f"Ana Tablo R1 M{i+1}") for i in range(8)] + [(f"CR1_{i}", f"T-R1 M{i+1}") for i in range(4)]
        gun2_maclari = [(f"MQF_{i}", f"Ana Tablo ÇF M{i+1}") for i in range(4)] + [(f"MSF_{i}", f"Ana Tablo YF M{i+1}") for i in range(2)] + [(f"CR2_{i}", f"T-R2 M{i+1}") for i in range(4)] + [(f"CR3_{i}", f"T-R3 M{i+1}") for i in range(2)] + [("MATCH_7_8", "7.-8.'lik Maçı")]
        gun3_maclari = [("FINAL_MAIN", "Ana Tablo FİNAL"), ("FINAL_TESELLI", "3.-4.'lük (Teselli Finali)"), ("MATCH_5_6", "5.-6.'lık Maçı"),] + [(f"CR4_{i}", f"T-YF M{i+1}") for i in range(2)]

        edit_day_schedule(gun1_maclari, "1. GÜN")
        edit_day_schedule(gun2_maclari, "2. GÜN")
        edit_day_schedule(gun3_maclari, "3. GÜN")
