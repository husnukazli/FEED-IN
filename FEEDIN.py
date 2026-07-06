import streamlit as st
import json
import os
import pandas as pd
from fpdf import FPDF

st.set_page_config(layout="wide", page_title="Consolation Milli Takım Belirleme", initial_sidebar_state="expanded")

# ==============================================================================
# 1. DOSYA VE FPDF YARDIMCI FONKSİYONLARI (Sadece Sıralama İçin Kullanılacak)
# ==============================================================================
DB_FILE = "turnuva_db.json"
FONT_YUKLENDI = os.path.exists("arial.ttf")

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {
        'Erkekler': {'players': [f"Oyuncu {i}" for i in range(1, 17)], 'res': {}, 'scores': {}, 'schedule_data': {}, 'publish': {'gun': 'Tüm Günler', 'filtre': 'Tümü'}},
        'Kadınlar': {'players': [f"Oyuncu {i}" for i in range(1, 17)], 'res': {}, 'scores': {}, 'schedule_data': {}, 'publish': {'gun': 'Tüm Günler', 'filtre': 'Tümü'}}
    }

def save_data():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.data, f)

if 'data' not in st.session_state:
    st.session_state.data = load_data()
    # Eski verilerde publish ayarı yoksa ekle
    for c in ['Erkekler', 'Kadınlar']:
        if 'publish' not in st.session_state.data[c]:
            st.session_state.data[c]['publish'] = {'gun': 'Tüm Günler', 'filtre': 'Tümü'}

# ==============================================================================
# 2. ŞİFRELİ GİRİŞ / MİSAFİR MODU (SİDEBAR)
# ==============================================================================
if "admin_mi" not in st.session_state:
    st.session_state.admin_mi = False

with st.sidebar:
    st.markdown("### 👨‍⚖️ Turnuva Yönetimi")
    if not st.session_state.admin_mi:
        st.info("👁️ Şu an **Misafir Modunda** izliyorsunuz.")
        girilen_sifre = st.text_input("Hakem Şifresi:", type="password")
        if st.button("🔒 Giriş Yap"):
            if girilen_sifre == "zonguldak2026":
                st.session_state.admin_mi = True
                st.success("✅ Başhakem Yetkisi Aktif!")
                st.rerun()
            else:
                st.error("❌ Hatalı Şifre!")
    else:
        st.success("🟢 **Aktif Mod:** Başhakem")
        if st.button("🔓 Çıkış Yap (Misafir Modu)"):
            st.session_state.admin_mi = False
            st.rerun()
            
    st.divider()
    if not st.session_state.admin_mi:
        active_cat = st.selectbox("🎾 Turnuva Kategorisi:", ["Erkekler", "Kadınlar"])
    else:
        active_cat = st.radio("🎾 Kategori:", ["Erkekler", "Kadınlar"])

cat_data = st.session_state.data[active_cat]

# ==============================================================================
# 3. ÖZEL CSS VE SİMETRİ YARDIMCILARI (Agresif PDF Baskı Gizlemesi)
# ==============================================================================
st.markdown("""
<style>
/* Kart yüksekliği ve Görsel Ağaç */
.match-wrapper { height: 105px; margin-bottom: 5px; }
.match-card {
    border: 1px solid #1f77b4; border-radius: 6px; padding: 6px; 
    background-color: #f8f9fa; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); height: 100%;
}
.match-label { font-size: 11px; font-weight: bold; color: #1f77b4; border-bottom: 1px solid #ddd; margin-bottom: 4px; padding-bottom: 2px; }
.player-name { font-size: 13px; font-weight: 500; color: #333; padding: 2px 0; overflow: hidden; white-space: nowrap; text-overflow: ellipsis;}
.player-separator { border-top: 1px dashed #ccc; margin: 2px 0; }

/* KUSURSUZ PDF BASKISI İÇİN - Sadece AĞAÇ görünecek */
@media print {
    header, footer, [data-testid="stSidebar"], .stTabs [data-baseweb="tab-list"], 
    .stSelectbox, .stRadio, .stTextInput, button, .stExpander, .no-print { 
        display: none !important; 
    }
    .stTabs { margin-top: -60px !important; }
    [data-testid="stHorizontalBlock"] { display: flex !important; flex-wrap: nowrap !important; }
    [data-testid="column"] { flex: 1 1 0% !important; min-width: 0 !important; display: block !important; }
    * { -webkit-print-color-adjust: exact !important; color-adjust: exact !important; }
    .match-wrapper { page-break-inside: avoid; }
    .match-card { border: 1px solid #000; background-color: #eee !important; margin-bottom: 2px !important; }
}
</style>
""", unsafe_allow_html=True)

def spacer(height_px):
    st.markdown(f'<div style="height:{height_px}px;"></div>', unsafe_allow_html=True)

# Simetri Eksen Boşlukları
S_R2_TOP = 55
S_R2_GAP = 110
S_R3_TOP = 165
S_R3_GAP = 330
S_FIN_TOP = 385

def match_card(m_id, p1, p2, label):
    st.session_state[f"match_players_{active_cat}_{m_id}"] = (p1, p2)
    name1 = p1 if p1 else "Bekleniyor..."
    name2 = p2 if p2 else "Bekleniyor..."
    
    current_winner = cat_data['res'].get(m_id, {}).get("w", "-")
    current_score = cat_data['scores'].get(m_id, "")
    
    html = f"""
    <div class="match-wrapper"><div class="match-card">
        <div class="match-label">{label}</div>
        <div class="player-name" style="font-weight: {'bold' if current_winner == p1 and p1 else 'normal'};">{name1}</div>
        <div class="player-separator"></div>
        <div class="player-name" style="font-weight: {'bold' if current_winner == p2 and p2 else 'normal'};">{name2}</div>
    </div></div>
    """
    st.markdown(html, unsafe_allow_html=True)
    
    if not st.session_state.admin_mi:
        if current_winner != "-":
            st.markdown(f"<div style='text-align:center; font-size:12px; color:green; margin-top:-5px;' class='no-print'><b>K:</b> {current_winner} <br> {current_score}</div>", unsafe_allow_html=True)
        return current_winner if current_winner != "-" else None, p2 if current_winner == p1 else (p1 if current_winner == p2 else None)
    
    if p1 and p2:
        options = ["-", p1, p2]
        idx = options.index(current_winner) if current_winner in options else 0
        
        c_win, c_score = st.columns([1.2, 1])
        winner = c_win.selectbox("Kz", options, index=idx, key=f"sel_{active_cat}_{m_id}", label_visibility="collapsed")
        score = c_score.text_input("Sk", value=current_score, key=f"score_{active_cat}_{m_id}", label_visibility="collapsed", placeholder="Skor")
        
        if score != current_score or winner != current_winner:
            cat_data['scores'][m_id] = score
            if winner != "-":
                loser = p2 if winner == p1 else p1
                cat_data['res'][m_id] = {"w": winner, "l": loser}
            elif winner == "-" and m_id in cat_data['res']:
                del cat_data['res'][m_id]
            save_data()
            st.rerun()
            
        if winner != "-":
            return winner, p2 if winner == p1 else p1
    return None, None

st.title(f"🏆 {active_cat} Kategorisi")

tab_ana, tab_teselli, tab_program, tab_dosya = st.tabs(["Ana Tablo", "Teselli Tablosu", "Maç Programı & Sıralama", "⚙️ Veri & Yedekleme"])
p = cat_data['players']

# ==========================================
# TAB 1: ANA TABLO (Görsel Ağaç)
# ==========================================
with tab_ana:
    st.markdown("<div class='no-print' style='text-align: right;'><button onclick='window.print()' style='padding:5px 10px; cursor:pointer;'>🖨️ Fikstürü Yazdır / PDF Al (Ctrl+P)</button></div>", unsafe_allow_html=True)
    st.divider()
    
    c1, c2, c3, c4 = st.columns(4)
    m_r1, m_qf, m_sf = {}, {}, {}
    
    with c1: 
        st.markdown("<h5 style='text-align: center;'>Son 16</h5>", unsafe_allow_html=True)
        for i in range(4): m_r1[i] = match_card(f"MR1_{i}", p[i*2], p[i*2+1], f"R1-M{i+1}")
        spacer(60)
        for i in range(4, 8): m_r1[i] = match_card(f"MR1_{i}", p[i*2], p[i*2+1], f"R1-M{i+1}")
            
    with c2: 
        st.markdown("<h5 style='text-align: center;'>Çeyrek Final</h5>", unsafe_allow_html=True)
        spacer(S_R2_TOP)
        m_qf[0] = match_card(f"MQF_0", m_r1[0][0], m_r1[1][0], "ÇF-M1")
        spacer(S_R2_GAP)
        m_qf[1] = match_card(f"MQF_1", m_r1[2][0], m_r1[3][0], "ÇF-M2")
        spacer(S_R2_GAP + 60)
        m_qf[2] = match_card(f"MQF_2", m_r1[4][0], m_r1[5][0], "ÇF-M3")
        spacer(S_R2_GAP)
        m_qf[3] = match_card(f"MQF_3", m_r1[6][0], m_r1[7][0], "ÇF-M4")
            
    with c3: 
        st.markdown("<h5 style='text-align: center;'>Yarı Final</h5>", unsafe_allow_html=True)
        spacer(S_R3_TOP)
        m_sf[0] = match_card("MSF_0", m_qf[0][0], m_qf[1][0], "YF-M1")
        spacer(S_R3_GAP + 60)
        m_sf[1] = match_card("MSF_1", m_qf[2][0], m_qf[3][0], "YF-M2")
            
    with c4: 
        st.markdown("<h5 style='text-align: center;'>Final</h5>", unsafe_allow_html=True)
        spacer(S_FIN_TOP + 30)
        res_main = match_card("FINAL_MAIN", m_sf[0][0], m_sf[1][0], "🏆 ŞAMPİYON")

# ==========================================
# TAB 2: TESELLİ TABLOSU (Görsel Ağaç)
# ==========================================
with tab_teselli:
    st.markdown("<div class='no-print' style='text-align: right;'><button onclick='window.print()' style='padding:5px 10px; cursor:pointer;'>🖨️ Teselli Ağacını Yazdır / PDF Al (Ctrl+P)</button></div>", unsafe_allow_html=True)
    st.divider()
    
    tc1, tc2, tc3, tc4, tc5 = st.columns(5)
    c_r1, c_r2, c_r3, c_r4 = {}, {}, {}, {}

    with tc1: 
        st.markdown("<h6 style='text-align: center;'>T-R1</h6>", unsafe_allow_html=True)
        for i in range(2): c_r1[i] = match_card(f"CR1_{i}", m_r1[i*2][1], m_r1[i*2+1][1], f"T-R1 M{i+1}")
        spacer(100)
        for i in range(2, 4): c_r1[i] = match_card(f"CR1_{i}", m_r1[i*2][1], m_r1[i*2+1][1], f"T-R1 M{i+1}")
        
    with tc2: 
        st.markdown("<h6 style='text-align: center;'>T-ÇF</h6>", unsafe_allow_html=True)
        qf_losers_reversed = [m_qf[3][1], m_qf[2][1], m_qf[1][1], m_qf[0][1]]
        for i in range(2): c_r2[i] = match_card(f"CR2_{i}", c_r1[i][0], qf_losers_reversed[i], f"T-R2 M{i+1}")
        spacer(100)
        for i in range(2, 4): c_r2[i] = match_card(f"CR2_{i}", c_r1[i][0], qf_losers_reversed[i], f"T-R2 M{i+1}")

    with tc3: 
        st.markdown("<h6 style='text-align: center;'>T-YF 1</h6>", unsafe_allow_html=True)
        spacer(S_R2_TOP)
        c_r3[0] = match_card("CR3_0", c_r2[0][0], c_r2[1][0], "T-R3 M1")
        spacer(S_R2_GAP + 100)
        c_r3[1] = match_card("CR3_1", c_r2[2][0], c_r2[3][0], "T-R3 M2")

    with tc4: 
        st.markdown("<h6 style='text-align: center;'>T-YF 2</h6>", unsafe_allow_html=True)
        spacer(S_R2_TOP + 30)
        c_r4[0] = match_card("CR4_0", c_r3[0][0], m_sf[0][1], "T-YF M1")
        spacer(S_R2_GAP + 130)
        c_r4[1] = match_card("CR4_1", c_r3[1][0], m_sf[1][1], "T-YF M2")

    with tc5: 
        st.markdown("<h6 style='text-align: center;'>Finaller</h6>", unsafe_allow_html=True)
        spacer(S_R3_TOP)
        match_card("FINAL_TESELLI", c_r4[0][0], c_r4[1][0], "🥉 3.-4.'LÜK")
        spacer(50)
        match_card("MATCH_5_6", c_r4[0][1], c_r4[1][1], "5. VE 6. MAÇI")
        spacer(50)
        match_card("MATCH_7_8", c_r3[0][1], c_r3[1][1], "7. VE 8. MAÇI")

# ==========================================
# TAB 3: PROGRAM VE SIRALAMA (Eski Yapı + Admin Yayın Kontrolü)
# ==========================================
with tab_program:
    st.subheader("📅 Ortak Maç Programı")
    
    # YAYIN FİLTRELERİ (Admin Seçer, Misafir Sadece Seçileni Görür)
    if st.session_state.admin_mi:
        st.info("💡 **Yayın Ayarı:** Aşağıdaki seçimleriniz, Misafir modunda programın nasıl görüneceğini belirler.")
        col_gun, col_filtre = st.columns(2)
        secilen_gun = col_gun.radio("🗓️ Günü Seçin:", ["Tüm Günler", "1. GÜN", "2. GÜN", "3. GÜN"], horizontal=True, index=["Tüm Günler", "1. GÜN", "2. GÜN", "3. GÜN"].index(cat_data['publish'].get('gun', 'Tüm Günler')))
        tablo_filtresi = col_filtre.radio("🔍 Fikstür Filtresi:", ["Tümü", "Sadece Ana Tablo", "Sadece Teselli"], horizontal=True, index=["Tümü", "Sadece Ana Tablo", "Sadece Teselli"].index(cat_data['publish'].get('filtre', 'Tümü')))
        
        if secilen_gun != cat_data['publish'].get('gun') or tablo_filtresi != cat_data['publish'].get('filtre'):
            cat_data['publish'] = {'gun': secilen_gun, 'filtre': tablo_filtresi}
            save_data()
    else:
        # Misafir sadece adminin seçtiği yayını görür
        secilen_gun = cat_data['publish'].get('gun', 'Tüm Günler')
        tablo_filtresi = cat_data['publish'].get('filtre', 'Tümü')
        st.warning(f"👁️ Yayındaki Görünüm: **{secilen_gun} | {tablo_filtresi}**")
    
    st.divider()

    def edit_day_schedule(matches, day_name):
        filtered_matches = []
        for m_id, label in matches:
            is_consolation = m_id.startswith("CR") or "TESELLI" in m_id or "5_6" in m_id or "7_8" in m_id
            if tablo_filtresi == "Sadece Ana Tablo" and is_consolation: continue
            if tablo_filtresi == "Sadece Teselli" and not is_consolation: continue
            filtered_matches.append((m_id, label))
        
        if not filtered_matches: return

        if secilen_gun in ["Tüm Günler", day_name]:
            st.markdown(f"<h4 style='color:#1f77b4;'>🗓️ {day_name}</h4>", unsafe_allow_html=True)
            h1, h2, h3, h4, h5, h6 = st.columns([1.5, 2, 2, 1, 1, 1])
            h1.markdown("**Maç Türü**"); h2.markdown("**Oyuncu 1**"); h3.markdown("**Oyuncu 2**"); h4.markdown("**Saat**"); h5.markdown("**Kort**"); h6.markdown("**Skor**")
            st.markdown("<div style='margin-top:-10px; margin-bottom:10px; border-bottom:1px solid #ddd;'></div>", unsafe_allow_html=True)
            
            for m_id, label in filtered_matches:
                p1, p2 = st.session_state.get(f"match_players_{active_cat}_{m_id}", ("⏳", "⏳"))
                winner = cat_data['res'].get(m_id, {}).get("w", None)
                p1_display = f"🏆 **{p1}**" if winner and p1 == winner else p1
                p2_display = f"🏆 **{p2}**" if winner and p2 == winner else p2
                data = cat_data['schedule_data'].get(m_id, {"saat": "", "kort": "", "skor": ""})
                
                c1, c2, c3, c4, c5, c6 = st.columns([1.5, 2, 2, 1, 1, 1])
                c1.write(label); c2.write(p1_display); c3.write(p2_display)
                
                if not st.session_state.admin_mi:
                    c4.write(data.get("saat", "-"))
                    c5.write(data.get("kort", "-"))
                    c6.write(data.get("skor", "-"))
                else:
                    new_saat = c4.text_input("Saat", value=data.get("saat", ""), key=f"time_{active_cat}_{m_id}", label_visibility="collapsed", placeholder="10:00")
                    new_kort = c5.text_input("Kort", value=data.get("kort", ""), key=f"court_{active_cat}_{m_id}", label_visibility="collapsed", placeholder="Kort 1")
                    new_skor = c6.text_input("Skor", value=data.get("skor", ""), key=f"prog_score_{active_cat}_{m_id}", label_visibility="collapsed")
                    
                    if new_saat != data.get("saat") or new_kort != data.get("kort") or new_skor != data.get("skor"):
                        cat_data['schedule_data'][m_id] = {"saat": new_saat, "kort": new_kort, "skor": new_skor}
                        save_data()
            st.markdown("<br>", unsafe_allow_html=True)

    gun1_maclari = [(f"MR1_{i}", f"Ana Tablo R1 M{i+1}") for i in range(8)] + [(f"CR1_{i}", f"T-R1 M{i+1}") for i in range(4)]
    gun2_maclari = [(f"MQF_{i}", f"Ana Tablo ÇF M{i+1}") for i in range(4)] + [(f"MSF_{i}", f"Ana Tablo YF M{i+1}") for i in range(2)] + [(f"CR2_{i}", f"T-R2 M{i+1}") for i in range(4)] + [(f"CR3_{i}", f"T-R3 M{i+1}") for i in range(2)] + [("MATCH_7_8", "7.-8.'lik Maçı")]
    gun3_maclari = [("FINAL_MAIN", "Ana Tablo FİNAL"), ("FINAL_TESELLI", "3.-4.'lük (Teselli Finali)"), ("MATCH_5_6", "5.-6.'lık Maçı"),] + [(f"CR4_{i}", f"T-YF M{i+1}") for i in range(2)]

    edit_day_schedule(gun1_maclari, "1. GÜN")
    edit_day_schedule(gun2_maclari, "2. GÜN")
    edit_day_schedule(gun3_maclari, "3. GÜN")
    
    st.divider()
    st.subheader("🇹🇷 Milli Takım Sıralaması")
    res = cat_data['res']
    rankings = [("1.", "FINAL_MAIN", "w"), ("2.", "FINAL_MAIN", "l"), ("3.", "FINAL_TESELLI", "w"), ("4.", "FINAL_TESELLI", "l"), 
                ("5.", "MATCH_5_6", "w"), ("6.", "MATCH_5_6", "l"), ("7.", "MATCH_7_8", "w"), ("8.", "MATCH_7_8", "l")]
    
    for rank, m_id, key in rankings:
        player_name = res[m_id][key] if m_id in res and key in res[m_id] else "Belli Değil"
        st.markdown(f"**{rank}** {player_name}")

# ==========================================
# TAB 4: YEDEKLEME VE DOSYA (Sadece Admin)
# ==========================================
with tab_dosya:
    if st.session_state.admin_mi:
        st.subheader("📥 Veri Yönetimi ve Oyuncu Listesi")
        
        st.markdown("**1. Esame Listesini Güncelle**")
        txt = st.text_area(f"{active_cat} Kategorisi 16 Oyuncu girin:", value="\n".join(p), height=150)
        if st.button("👥 Listeyi Kaydet"):
            cat_data['players'] = [name.strip() for name in txt.splitlines() if name.strip()]
            save_data()
            st.success("Liste güncellendi!")
            st.rerun()
            
        st.divider()
        st.markdown("**2. Sistemi Yedekle / Geri Yükle**")
        c_sv, c_ld = st.columns(2)
        
        data_to_save = json.dumps(st.session_state.data, ensure_ascii=False)
        c_sv.download_button("📥 Tüm Veriyi Yedekle (.json)", data=data_to_save, file_name="turnuva_verisi.json")
        
        uploaded_file = c_ld.file_uploader("📤 Dosyayı Geri Yükle", type="json")
        if uploaded_file and c_ld.button("Yüklenen Veriyi Uygula"):
            st.session_state.data = json.load(uploaded_file)
            save_data()
            st.success("Veri geri yüklendi!")
            st.rerun()
    else:
        st.warning("🔒 Bu panel sadece Başhakem erişimine açıktır.")
