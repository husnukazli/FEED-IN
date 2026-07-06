import streamlit as st
import json
import os
import pandas as pd
from fpdf import FPDF

st.set_page_config(layout="wide", page_title="Consolation Milli Takım Belirleme", initial_sidebar_state="expanded")

# ==============================================================================
# 1. DOSYA VE FPDF YARDIMCI FONKSİYONLARI
# ==============================================================================
DB_FILE = "turnuva_db.json"
FONT_YUKLENDI = os.path.exists("arial.ttf")

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Ortak yayın ayarı kontrolü
                if 'publish' not in data:
                    data['publish'] = {'gun': 'Tüm Günler', 'filtre': 'Tümü', 'kategori': 'Tümü'}
                return data
        except: pass
    return {
        'Erkekler': {'players': [f"Oyuncu {i}" for i in range(1, 17)], 'res': {}, 'scores': {}, 'schedule_data': {}},
        'Kadınlar': {'players': [f"Oyuncu {i}" for i in range(1, 17)], 'res': {}, 'scores': {}, 'schedule_data': {}},
        'publish': {'gun': 'Tüm Günler', 'filtre': 'Tümü', 'kategori': 'Tümü'}
    }

def save_data():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.data, f)

if 'data' not in st.session_state:
    st.session_state.data = load_data()

# FPDF Çıktı Fonksiyonu (Arial Türkçe destekli ve esnek sütun genişlikli)
def to_pdf_text(text):
    if FONT_YUKLENDI: return str(text)
    return str(text).encode('latin-1', 'replace').decode('latin-1')

def generate_pdf(df, baslik, col_widths=None):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    if FONT_YUKLENDI:
        try:
            pdf.add_font("ArialTR", "", "arial.ttf", uni=True)
            pdf.set_font("ArialTR", "", 14)
        except: pdf.set_font("Arial", 'B', 14)
    else: pdf.set_font("Arial", 'B', 14)
        
    pdf.cell(0, 10, to_pdf_text(baslik), ln=True, align='C')
    pdf.ln(5)
    
    if not df.empty:
        if FONT_YUKLENDI: pdf.set_font("ArialTR", "", 10)
        else: pdf.set_font("Arial", 'B', 10)
        
        # Sütun Genişlikleri Ayarı
        if col_widths is None:
            w = [190 / len(df.columns)] * len(df.columns)
        else:
            w = col_widths

        # Başlıklar
        for i, col in enumerate(df.columns):
            pdf.cell(w[i], 10, to_pdf_text(col), border=1, align='C')
        pdf.ln()
        
        if FONT_YUKLENDI: pdf.set_font("ArialTR", "", 9)
        else: pdf.set_font("Arial", '', 9)
            
        # Satırlar
        for _, row in df.iterrows():
            for i, item in enumerate(row):
                align = 'C' if w[i] < 30 else 'L' # Dar sütunları ortala, genişleri sola yasla
                pdf.cell(w[i], 8, to_pdf_text(str(item)), border=1, align=align)
            pdf.ln()
    return bytes(pdf.output())

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
    # Fikstür ve Sıralama için Kategori Seçimi
    if not st.session_state.admin_mi:
        active_cat = st.selectbox("🎾 Fikstür Kategorisi:", ["Erkekler", "Kadınlar"])
    else:
        active_cat = st.radio("🎾 Fikstür Kategorisi:", ["Erkekler", "Kadınlar"])

cat_data = st.session_state.data[active_cat]

# ==============================================================================
# 3. ÖZEL CSS VE SİMETRİ YARDIMCILARI
# ==============================================================================
st.markdown("""
<style>
.match-wrapper { height: 105px; margin-bottom: 5px; }
.match-card {
    border: 1px solid #1f77b4; border-radius: 6px; padding: 6px; 
    background-color: #f8f9fa; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); height: 100%;
}
.match-label { font-size: 11px; font-weight: bold; color: #1f77b4; border-bottom: 1px solid #ddd; margin-bottom: 4px; padding-bottom: 2px; }
.player-name { font-size: 13px; font-weight: 500; color: #333; padding: 2px 0; overflow: hidden; white-space: nowrap; text-overflow: ellipsis;}
.player-separator { border-top: 1px dashed #ccc; margin: 2px 0; }

@media print {
    header, footer, [data-testid="stSidebar"], .stTabs [data-baseweb="tab-list"], 
    .stSelectbox, .stRadio, .stTextInput, button, .stExpander, .no-print { display: none !important; }
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

# ==========================================
# SEKME YÖNETİMİ
# ==========================================
st.title("🎾 Turnuva Yönetim Sistemi")
tab_ana, tab_teselli, tab_program, tab_siralama, tab_dosya = st.tabs(["🏆 Ana Tablo", "🔄 Teselli Tablosu", "📅 Maç Programı", "🇹🇷 Sıralama", "⚙️ Veri Yönetimi"])
p = cat_data['players']

# ==========================================
# TAB 1: ANA TABLO
# ==========================================
with tab_ana:
    st.markdown("<div class='no-print' style='text-align: right;'><button onclick='window.print()' style='padding:5px 10px; cursor:pointer;'>🖨️ Fikstürü Yazdır / PDF Al (Ctrl+P)</button></div>", unsafe_allow_html=True)
    st.markdown(f"#### {active_cat} Ana Tablosu")
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
# TAB 2: TESELLİ TABLOSU
# ==========================================
with tab_teselli:
    st.markdown("<div class='no-print' style='text-align: right;'><button onclick='window.print()' style='padding:5px 10px; cursor:pointer;'>🖨️ Teselli Ağacını Yazdır / PDF Al (Ctrl+P)</button></div>", unsafe_allow_html=True)
    st.markdown(f"#### {active_cat} Teselli Tablosu")
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
        c_r3[0] = match_card("CR3_0", c_r2[0][0], c_r2[1][0], "T-YF1 M1")
        spacer(S_R2_GAP + 100)
        c_r3[1] = match_card("CR3_1", c_r2[2][0], c_r2[3][0], "T-YF1 M2")

    with tc4: 
        st.markdown("<h6 style='text-align: center;'>T-YF 2</h6>", unsafe_allow_html=True)
        spacer(S_R2_TOP + 30)
        c_r4[0] = match_card("CR4_0", c_r3[0][0], m_sf[0][1], "T-YF2 M1")
        spacer(S_R2_GAP + 130)
        c_r4[1] = match_card("CR4_1", c_r3[1][0], m_sf[1][1], "T-YF2 M2")

    with tc5: 
        st.markdown("<h6 style='text-align: center;'>Finaller</h6>", unsafe_allow_html=True)
        spacer(S_R3_TOP)
        match_card("FINAL_TESELLI", c_r4[0][0], c_r4[1][0], "🥉 3.-4.'LÜK")
        spacer(50)
        match_card("MATCH_5_6", c_r4[0][1], c_r4[1][1], "5. VE 6. MAÇI")
        spacer(50)
        match_card("MATCH_7_8", c_r3[0][1], c_r3[1][1], "7. VE 8. MAÇI")

# ==========================================
# TAB 3: ORTAK MAÇ PROGRAMI
# ==========================================
with tab_program:
    st.subheader("📅 Ortak Maç Programı")
    
    if st.session_state.admin_mi:
        st.info("💡 **Yayın Ayarı:** Seçimleriniz anında Misafir (İzleyici) moduna yansır.")
        c_gun, c_kat, c_fil = st.columns(3)
        
        gunler = ["Tüm Günler", "1. GÜN", "2. GÜN", "3. GÜN", "4. GÜN"]
        kategoriler = ["Tümü", "Erkekler", "Kadınlar"]
        filtreler = ["Tümü", "Sadece Ana Tablo", "Sadece Teselli"]
        
        mevcut_g = st.session_state.data['publish'].get('gun', 'Tüm Günler')
        mevcut_k = st.session_state.data['publish'].get('kategori', 'Tümü')
        mevcut_f = st.session_state.data['publish'].get('filtre', 'Tümü')
        
        secilen_gun = c_gun.radio("🗓️ Gün:", gunler, index=gunler.index(mevcut_g) if mevcut_g in gunler else 0)
        secilen_kategori = c_kat.radio("🎾 Kategori:", kategoriler, index=kategoriler.index(mevcut_k) if mevcut_k in kategoriler else 0)
        tablo_filtresi = c_fil.radio("🔍 Filtre:", filtreler, index=filtreler.index(mevcut_f) if mevcut_f in filtreler else 0)
        
        if secilen_gun != mevcut_g or secilen_kategori != mevcut_k or tablo_filtresi != mevcut_f:
            st.session_state.data['publish'] = {'gun': secilen_gun, 'kategori': secilen_kategori, 'filtre': tablo_filtresi}
            save_data()
    else:
        secilen_gun = st.session_state.data['publish'].get('gun', 'Tüm Günler')
        secilen_kategori = st.session_state.data['publish'].get('kategori', 'Tümü')
        tablo_filtresi = st.session_state.data['publish'].get('filtre', 'Tümü')
        st.warning(f"👁️ Yayındaki Akış: **{secilen_gun} | {secilen_kategori} Kategorisi | {tablo_filtresi}**")

    st.divider()

    # Program Verisi Toplama (PDF için)
    pdf_program_data = []

    def draw_schedule(cat_name, matches, day_name):
        cat_d = st.session_state.data[cat_name]
        filtered_matches = []
        
        for m_id, label in matches:
            is_consolation = m_id.startswith("CR") or "TESELLI" in m_id or "5_6" in m_id or "7_8" in m_id
            if tablo_filtresi == "Sadece Ana Tablo" and is_consolation: continue
            if tablo_filtresi == "Sadece Teselli" and not is_consolation: continue
            filtered_matches.append((m_id, label))
        
        if not filtered_matches: return

        st.markdown(f"<h5 style='color:#1f77b4; margin-top:10px;'>🎾 {cat_name} - {day_name}</h5>", unsafe_allow_html=True)
        h1, h2, h3, h4, h5, h6 = st.columns([1.5, 2, 2, 1, 1, 1])
        h1.markdown("**Maç Türü**"); h2.markdown("**Oyuncu 1**"); h3.markdown("**Oyuncu 2**"); h4.markdown("**Saat**"); h5.markdown("**Kort**"); h6.markdown("**Skor**")
        st.markdown("<div style='margin-top:-10px; margin-bottom:10px; border-bottom:1px solid #ddd;'></div>", unsafe_allow_html=True)
        
        for m_id, label in filtered_matches:
            p1, p2 = st.session_state.get(f"match_players_{cat_name}_{m_id}", ("⏳", "⏳"))
            winner = cat_d['res'].get(m_id, {}).get("w", None)
            p1_display = f"🏆 **{p1}**" if winner and p1 == winner else p1
            p2_display = f"🏆 **{p2}**" if winner and p2 == winner else p2
            data = cat_d['schedule_data'].get(m_id, {"saat": "", "kort": "", "skor": ""})
            
            # PDF Listesine Ekle
            pdf_program_data.append({
                "Tarih/Gün": day_name, "Kategori": cat_name, "Tur": label, "Saat": data.get("saat", "-"), "Kort": data.get("kort", "-"),
                "Oyuncu 1": p1, "Oyuncu 2": p2, "Skor": data.get("skor", "-")
            })

            c1, c2, c3, c4, c5, c6 = st.columns([1.5, 2, 2, 1, 1, 1])
            c1.write(label); c2.write(p1_display); c3.write(p2_display)
            
            if not st.session_state.admin_mi:
                c4.write(data.get("saat", "-"))
                c5.write(data.get("kort", "-"))
                c6.write(data.get("skor", "-"))
            else:
                new_saat = c4.text_input("Saat", value=data.get("saat", ""), key=f"t_{cat_name}_{m_id}", label_visibility="collapsed")
                new_kort = c5.text_input("Kort", value=data.get("kort", ""), key=f"c_{cat_name}_{m_id}", label_visibility="collapsed")
                new_skor = c6.text_input("Skor", value=data.get("skor", ""), key=f"s_{cat_name}_{m_id}", label_visibility="collapsed")
                
                if new_saat != data.get("saat") or new_kort != data.get("kort") or new_skor != data.get("skor"):
                    cat_d['schedule_data'][m_id] = {"saat": new_saat, "kort": new_kort, "skor": new_skor}
                    save_data()

    # Ortak Akış Döngüsü
    g_maclar = {
        "1. GÜN": [(f"MR1_{i}", f"Ana Tablo R1 M{i+1}") for i in range(8)],
        "2. GÜN": [(f"MQF_{i}", f"Ana Tablo ÇF M{i+1}") for i in range(4)] + [(f"CR1_{i}", f"T-R1 M{i+1}") for i in range(4)] + [(f"CR2_{i}", f"T-ÇF M{i+1}") for i in range(4)],
        "3. GÜN": [(f"MSF_{i}", f"Ana Tablo YF M{i+1}") for i in range(2)] + [(f"CR3_{i}", f"T-YF1 M{i+1}") for i in range(2)] + [(f"CR4_{i}", f"T-YF2 M{i+1}") for i in range(2)] + [("MATCH_7_8", "7.-8.'lik Maçı")],
        "4. GÜN": [("FINAL_MAIN", "Ana Tablo FİNAL"), ("FINAL_TESELLI", "3.-4.'lük (Teselli)"), ("MATCH_5_6", "5.-6.'lık Maçı")]
    }

    kategoriler_to_show = ["Erkekler", "Kadınlar"] if secilen_kategori == "Tümü" else [secilen_kategori]
    gunler_to_show = ["1. GÜN", "2. GÜN", "3. GÜN", "4. GÜN"] if secilen_gun == "Tüm Günler" else [secilen_gun]

    for g_adi in gunler_to_show:
        for k_adi in kategoriler_to_show:
            draw_schedule(k_adi, g_maclar[g_adi], g_adi)
            
    if pdf_program_data:
        st.divider()
        pdf_prog_df = pd.DataFrame(pdf_program_data)
        # PDF Sütun genişlikleri (Tarih, Kategori, Tur, Saat, Kort, Oyuncu1, Oyuncu2, Skor)
        prog_col_widths = [18, 18, 25, 12, 12, 40, 40, 25]
        btn_pdf_prog = generate_pdf(pdf_prog_df, f"Mac Programi ({secilen_gun} - {secilen_kategori})", col_widths=prog_col_widths)
        st.download_button("📥 Ekrandaki Maç Programını PDF Olarak İndir (Arial Destekli)", data=btn_pdf_prog, file_name="Mac_Programi.pdf", mime="application/pdf")

# ==========================================
# TAB 4: SIRALAMA (Ayrı Sekme ve Özel Tasarım)
# ==========================================
with tab_siralama:
    st.subheader("🇹🇷 Milli Takım Kesin Sıralama")
    
    # Sıralamada Kategori Seçimi (Sıralama sayfasına özel bağımsız)
    sira_kategori = st.radio("Sıralamasını Görmek İstediğiniz Kategori:", ["Erkekler", "Kadınlar", "Tümü"], horizontal=True)
    kategoriler_sira = ["Erkekler", "Kadınlar"] if sira_kategori == "Tümü" else [sira_kategori]
    
    pdf_siralama_data = []

    for k_adi in kategoriler_sira:
        st.markdown(f"#### 🏆 {k_adi} Sıralaması")
        res = st.session_state.data[k_adi]['res']
        rankings = [("1.", "FINAL_MAIN", "w"), ("2.", "FINAL_MAIN", "l"), ("3.", "FINAL_TESELLI", "w"), ("4.", "FINAL_TESELLI", "l"), 
                    ("5.", "MATCH_5_6", "w"), ("6.", "MATCH_5_6", "l"), ("7.", "MATCH_7_8", "w"), ("8.", "MATCH_7_8", "l")]
        
        # Dar Numaralar, Geniş İsimler Hizalaması
        for rank, m_id, key in rankings:
            player_name = res[m_id][key] if m_id in res and key in res[m_id] else "Belli Değil"
            pdf_siralama_data.append({"Sıra": rank, "Kategori": k_adi, "Oyuncu Adı": player_name})
            
            c_no, c_isim = st.columns([0.5, 4])
            c_no.markdown(f"<div style='font-size:16px; font-weight:bold; padding:5px; background:#e0e0e0; text-align:center; border-radius:5px;'>{rank}</div>", unsafe_allow_html=True)
            c_isim.markdown(f"<div style='font-size:16px; padding:5px;'>{player_name}</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
    if pdf_siralama_data:
        st.divider()
        pdf_sir_df = pd.DataFrame(pdf_siralama_data)
        # Sütun Genişlikleri: Sıra (Dar), Kategori (Orta), Oyuncu (Geniş)
        sir_col_widths = [15, 30, 145]
        btn_pdf_sir = generate_pdf(pdf_sir_df, f"Milli Takim Siralamasi ({sira_kategori})", col_widths=sir_col_widths)
        st.download_button("📥 Sıralamayı PDF Olarak İndir (Arial Destekli)", data=btn_pdf_sir, file_name="Siralama.pdf", mime="application/pdf")

# ==========================================
# TAB 5: YEDEKLEME VE DOSYA (Sadece Admin)
# ==========================================
with tab_dosya:
    if st.session_state.admin_mi:
        st.subheader("📥 Veri Yönetimi ve Oyuncu Listesi")
        
        st.markdown(f"**1. Esame Listesini Güncelle ({active_cat})**")
        txt = st.text_area("16 Oyuncu girin (1. Seribaşı en üstte):", value="\n".join(cat_data['players']), height=150)
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
