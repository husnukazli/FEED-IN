import streamlit as st
import json

st.set_page_config(layout="wide", page_title="Consolation Milli Takım Belirleme")

# --- ÖZEL CSS (Daha şık ve simetrik bir görünüm için) ---
st.markdown("""
<style>
.match-card {
    border: 1px solid #1f77b4;
    border-radius: 6px;
    padding: 6px;
    margin-bottom: 8px;
    background-color: #f8f9fa;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
}
.match-label {
    font-size: 11px;
    font-weight: bold;
    color: #1f77b4;
    border-bottom: 1px solid #ddd;
    margin-bottom: 4px;
    padding-bottom: 2px;
}
.player-name {
    font-size: 13px;
    font-weight: 500;
    color: #333;
    padding: 2px 0;
}
.player-separator {
    border-top: 1px dashed #ccc;
    margin: 2px 0;
}
</style>
""", unsafe_allow_html=True)

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

# --- MAÇ KARTI FONKSİYONU ---
def match_card(m_id, p1, p2, label):
    st.session_state[f"match_players_{active_cat}_{m_id}"] = (p1, p2)
    
    name1 = p1 if p1 else "Bekleniyor..."
    name2 = p2 if p2 else "Bekleniyor..."
    
    # HTML ile şık kart tasarımı
    card_html = f"""
    <div class="match-card">
        <div class="match-label">{label}</div>
        <div class="player-name">{name1}</div>
        <div class="player-separator"></div>
        <div class="player-name">{name2}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
    
    if p1 and p2:
        current_winner = cat_data['res'].get(m_id, {}).get("w", "-")
        options = ["-", p1, p2]
        idx = options.index(current_winner) if current_winner in options else 0
        
        c_win, c_score = st.columns([1.2, 1])
        winner = c_win.selectbox("Kazanan", options, index=idx, key=f"sel_{active_cat}_{m_id}", label_visibility="collapsed")
        score = c_score.text_input("Skor", value=cat_data['scores'].get(m_id, ""), key=f"score_{active_cat}_{m_id}", label_visibility="collapsed", placeholder="Skor gir")
        
        cat_data['scores'][m_id] = score
        if winner != "-":
            loser = p2 if winner == p1 else p1
            cat_data['res'][m_id] = {"w": winner, "l": loser}
            return winner, loser
    return None, None

# --- TAB'LAR ---
tab_ana, tab_teselli, tab_siralama, tab_program = st.tabs(["🏆 Ana Tablo", "🔄 Teselli", "📊 Sıralama", "📅 Maç Programı"])

p = cat_data['players']

# --- ANA TABLO (SİMETRİK PİRAMİT) ---
with tab_ana:
    with st.expander("👥 Oyuncu Listesi (Esame Hiyerarşisine Göre)"):
        txt = st.text_area("16 Oyuncu girin (1. Seribaşı en üstte):", value="\n".join(p), height=150)
        if st.button("Listeyi Güncelle"):
            cat_data['players'] = [name.strip() for name in txt.splitlines() if name.strip()]
            st.rerun()
            
    st.divider()
    
    # Simetrik görünüm için kolon oranları
    c1, c2, c3, c4 = st.columns([1.2, 1.2, 1.2, 1.2])
    
    with c1: # 8 Maç (R1)
        st.markdown("<h5 style='text-align: center; color: #555;'>Son 16</h5>", unsafe_allow_html=True)
        m_r1 = {i: match_card(f"MR1_{i}", p[i*2], p[i*2+1], f"R1-M{i+1}") for i in range(8)}
    
    with c2: # 4 Maç (ÇF)
        st.markdown("<h5 style='text-align: center; color: #555;'>Çeyrek Final</h5>", unsafe_allow_html=True)
        spacer(60) 
        m_qf = {}
        for i in range(4):
            m_qf[i] = match_card(f"MQF_{i}", m_r1[i*2][0], m_r1[i*2+1][0], f"ÇF-M{i+1}")
            spacer(110) 
            
    with c3: # 2 Maç (YF)
        st.markdown("<h5 style='text-align: center; color: #555;'>Yarı Final</h5>", unsafe_allow_html=True)
        spacer(170)
        m_sf = {}
        for i in range(2):
            m_sf[i] = match_card(f"MSF_{i}", m_qf[i*2][0], m_qf[i*2+1][0], f"YF-M{i+1}")
            spacer(350)
            
    with c4: # 1 Maç (FİNAL)
        st.markdown("<h5 style='text-align: center; color: #555;'>Final</h5>", unsafe_allow_html=True)
        spacer(400)
        res_main = match_card("FINAL_MAIN", m_sf[0][0], m_sf[1][0], "FİNAL")

# --- TESELLİ (CONSOLATION) ---
with tab_teselli:
    st.markdown("<h4 style='text-align: center; color: #555;'>Teselli (Consolation) Tablosu</h4>", unsafe_allow_html=True)
    c_col1, c_col2, c_col3, c_col4 = st.columns([1.2, 1.2, 1.2, 1.2])
    
    with c_col1:
        st.markdown("<h6 style='text-align: center; color: #555;'>1. Tur Mağlupları</h6>", unsafe_allow_html=True)
        c_r1 = {i: match_card(f"CR1_{i}", m_r1[i*2][1], m_r1[i*2+1][1], f"T-R1 M{i+1}") for i in range(4)}
        
    with c_col2:
        st.markdown("<h6 style='text-align: center; color: #555;'>ÇF Mağlupları Eklenir</h6>", unsafe_allow_html=True)
        spacer(20)
        qf_losers_reversed = [m_qf[3][1], m_qf[2][1], m_qf[1][1], m_qf[0][1]]
        c_r2 = {i: match_card(f"CR2_{i}", c_r1[i][0], qf_losers_reversed[i], f"T-R2 M{i+1}") for i in range(4)}
        
    with c_col3:
        st.markdown("<h6 style='text-align: center; color: #555;'>Teselli Yarı Final</h6>", unsafe_allow_html=True)
        spacer(80)
        c_r3 = {i: match_card(f"CR3_{i}", c_r2[i*2][0], c_r2[i*2+1][0], f"T-R3 M{i+1}") for i in range(2)}
        spacer(50)
        res_78 = match_card("MATCH_7_8", c_r3[0][1], c_r3[1][1], "7.-8.'lik Maçı")
        
    with c_col4:
        st.markdown("<h6 style='text-align: center; color: #555;'>Klasman Finalleri</h6>", unsafe_allow_html=True)
        spacer(50)
        c_r4 = {i: match_card(f"CR4_{i}", c_r3[i][0], m_sf[i][1], f"T-YF M{i+1}") for i in range(2)}
        spacer(20)
        res_final_teselli = match_card("FINAL_TESELLI", c_r4[0][0], c_r4[1][0], "Teselli Finali")
        res_56 = match_card("MATCH_5_6", c_r4[0][1], c_r4[1][1], "5.-6.'lık Maçı")

# --- SIRALAMA ---
with tab_siralama:
    st.header("Milli Takım Belirleme Sıralaması")
    res = cat_data['res']
    rankings = [("1.", "FINAL_MAIN", "w"), ("2.", "FINAL_MAIN", "l"), 
                ("3.", "FINAL_TESELLI", "w"), ("4.", "FINAL_TESELLI", "l"), 
                ("5.", "MATCH_5_6", "w"), ("6.", "MATCH_5_6", "l"), 
                ("7.", "MATCH_7_8", "w"), ("8.", "MATCH_7_8", "l")]
    
    st.markdown("<div style='max-width: 400px;'>", unsafe_allow_html=True)
    for rank, m_id, key in rankings:
        player_name = res[m_id][key] if m_id in res and key in res[m_id] else "Belli Değil"
        st.info(f"**{rank}** {player_name}")
    st.markdown("</div>", unsafe_allow_html=True)

# --- MAÇ PROGRAMI ---
with tab_program:
    st.header("📅 Ortak Maç Programı")
    
    col_gun, col_filtre = st.columns(2)
    secilen_gun = col_gun.radio("🗓️ Günü Seçin:", ["Tüm Günler", "1. GÜN", "2. GÜN", "3. GÜN"], horizontal=True)
    tablo_filtresi = col_filtre.radio("🔍 Fikstür Filtresi:", ["Tümü", "Sadece Ana Tablo", "Sadece Teselli"], horizontal=True)
    
    st.divider()

    for cat in ['Erkekler', 'Kadınlar']:
        st.subheader(f"--- {cat} Turnuvası ---")
        
        def edit_day_schedule(matches, day_name):
            # Filtreleme Mantığı
            filtered_matches = []
            for m_id, label in matches:
                is_consolation = m_id.startswith("CR") or "TESELLI" in m_id or "5_6" in m_id or "7_8" in m_id
                
                if tablo_filtresi == "Sadece Ana Tablo" and is_consolation:
                    continue
                if tablo_filtresi == "Sadece Teselli" and not is_consolation:
                    continue
                filtered_matches.append((m_id, label))
            
            if not filtered_matches:
                return # Filtreye uyan maç yoksa bu günü/kısmı atla

            if secilen_gun in ["Tüm Günler", day_name]:
                st.markdown(f"#### 🗓️ {day_name}")
                h1, h2, h3, h4, h5, h6 = st.columns([1.5, 2, 2, 1, 1, 1])
                h1.markdown("**Maç**"); h2.markdown("**Oyuncu 1**"); h3.markdown("**Oyuncu 2**"); h4.markdown("**Maç Saati**"); h5.markdown("**Kort**"); h6.markdown("**Skor**")
                st.markdown("<div style='margin-top:-10px; margin-bottom:10px; border-bottom:1px solid #ddd;'></div>", unsafe_allow_html=True)
                
                for m_id, label in filtered_matches:
                    p1, p2 = st.session_state.get(f"match_players_{cat}_{m_id}", ("⏳", "⏳"))
                    winner = st.session_state.data[cat]['res'].get(m_id, {}).get("w", None)
                    p1_display = f"🏆 **{p1}**" if winner and p1 == winner else p1
                    p2_display = f"🏆 **{p2}**" if winner and p2 == winner else p2
                    data = st.session_state.data[cat]['schedule_data'].get(m_id, {"saat": "", "kort": "", "skor": ""})
                    
                    c1, c2, c3, c4, c5, c6 = st.columns([1.5, 2, 2, 1, 1, 1])
                    c1.write(label); c2.write(p1_display); c3.write(p2_display)
                    new_saat = c4.text_input("Saat", value=data.get("saat", ""), key=f"time_{cat}_{m_id}", label_visibility="collapsed")
                    new_kort = c5.text_input("Kort", value=data.get("kort", ""), key=f"court_{cat}_{m_id}", label_visibility="collapsed")
                    new_skor = c6.text_input("Skor", value=data.get("skor", ""), key=f"prog_score_{cat}_{m_id}", label_visibility="collapsed")
                    st.session_state.data[cat]['schedule_data'][m_id] = {"saat": new_saat, "kort": new_kort, "skor": new_skor}
                st.markdown("<br>", unsafe_allow_html=True)

        # Ana tablo ve Teselli maçlarının günlere mantıksal dağılımı
        gun1_maclari = [(f"MR1_{i}", f"Ana Tablo R1 M{i+1}") for i in range(8)] + [(f"CR1_{i}", f"T-R1 M{i+1}") for i in range(4)]
        gun2_maclari = [(f"MQF_{i}", f"Ana Tablo ÇF M{i+1}") for i in range(4)] + [(f"MSF_{i}", f"Ana Tablo YF M{i+1}") for i in range(2)] + [(f"CR2_{i}", f"T-R2 M{i+1}") for i in range(4)] + [(f"CR3_{i}", f"T-R3 M{i+1}") for i in range(2)]
        gun3_maclari = [("FINAL_MAIN", "Ana Tablo FİNAL"), ("FINAL_TESELLI", "Teselli Finali"), ("MATCH_5_6", "5.-6.'lık Maçı"), ("MATCH_7_8", "7.-8.'lik Maçı"),] + [(f"CR4_{i}", f"T-YF M{i+1}") for i in range(2)]

        edit_day_schedule(gun1_maclari, "1. GÜN")
        edit_day_schedule(gun2_maclari, "2. GÜN")
        edit_day_schedule(gun3_maclari, "3. GÜN")
