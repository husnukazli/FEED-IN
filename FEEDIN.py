import streamlit as st
import json
import os
import pandas as pd
import datetime
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
                if 'publish' not in data:
                    data['publish'] = {'gun': 'Tüm Günler', 'filtre': 'Tümü', 'kategori': 'Tümü', 'dates': {}}
                if 'dates' not in data['publish']:
                    data['publish']['dates'] = {}
                return data
        except: pass
    return {
        'Erkekler': {'players': [f"Oyuncu {i}" for i in range(1, 17)], 'res': {}, 'scores': {}, 'schedule_data': {}},
        'Kadınlar': {'players': [f"Oyuncu {i}" for i in range(1, 17)], 'res': {}, 'scores': {}, 'schedule_data': {}},
        'publish': {'gun': 'Tüm Günler', 'filtre': 'Tümü', 'kategori': 'Tümü', 'dates': {}}
    }

def save_data():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.data, f)

if 'data' not in st.session_state:
    st.session_state.data = load_data()

def format_date_tr(date_str):
    if not date_str: return ""
    try:
        d = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
        return f"{d.strftime('%d.%m.%Y')} {gunler[d.weekday()]}"
    except:
        return date_str

def to_pdf_text(text):
    if FONT_YUKLENDI: return str(text)
    return str(text).encode('latin-1', 'replace').decode('latin-1')

def generate_pdf(df, baslik, col_widths=None):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    font_family = "ArialTR" if FONT_YUKLENDI else "Arial"
    
    if FONT_YUKLENDI:
        try: pdf.add_font("ArialTR", "", "arial.ttf", uni=True)
        except: font_family = "Arial"
        
    pdf.set_font(font_family, 'B' if not FONT_YUKLENDI else "", 14)
    pdf.cell(0, 10, to_pdf_text(baslik), ln=True, align='C')
    pdf.ln(5)
    
    if not df.empty:
        pdf.set_font(font_family, 'B' if not FONT_YUKLENDI else "", 10)
        w = col_widths if col_widths else [190 / len(df.columns)] * len(df.columns)

        for i, col in enumerate(df.columns):
            pdf.cell(w[i], 10, to_pdf_text(col), border=1, align='C')
        pdf.ln()
        
        for _, row in df.iterrows():
            for i, item in enumerate(row):
                align = 'C' if w[i] < 26 else 'L' 
                text = str(item)
                pdf_text = to_pdf_text(text)
                
                original_size = 9
                pdf.set_font(font_family, "", original_size)
                
                current_size = original_size
                while pdf.get_string_width(pdf_text) > (w[i] - 2) and current_size > 5:
                    current_size -= 0.5
                    pdf.set_font(font_family, "", current_size)
                
                if pdf.get_string_width(pdf_text) > (w[i] - 2):
                    while pdf.get_string_width(pdf_text + "..") > (w[i] - 2) and len(pdf_text) > 0:
                        pdf_text = pdf_text[:-1]
                    pdf_text += ".."
                    
                pdf.cell(w[i], 8, pdf_text, border=1, align=align)
                pdf.set_font(font_family, "", original_size)
            pdf.ln()
    return bytes(pdf.output())

# ==============================================================================
# 2. ŞİFRELİ GİRİŞ / MİSAFİR MODU
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
        active_cat = st.selectbox("🎾 Fikstür Kategorisi:", ["Erkekler", "Kadınlar"])
    else:
        active_cat = st.radio("🎾 Fikstür Kategorisi:", ["Erkekler", "Kadınlar"])

cat_data = st.session_state.data[active_cat]

# ==============================================================================
# 3. ÖZEL CSS VE SİMETRİ YARDIMCILARI
# ==============================================================================
st.markdown("""
<style>
/* Kart yüksekliği kaynak metinleri için artırıldı (105px -> 125px) */
.match-wrapper { height: 125px; margin-bottom: 5px; }
.match-card {
    border: 1px solid #1f77b4; border-radius: 6px; padding: 6px; 
    background-color: #f8f9fa; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); height: 100%;
}
.match-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #ddd; margin-bottom: 4px; padding-bottom: 2px; }
.match-label { font-size: 11px; font-weight: bold; color: #1f77b4; }
.match-number { font-size: 11px; font-weight: bold; color: #fff; background-color: #1f77b4; padding: 1px 5px; border-radius: 4px; }
.player-name { font-size: 13px; font-weight: 500; color: #333; padding: 2px 0; overflow: hidden; white-space: nowrap; text-overflow: ellipsis;}
.player-src { font-size: 9px; color: #7f8c8d; font-style: italic; margin-top: -3px; margin-bottom: 2px; }
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

# Yükseklik 125px olduğu için simetri boşlukları güncellendi
S_R2_TOP = 65; S_R2_GAP = 130
S_R3_TOP = 195; S_R3_GAP = 390
S_FIN_TOP = 455

def match_card(m_id, p1, p2, label, match_no="", src1="", src2=""):
    st.session_state[f"match_players_{active_cat}_{m_id}"] = (p1, p2)
    name1 = p1 if p1 else "Bekleniyor..."
    name2 = p2 if p2 else "Bekleniyor..."
    
    current_winner = cat_data['res'].get(m_id, {}).get("w", "-")
    current_score = cat_data['scores'].get(m_id, "")
    
    html = f"""
    <div class="match-wrapper"><div class="match-card">
        <div class="match-header">
            <div class="match-label">{label}</div>
            <div class="match-number">M{match_no}</div>
        </div>
        <div class="player-name" style="font-weight: {'bold' if current_winner == p1 and p1 else 'normal'};">{name1}</div>
        {f'<div class="player-src">{src1}</div>' if src1 else ''}
        <div class="player-separator"></div>
        <div class="player-name" style="font-weight: {'bold' if current_winner == p2 and p2 else 'normal'};">{name2}</div>
        {f'<div class="player-src">{src2}</div>' if src2 else ''}
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
        for i in range(4): m_r1[i] = match_card(f"MR1_{i}", p[i*2], p[i*2+1], "R1", i+1)
        spacer(70)
        for i in range(4, 8): m_r1[i] = match_card(f"MR1_{i}", p[i*2], p[i*2+1], "R1", i+1)
            
    with c2: 
        st.markdown("<h5 style='text-align: center;'>Çeyrek Final</h5>", unsafe_allow_html=True)
        spacer(S_R2_TOP)
        m_qf[0] = match_card(f"MQF_0", m_r1[0][0], m_r1[1][0], "ÇF", 9, "M1 Kazananı", "M2 Kazananı")
        spacer(S_R2_GAP)
        m_qf[1] = match_card(f"MQF_1", m_r1[2][0], m_r1[3][0], "ÇF", 10, "M3 Kazananı", "M4 Kazananı")
        spacer(S_R2_GAP + 70)
        m_qf[2] = match_card(f"MQF_2", m_r1[4][0], m_r1[5][0], "ÇF", 11, "M5 Kazananı", "M6 Kazananı")
        spacer(S_R2_GAP)
        m_qf[3] = match_card(f"MQF_3", m_r1[6][0], m_r1[7][0], "ÇF", 12, "M7 Kazananı", "M8 Kazananı")
            
    with c3: 
        st.markdown("<h5 style='text-align: center;'>Yarı Final</h5>", unsafe_allow_html=True)
        spacer(S_R3_TOP)
        m_sf[0] = match_card("MSF_0", m_qf[0][0], m_qf[1][0], "YF", 13, "M9 Kazananı", "M10 Kazananı")
        spacer(S_R3_GAP + 70)
        m_sf[1] = match_card("MSF_1", m_qf[2][0], m_qf[3][0], "YF", 14, "M11 Kazananı", "M12 Kazananı")
            
    with c4: 
        st.markdown("<h5 style='text-align: center;'>Final</h5>", unsafe_allow_html=True)
        spacer(S_FIN_TOP + 35)
        res_main = match_card("FINAL_MAIN", m_sf[0][0], m_sf[1][0], "FİNAL", 15, "M13 Kazananı", "M14 Kazananı")

    if st.session_state.admin_mi:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button(f"💾 {active_cat} Ana Tablo Skorlarını Kaydet", use_container_width=True, key="btn_save_ana"):
            save_data()
            st.success("Ana Tablo değişiklikleri başarıyla kaydedildi!")

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
        for i in range(2): c_r1[i] = match_card(f"CR1_{i}", m_r1[i*2][1], m_r1[i*2+1][1], "T-R1", i+16, f"M{(i*2)+1} Kaybedeni", f"M{(i*2)+2} Kaybedeni")
        spacer(110)
        for i in range(2, 4): c_r1[i] = match_card(f"CR1_{i}", m_r1[i*2][1], m_r1[i*2+1][1], "T-R1", i+16, f"M{(i*2)+1} Kaybedeni", f"M{(i*2)+2} Kaybedeni")
        
    with tc2: 
        st.markdown("<h6 style='text-align: center;'>T-ÇF</h6>", unsafe_allow_html=True)
        qf_losers_reversed = [m_qf[3][1], m_qf[2][1], m_qf[1][1], m_qf[0][1]]
        qf_src_reversed = [12, 11, 10, 9] # Ters eşleşmenin kaynakları
        for i in range(2): c_r2[i] = match_card(f"CR2_{i}", c_r1[i][0], qf_losers_reversed[i], "T-ÇF", i+20, f"M{i+16} Kazananı", f"M{qf_src_reversed[i]} Kaybedeni")
        spacer(110)
        for i in range(2, 4): c_r2[i] = match_card(f"CR2_{i}", c_r1[i][0], qf_losers_reversed[i], "T-ÇF", i+20, f"M{i+16} Kazananı", f"M{qf_src_reversed[i]} Kaybedeni")

    with tc3: 
        st.markdown("<h6 style='text-align: center;'>T-YF 1</h6>", unsafe_allow_html=True)
        spacer(S_R2_TOP)
        c_r3[0] = match_card("CR3_0", c_r2[0][0], c_r2[1][0], "T-YF1", 24, "M20 Kazananı", "M21 Kazananı")
        spacer(S_R2_GAP + 110)
        c_r3[1] = match_card("CR3_1", c_r2[2][0], c_r2[3][0], "T-YF1", 25, "M22 Kazananı", "M23 Kazananı")

    with tc4: 
        st.markdown("<h6 style='text-align: center;'>T-YF 2</h6>", unsafe_allow_html=True)
        spacer(S_R2_TOP + 35)
        c_r4[0] = match_card("CR4_0", c_r3[0][0], m_sf[0][1], "T-YF2", 26, "M24 Kazananı", "M13 Kaybedeni")
        spacer(S_R2_GAP + 145)
        c_r4[1] = match_card("CR4_1", c_r3[1][0], m_sf[1][1], "T-YF2", 27, "M25 Kazananı", "M14 Kaybedeni")

    with tc5: 
        st.markdown("<h6 style='text-align: center;'>Finaller</h6>", unsafe_allow_html=True)
        spacer(S_R3_TOP)
        match_card("FINAL_TESELLI", c_r4[0][0], c_r4[1][0], "3.-4.'LÜK", 28, "M26 Kazananı", "M27 Kazananı")
        spacer(60)
        match_card("MATCH_5_6", c_r4[0][1], c_r4[1][1], "5.-6.'LIK", 29, "M26 Kaybedeni", "M27 Kaybedeni")
        spacer(60)
        match_card("MATCH_7_8", c_r3[0][1], c_r3[1][1], "7.-8.'LİK", 30, "M24 Kaybedeni", "M25 Kaybedeni")

    if st.session_state.admin_mi:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button(f"💾 {active_cat} Teselli Skorlarını Kaydet", use_container_width=True, key="btn_save_teselli"):
            save_data()
            st.success("Teselli değişiklikleri başarıyla kaydedildi!")

# ==========================================
# TAB 3: ORTAK MAÇ PROGRAMI
# ==========================================
with tab_program:
    st.subheader("📅 Ortak Maç Programı")
    
    if st.session_state.admin_mi:
        with st.expander("🗓️ Günlerin Gerçek Tarihlerini Belirle"):
            st.info("Bu tarihler PDF çıktısına ve İzleyici ekranına otomatik yansır.")
            dc1, dc2, dc3, dc4 = st.columns(4)
            
            dates_dict = st.session_state.data['publish'].get('dates', {})
            def_d1 = datetime.datetime.strptime(dates_dict.get("1. GÜN", str(datetime.date.today())), "%Y-%m-%d").date() if dates_dict.get("1. GÜN") else datetime.date.today()
            def_d2 = datetime.datetime.strptime(dates_dict.get("2. GÜN", str(datetime.date.today() + datetime.timedelta(days=1))), "%Y-%m-%d").date() if dates_dict.get("2. GÜN") else datetime.date.today() + datetime.timedelta(days=1)
            def_d3 = datetime.datetime.strptime(dates_dict.get("3. GÜN", str(datetime.date.today() + datetime.timedelta(days=2))), "%Y-%m-%d").date() if dates_dict.get("3. GÜN") else datetime.date.today() + datetime.timedelta(days=2)
            def_d4 = datetime.datetime.strptime(dates_dict.get("4. GÜN", str(datetime.date.today() + datetime.timedelta(days=3))), "%Y-%m-%d").date() if dates_dict.get("4. GÜN") else datetime.date.today() + datetime.timedelta(days=3)

            date1 = dc1.date_input("1. GÜN:", value=def_d1, key="d1_in")
            date2 = dc2.date_input("2. GÜN:", value=def_d2, key="d2_in")
            date3 = dc3.date_input("3. GÜN:", value=def_d3, key="d3_in")
            date4 = dc4.date_input("4. GÜN:", value=def_d4, key="d4_in")
            
            if str(date1) != dates_dict.get("1. GÜN") or str(date2) != dates_dict.get("2. GÜN") or str(date3) != dates_dict.get("3. GÜN") or str(date4) != dates_dict.get("4. GÜN"):
                st.session_state.data['publish']['dates'] = {"1. GÜN": str(date1), "2. GÜN": str(date2), "3. GÜN": str(date3), "4. GÜN": str(date4)}
                save_data()

        st.info("💡 **Yayın Ayarı:** Seçimleriniz anında Misafir (İzleyici) moduna yansır.")
        c_gun, c_kat, c_fil = st.columns(3)
        
        gunler = ["Tüm Günler", "1. GÜN", "2. GÜN", "3. GÜN", "4. GÜN"]
        kategoriler = ["Tümü", "Erkekler", "Kadınlar"]
        filtreler = ["Tümü", "Sadece Ana Tablo", "Sadece Teselli"]
        
        mevcut_g = st.session_state.data['publish'].get('gun', 'Tüm Günler')
        mevcut_k = st.session_state.data['publish'].get('kategori', 'Tümü')
        mevcut_f = st.session_state.data['publish'].get('filtre', 'Tümü')
        
        secilen_gun = c_gun.radio("🗓️ Günü Seçin (İç Yönetim):", gunler, index=gunler.index(mevcut_g) if mevcut_g in gunler else 0)
        secilen_kategori = c_kat.radio("🎾 Kategori:", kategoriler, index=kategoriler.index(mevcut_k) if mevcut_k in kategoriler else 0)
        tablo_filtresi = c_fil.radio("🔍 Filtre:", filtreler, index=filtreler.index(mevcut_f) if mevcut_f in filtreler else 0)
        
        if secilen_gun != mevcut_g or secilen_kategori != mevcut_k or tablo_filtresi != mevcut_f:
            st.session_state.data['publish']['gun'] = secilen_gun
            st.session_state.data['publish']['kategori'] = secilen_kategori
            st.session_state.data['publish']['filtre'] = tablo_filtresi
            save_data()
    else:
        secilen_gun = st.session_state.data['publish'].get('gun', 'Tüm Günler')
        secilen_kategori = st.session_state.data['publish'].get('kategori', 'Tümü')
        tablo_filtresi = st.session_state.data['publish'].get('filtre', 'Tümü')
        
        dates_dict = st.session_state.data['publish'].get('dates', {})
        gosterim_gun_ismi = format_date_tr(dates_dict.get(secilen_gun)) if secilen_gun in dates_dict else secilen_gun
        st.warning(f"👁️ Yayındaki Akış: **{gosterim_gun_ismi} | {secilen_kategori} Kategorisi | {tablo_filtresi}**")

    st.divider()

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

        dates_dict = st.session_state.data['publish'].get('dates', {})
        gercek_tarih_str = format_date_tr(dates_dict.get(day_name))
        
        pdf_tarih = gercek_tarih_str if gercek_tarih_str else day_name.replace(" GÜN", "")
        pdf_kategori = "E" if cat_name == "Erkekler" else "K"

        baslik_gun = f"{gercek_tarih_str} ({day_name})" if gercek_tarih_str else day_name
        st.markdown(f"<h5 style='color:#1f77b4; margin-top:10px;'>🎾 {cat_name} - {baslik_gun}</h5>", unsafe_allow_html=True)
        h1, h2, h3, h4, h5, h6 = st.columns([1.5, 2, 2, 1, 1, 1])
        h1.markdown("**Maç Türü**"); h2.markdown("**Oyuncu 1**"); h3.markdown("**Oyuncu 2**"); h4.markdown("**Saat**"); h5.markdown("**Kort**"); h6.markdown("**Skor**")
        st.markdown("<div style='margin-top:-10px; margin-bottom:10px; border-bottom:1px solid #ddd;'></div>", unsafe_allow_html=True)
        
        for m_id, label in filtered_matches:
            p1, p2 = st.session_state.get(f"match_players_{cat_name}_{m_id}", ("⏳", "⏳"))
            winner = cat_d['res'].get(m_id, {}).get("w", None)
            p1_display = f"🏆 **{p1}**" if winner and p1 == winner else p1
            p2_display = f"🏆 **{p2}**" if winner and p2 == winner else p2
            
            bracket_score = cat_d['scores'].get(m_id, "")
            data = cat_d['schedule_data'].get(m_id, {"saat": "", "kort": ""}) 
            
            # PDF kısaltmaları M numaraları ile zenginleştirildi
            pdf_tur = label.replace("Ana Tablo", "AT").replace("T-", "FC ")
            pdf_tur = pdf_tur.replace("3.-4.'lük Maçı", "FC 3-4").replace("5.-6.'lık Maçı", "FC 5-6").replace("7.-8.'lik Maçı", "FC 7-8")

            pdf_program_data.append({
                "Tarih/Gün": pdf_tarih, "Kat.": pdf_kategori, "Tur": pdf_tur, "Saat": data.get("saat", "-"), "Kort": data.get("kort", "-"),
                "Oyuncu 1": p1, "Oyuncu 2": p2, "Skor": bracket_score if bracket_score else "-"
            })

            c1, c2, c3, c4, c5, c6 = st.columns([1.5, 2, 2, 1, 1, 1])
            c1.write(label); c2.write(p1_display); c3.write(p2_display)
            
            if not st.session_state.admin_mi:
                c4.write(data.get("saat", "-"))
                c5.write(data.get("kort", "-"))
                c6.write(bracket_score if bracket_score else "-")
            else:
                new_saat = c4.text_input("Saat", value=data.get("saat", ""), key=f"t_{cat_name}_{m_id}", label_visibility="collapsed")
                new_kort = c5.text_input("Kort", value=data.get("kort", ""), key=f"c_{cat_name}_{m_id}", label_visibility="collapsed")
                new_skor = c6.text_input("Skor", value=bracket_score, key=f"s_{cat_name}_{m_id}", label_visibility="collapsed")
                
                if new_saat != data.get("saat") or new_kort != data.get("kort"):
                    cat_d['schedule_data'][m_id] = {"saat": new_saat, "kort": new_kort}
                if new_skor != bracket_score:
                    cat_d['scores'][m_id] = new_skor

    g_maclar = {
        "1. GÜN": [(f"MR1_{i}", f"Ana Tablo R1 (M{i+1})") for i in range(8)],
        "2. GÜN": [(f"MQF_{i}", f"Ana Tablo ÇF (M{i+9})") for i in range(4)] + [(f"CR1_{i}", f"T-R1 (M{i+16})") for i in range(4)] + [(f"CR2_{i}", f"T-ÇF (M{i+20})") for i in range(4)],
        "3. GÜN": [(f"MSF_{i}", f"Ana Tablo YF (M{i+13})") for i in range(2)] + [(f"CR3_{i}", f"T-YF1 (M{i+24})") for i in range(2)] + [(f"CR4_{i}", f"T-YF2 (M{i+26})") for i in range(2)] + [("MATCH_7_8", "7.-8.'lik Maçı (M30)")],
        "4. GÜN": [("FINAL_MAIN", "Ana Tablo FİNAL (M15)"), ("FINAL_TESELLI", "3.-4.'lük Maçı (M28)"), ("MATCH_5_6", "5.-6.'lık Maçı (M29)")]
    }

    kategoriler_to_show = ["Erkekler", "Kadınlar"] if secilen_kategori == "Tümü" else [secilen_kategori]
    gunler_to_show = ["1. GÜN", "2. GÜN", "3. GÜN", "4. GÜN"] if secilen_gun == "Tüm Günler" else [secilen_gun]

    for g_adi in gunler_to_show:
        for k_adi in kategoriler_to_show:
            draw_schedule(k_adi, g_maclar[g_adi], g_adi)
            
    if st.session_state.admin_mi:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("💾 Maç Programını Kaydet", use_container_width=True, key="btn_save_prog"):
            save_data()
            st.success("Maç programı başarıyla kaydedildi!")

    if pdf_program_data:
        st.divider()
        pdf_prog_df = pd.DataFrame(pdf_program_data)
        prog_col_widths = [29, 9, 21, 12, 12, 42, 42, 23]
        btn_pdf_prog = generate_pdf(pdf_prog_df, f"Mac Programi", col_widths=prog_col_widths)
        st.download_button("📥 Ekrandaki Maç Programını PDF Olarak İndir (Auto-Fit Destekli)", data=btn_pdf_prog, file_name="Mac_Programi.pdf", mime="application/pdf")

# ==========================================
# TAB 4: SIRALAMA
# ==========================================
with tab_siralama:
    st.subheader("🇹🇷 Milli Takım Kesin Sıralama")
    
    sira_kategori = st.radio("Sıralamasını Görmek İstediğiniz Kategori:", ["Erkekler", "Kadınlar", "Tümü"], horizontal=True)
    kategoriler_sira = ["Erkekler", "Kadınlar"] if sira_kategori == "Tümü" else [sira_kategori]
    
    pdf_siralama_data = []

    for k_adi in kategoriler_sira:
        st.markdown(f"#### 🏆 {k_adi} Sıralaması")
        res = st.session_state.data[k_adi]['res']
        rankings = [("1.", "FINAL_MAIN", "w"), ("2.", "FINAL_MAIN", "l"), ("3.", "FINAL_TESELLI", "w"), ("4.", "FINAL_TESELLI", "l"), 
                    ("5.", "MATCH_5_6", "w"), ("6.", "MATCH_5_6", "l"), ("7.", "MATCH_7_8", "w"), ("8.", "MATCH_7_8", "l")]
        
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
        sir_col_widths = [15, 30, 145]
        btn_pdf_sir = generate_pdf(pdf_sir_df, f"Milli Takim Siralamasi ({sira_kategori})", col_widths=sir_col_widths)
        st.download_button("📥 Sıralamayı PDF Olarak İndir", data=btn_pdf_sir, file_name="Siralama.pdf", mime="application/pdf")

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
