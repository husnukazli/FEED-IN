import streamlit as st
import json
import os
import pandas as pd
import datetime
import re
import html
from fpdf import FPDF

from bracket_engine import compute_bracket_state
from bracket_svg import render_main_bracket_svg, render_consolation_bracket_svg
from bracket_pdf import generate_bracket_pdf

st.set_page_config(layout="wide", page_title="Milli Takım Belirleme Turnuvası", initial_sidebar_state="expanded")

# ==============================================================================
# 1. DOSYA, ŞİFRE VE FPDF YARDIMCI FONKSİYONLARI
# ==============================================================================
FONT_YUKLENDI = os.path.exists("arial.ttf")
FONT_BOLD_YUKLENDI = os.path.exists("arialbd.ttf")

# Yaş gruplarına özel şifreler (Streamlit secrets üzerinden yönetilebilir)
SIFRELER = {
    "12 Yaş": st.secrets.get("sifre_12", "hakem12"),
    "14 Yaş": st.secrets.get("sifre_14", "hakem14"),
    "16 Yaş": st.secrets.get("sifre_16", "hakem16"),
    "18 Yaş": st.secrets.get("sifre_18", "hakem18")
}

if 'aktif_yas' not in st.session_state:
    st.session_state.aktif_yas = "12 Yaş"
if "admin_mi" not in st.session_state:
    st.session_state.admin_mi = False

# Sol menü - En üstte yaş grubu seçimi (Herkes görebilir)
with st.sidebar:
    st.markdown("### 🏆 Turnuva Seçimi")
    secilen_yas = st.selectbox("Yaş Grubu:", ["12 Yaş", "14 Yaş", "16 Yaş", "18 Yaş"])
    
    # Kategori değişirse veriyi sıfırla ve güvenliği (admin) kapat
    if secilen_yas != st.session_state.aktif_yas:
        st.session_state.aktif_yas = secilen_yas
        st.session_state.admin_mi = False
        if 'data' in st.session_state:
            del st.session_state['data']

DB_FILE = f"turnuva_db_{st.session_state.aktif_yas[:2]}.json"

def clean_html_text(text):
    if not isinstance(text, str): return str(text)
    t = html.unescape(text)
    t = re.sub(r'<[^>]+>', '', t)
    return t.strip()

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

def clean_ghost_data(data):
    degisiklik_oldu = False
    for cat in ['Erkekler', 'Kadınlar']:
        while True:
            b_state = compute_bracket_state(data[cat])
            cleaned_in_loop = False
            keys_to_delete = []
            
            for mid, res_dict in data[cat]['res'].items():
                match = b_state.get(mid)
                if not match: continue
                p1, p2 = match.get("p1"), match.get("p2")
                w = res_dict.get("w")
                if w and (w != p1 and w != p2):
                    keys_to_delete.append(mid)
                    cleaned_in_loop = True
                    degisiklik_oldu = True
                    
            for k in keys_to_delete:
                del data[cat]['res'][k]
                
            if not cleaned_in_loop:
                break
    return degisiklik_oldu

# Seçilen yaş grubunun verisini yükle
if 'data' not in st.session_state:
    st.session_state.data = load_data()
    for cat in ['Erkekler', 'Kadınlar']:
        temiz_liste = []
        for p in st.session_state.data[cat]['players']:
            cp = clean_html_text(p)
            if cp: temiz_liste.append(cp)
        while len(temiz_liste) < 16:
            temiz_liste.append(f"Oyuncu {len(temiz_liste)+1}")
        st.session_state.data[cat]['players'] = temiz_liste[:16]
        
    if clean_ghost_data(st.session_state.data):
        save_data()

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
    t = str(text).replace("İ", "I").replace("ı", "i").replace("Ş", "S").replace("ş", "s") \
                  .replace("Ğ", "G").replace("ğ", "g").replace("Ç", "C").replace("ç", "c") \
                  .replace("Ö", "O").replace("ö", "o").replace("Ü", "U").replace("ü", "u")
    return t.encode('latin-1', 'replace').decode('latin-1')

def generate_pdf(df, baslik, col_widths=None):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    font_family = "ArialTR" if FONT_YUKLENDI else "Arial"
    
    if FONT_YUKLENDI:
        try: 
            pdf.add_font("ArialTR", "", "arial.ttf", uni=True)
            if FONT_BOLD_YUKLENDI:
                pdf.add_font("ArialTR", "B", "arialbd.ttf", uni=True)
        except: 
            font_family = "Arial"
            
    header_style = 'B' if (font_family == "Arial" or FONT_BOLD_YUKLENDI) else ""
        
    pdf.set_font(font_family, header_style, 14)
    pdf.cell(0, 10, to_pdf_text(baslik), ln=True, align='C')
    pdf.ln(5)
    
    if not df.empty:
        pdf.set_font(font_family, header_style, 10)
        w = col_widths if col_widths else [190 / len(df.columns)] * len(df.columns)
        for i, col in enumerate(df.columns):
            pdf.cell(w[i], 10, to_pdf_text(col), border=1, align='C')
        pdf.ln()
        
        for _, row in df.iterrows():
            for i, item in enumerate(row):
                align = 'C' if w[i] < 26 else 'L' 
                text = str(item)
                
                is_bold = False
                if text.startswith("**") and text.endswith("**"):
                    is_bold = True
                    text = text[2:-2]
                    
                pdf_text = to_pdf_text(text)
                
                cell_style = 'B' if is_bold and (font_family == "Arial" or FONT_BOLD_YUKLENDI) else ""
                
                original_size = 9
                pdf.set_font(font_family, cell_style, original_size)
                current_size = original_size
                
                while pdf.get_string_width(pdf_text) > (w[i] - 2) and current_size > 5:
                    current_size -= 0.5
                    pdf.set_font(font_family, cell_style, current_size)
                if pdf.get_string_width(pdf_text) > (w[i] - 2):
                    while pdf.get_string_width(pdf_text + "..") > (w[i] - 2) and len(pdf_text) > 0:
                        pdf_text = pdf_text[:-1]
                    pdf_text += ".."
                pdf.cell(w[i], 8, pdf_text, border=1, align=align)
            pdf.ln()
    return bytes(pdf.output())

# ==============================================================================
# 2. ŞİFRELİ GİRİŞ / MİSAFİR MODU
# ==============================================================================
with st.sidebar:
    st.divider()
    st.markdown("### 👨‍⚖️ Turnuva Yönetimi")
    if not st.session_state.admin_mi:
        st.info(f"👁️ Şu an **{st.session_state.aktif_yas}** verilerini İzleyici Modunda görüyorsunuz.")
        girilen_sifre = st.text_input("Başhakem Şifresi:", type="password")
        if st.button("🔒 Giriş Yap"):
            beklenen_sifre = SIFRELER.get(st.session_state.aktif_yas)
            if girilen_sifre == beklenen_sifre:
                st.session_state.admin_mi = True
                st.success(f"✅ {st.session_state.aktif_yas} Başhakem Yetkisi Aktif!")
                st.rerun()
            else:
                st.error("❌ Hatalı Şifre!")
    else:
        st.success(f"🟢 **Aktif Mod:** {st.session_state.aktif_yas} Başhakem")
        if st.button("🔓 Çıkış Yap (İzleyici Modu)"):
            st.session_state.admin_mi = False
            st.rerun()
            
    st.divider()
    if not st.session_state.admin_mi:
        active_cat = st.selectbox("🎾 Fikstür Kategorisi:", ["Erkekler", "Kadınlar"])
    else:
        active_cat = st.radio("🎾 Fikstür Kategorisi:", ["Erkekler", "Kadınlar"])

cat_data = st.session_state.data[active_cat]

# ==============================================================================
# 3. ÖZEL CSS
# ==============================================================================
st.markdown("""
<style>
.match-wrapper { height: 135px; margin-bottom: 5px; }
.match-card {
    border: 1px solid #1f77b4; border-radius: 6px; padding: 6px; 
    background-color: #f8f9fa; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); height: 100%;
}
.match-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #ddd; margin-bottom: 4px; padding-bottom: 2px; }
.match-label { font-size: 11px; font-weight: bold; color: #1f77b4; }
.match-number { font-size: 11px; font-weight: bold; color: #fff; background-color: #1f77b4; padding: 1px 5px; border-radius: 4px; }
.player-name { font-size: 13px; font-weight: 500; color: #333; padding: 2px 0; overflow: hidden; white-space: nowrap; text-overflow: ellipsis;}
.player-src { font-size: 11px; color: #444; font-weight: bold; font-style: italic; margin-top: -2px; margin-bottom: 2px; }
.player-separator { border-top: 1px dashed #ccc; margin: 2px 0; }

.print-only-score { display: none; font-size: 10px; font-weight: bold; text-align: center; color: #1f77b4; margin-top: 3px; border-top: 1px dashed #bbb; padding-top: 3px; }

@media print {
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stMainView"], section {
        overflow: visible !important;
        height: auto !important;
        max-height: none !important;
        display: block !important;
    }
    header, footer, [data-testid="stSidebar"], .stTabs [data-baseweb="tab-list"], 
    .stSelectbox, .stRadio, .stTextInput, button, .stExpander, .no-print { display: none !important; }
    .stTabs { margin-top: 0 !important; }
    [data-testid="stHorizontalBlock"] { display: flex !important; flex-wrap: nowrap !important; }
    [data-testid="column"] { flex: 1 1 0% !important; min-width: 0 !important; display: block !important; }
    * { -webkit-print-color-adjust: exact !important; color-adjust: exact !important; }
    .match-wrapper { page-break-inside: avoid; }
    .match-card { border: 1px solid #000; background-color: #eee !important; margin-bottom: 2px !important; }
    .page-break { page-break-before: always !important; display: block !important; margin-top: 20px !important;} 
    
    .print-only-score { display: block !important; }
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# SEKME YÖNETİMİ
# ==========================================
st.title(f"🎾 {st.session_state.aktif_yas} Milli Takım Belirleme Turnuvası")
tab_fikstur, tab_program, tab_siralama, tab_dosya = st.tabs(["🏆 Fikstürler", "📅 Maç Programı", "🇹🇷 Sıralama", "⚙️ Veri Yönetimi"])
p = cat_data['players']

# ==========================================
# TAB 1: BİRLEŞTİRİLMİŞ FİKSTÜR EKRANI
# ==========================================
with tab_fikstur:
    c_view1, c_view2 = st.columns([3, 1])
    with c_view1:
        gorunum = st.radio("👀 Görünüm:", ["İkisini de Göster", "Sadece Ana Tablo", "Sadece Teselli"], horizontal=True, label_visibility="collapsed")
    with c_view2:
        try:
            pdf_bytes = generate_bracket_pdf(cat_data, active_cat, FPDF, to_pdf_text, FONT_YUKLENDI)
            st.download_button("📄 Ağacı PDF İndir", data=pdf_bytes, file_name=f"{st.session_state.aktif_yas[:2]}_yas_{active_cat}_fikstur.pdf", mime="application/pdf", key="dl_bracket_pdf")
        except Exception as e:
            st.caption(f"PDF oluşturulamadı: {e}")
    st.divider()

    show_ana = gorunum in ["İkisini de Göster", "Sadece Ana Tablo"]
    show_tes = gorunum in ["İkisini de Göster", "Sadece Teselli"]

    bracket_state = compute_bracket_state(cat_data)

    if show_ana:
        st.markdown(f"#### 🏆 {active_cat} Ana Tablosu")
        st.markdown(render_main_bracket_svg(bracket_state), unsafe_allow_html=True)

    if show_ana and show_tes:
        st.markdown("<div class='page-break'></div><br class='no-print'><hr class='no-print' style='border: 2px dashed #1f77b4; margin: 20px 0;'><br class='no-print'>", unsafe_allow_html=True)

    if show_tes:
        st.markdown(f"#### 🔄 {active_cat} Teselli Tablosu")
        st.markdown(render_consolation_bracket_svg(bracket_state), unsafe_allow_html=True)

    if st.session_state.admin_mi:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### ✏️ Günlük Skor Girişi")
        
        GUNLUK_MACLAR = {
            "1. GÜN MAÇLARI": [
                ("MR1_0","Ana R1","M1"),("MR1_1","Ana R1","M2"),("MR1_2","Ana R1","M3"),("MR1_3","Ana R1","M4"),
                ("MR1_4","Ana R1","M5"),("MR1_5","Ana R1","M6"),("MR1_6","Ana R1","M7"),("MR1_7","Ana R1","M8")
            ],
            "2. GÜN MAÇLARI": [
                ("MQF_0","Ana ÇF","M9"),("MQF_1","Ana ÇF","M10"),("MQF_2","Ana ÇF","M11"),("MQF_3","Ana ÇF","M12"),
                ("CR1_0","T-R1","M16"),("CR1_1","T-R1","M17"),("CR1_2","T-R1","M18"),("CR1_3","T-R1","M19"),
                ("CR2_0","T-ÇF","M20"),("CR2_1","T-ÇF","M21"),("CR2_2","T-ÇF","M22"),("CR2_3","T-ÇF","M23")
            ],
            "3. GÜN MAÇLARI": [
                ("MSF_0","Ana YF","M13"),("MSF_1","Ana YF","M14"),
                ("CR3_0","T-YF1","M24"),("CR3_1","T-YF1","M25"),
                ("CR4_0","T-YF2","M26"),("CR4_1","T-YF2","M27"),
                ("MATCH_7_8","7.-8.'LİK","M30")
            ],
            "4. GÜN MAÇLARI": [
                ("FINAL_MAIN","FİNAL","M15"),("FINAL_TESELLI","3.-4.'LÜK","M28"),("MATCH_5_6","5.-6.'LIK","M29")
            ]
        }

        degisti = False
        for gun_baslik, mac_listesi in GUNLUK_MACLAR.items():
            with st.expander(f"📅 {gun_baslik}", expanded=False):
                for mid, lbl, mno in mac_listesi:
                    d = bracket_state[mid]
                    p1, p2 = d.get("p1"), d.get("p2")
                    cw, cs = st.columns([3, 1.3])
                    
                    if p1 and p2:
                        mevcut_kazanan = cat_data['res'].get(mid, {}).get("w", "-")
                        mevcut_skor = cat_data['scores'].get(mid, "")
                        secenekler = ["-", p1, p2]
                        idx = secenekler.index(mevcut_kazanan) if mevcut_kazanan in secenekler else 0
                        
                        secilen = cw.selectbox(f"{lbl} · {mno}: {p1}  vs  {p2}", secenekler, index=idx, key=f"tab1_edit_sel_{active_cat}_{mid}")
                        skor = cs.text_input("Skor", value=mevcut_skor, key=f"tab1_edit_sk_{active_cat}_{mid}", label_visibility="collapsed", placeholder="Skor")
                        
                        if secilen != mevcut_kazanan or skor != mevcut_skor:
                            cat_data['scores'][mid] = clean_html_text(skor)
                            if secilen != "-":
                                kaybeden = p2 if secilen == p1 else p1
                                cat_data['res'][mid] = {"w": secilen, "l": kaybeden}
                            elif mid in cat_data['res']:
                                del cat_data['res'][mid]
                            degisti = True
                    else:
                        p1_disp = p1 if p1 else "Bekleniyor..."
                        p2_disp = p2 if p2 else "Bekleniyor..."
                        cw.markdown(f"<div style='padding-top: 8px; font-size: 14px; color: #555;'>{lbl} · {mno}: <b>{p1_disp}</b> vs <b>{p2_disp}</b></div>", unsafe_allow_html=True)
                        cs.text_input("Skor", value="", key=f"tab1_edit_sk_dis_{active_cat}_{mid}", disabled=True, label_visibility="collapsed", placeholder="Skor")
        
        if degisti:
            bracket_state = compute_bracket_state(cat_data)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(f"💾 {st.session_state.aktif_yas} - {active_cat} Skorlarını Kaydet", use_container_width=True, key="btn_save_all"):
            save_data()
            st.success("Tüm fikstür değişiklikleri başarıyla kaydedildi!")

# ==========================================
# TAB 2: ORTAK MAÇ PROGRAMI
# ==========================================
with tab_program:
    st.subheader("📅 Ortak Maç Programı")
        
    c_f1, c_f2, c_f3 = st.columns(3)
    secilen_gun = c_f1.selectbox("📅 Gün Seçimi:", ["Tüm Günler", "1. GÜN", "2. GÜN", "3. GÜN", "4. GÜN"])
    secilen_kategori = c_f2.selectbox("🎾 Kategori Seçimi:", ["Tümü", "Erkekler", "Kadınlar"])
    tablo_filtresi = c_f3.selectbox("📊 Tablo Gösterimi:", ["İkisini de Göster", "Sadece Ana Tablo", "Sadece Teselli"])

    pdf_program_data = []

    def draw_schedule(cat_name, matches, day_name):
        cat_d = st.session_state.data[cat_name]
        b_state = compute_bracket_state(cat_d)
        
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
        
        day_key_safe = day_name.replace(" ", "_").replace(".", "")

        for m_id, label in filtered_matches:
            match_data = b_state.get(m_id, {})
            p1 = match_data.get("p1") or "Bekleniyor..."
            p2 = match_data.get("p2") or "Bekleniyor..."
            
            winner = cat_d['res'].get(m_id, {}).get("w", None)
            
            p1_clean = clean_html_text(p1)
            p2_clean = clean_html_text(p2)
            
            is_p1_winner = (winner and p1 == winner)
            is_p2_winner = (winner and p2 == winner)
            
            pdf_p1 = f"**{p1_clean}**" if is_p1_winner else p1_clean
            pdf_p2 = f"**{p2_clean}**" if is_p2_winner else p2_clean
            
            ui_p1 = f"<b>{p1_clean}</b>" if is_p1_winner else p1_clean
            ui_p2 = f"<b>{p2_clean}</b>" if is_p2_winner else p2_clean
            
            bracket_score = cat_d['scores'].get(m_id, "")
            data = cat_d['schedule_data'].get(m_id, {"saat": "", "kort": ""}) 
            
            pdf_tur = label.replace("Ana Tablo", "AT").replace("T-", "FC ")
            pdf_tur = pdf_tur.replace("3.-4.'lük Maçı", "FC 3-4").replace("5.-6.'lık Maçı", "FC 5-6").replace("7.-8.'lik Maçı", "FC 7-8")

            pdf_program_data.append({
                "Tarih/Gün": pdf_tarih, "Kat.": pdf_kategori, "Tur": pdf_tur, "Saat": data.get("saat", "-"), "Kort": data.get("kort", "-"),
                "Oyuncu 1": pdf_p1, "Oyuncu 2": pdf_p2, "Skor": bracket_score if bracket_score else "-"
            })

            bg_style = ""
            if m_id.startswith("MQF_") or m_id.startswith("CR1_"):
                try:
                    mac_index = int(m_id.split("_")[1])
                    if m_id.startswith("MQF_"):
                        color_idx = 3 - mac_index
                    else:
                        color_idx = mac_index
                        
                    renkler = {0: "#d0ebff", 1: "#d3f9d8", 2: "#fff3bf", 3: "#ffc9c9"}
                    bg_renk = renkler.get(color_idx, "")
                    if bg_renk:
                        bg_style = f"background-color: {bg_renk}; color: #000; padding: 4px; border-radius: 4px; margin-bottom: 2px;"
                except:
                    pass
            elif m_id.startswith("MSF_") or m_id.startswith("CR3_"):
                try:
                    mac_index = int(m_id.split("_")[1])
                    color_idx = mac_index
                    renkler = {0: "#d0ebff", 1: "#d3f9d8"}
                    bg_renk = renkler.get(color_idx, "")
                    if bg_renk:
                        bg_style = f"background-color: {bg_renk}; color: #000; padding: 4px; border-radius: 4px; margin-bottom: 2px;"
                except:
                    pass

            c1, c2, c3, c4, c5, c6 = st.columns([1.5, 2, 2, 1, 1, 1])
            
            if bg_style:
                c1.markdown(f"<div style='{bg_style}'><b>{label}</b></div>", unsafe_allow_html=True)
                c2.markdown(f"<div style='{bg_style}'>{ui_p1}</div>", unsafe_allow_html=True)
                c3.markdown(f"<div style='{bg_style}'>{ui_p2}</div>", unsafe_allow_html=True)
            else:
                c1.markdown(label, unsafe_allow_html=True)
                c2.markdown(ui_p1, unsafe_allow_html=True)
                c3.markdown(ui_p2, unsafe_allow_html=True)
            
            if not st.session_state.admin_mi:
                c4.write(data.get("saat", "-"))
                c5.write(data.get("kort", "-"))
                c6.write(clean_html_text(bracket_score) if bracket_score else "-")
            else:
                new_saat = c4.text_input("Saat", value=data.get("saat", ""), key=f"t_{cat_name}_{m_id}_{day_key_safe}", label_visibility="collapsed")
                new_kort = c5.text_input("Kort", value=data.get("kort", ""), key=f"c_{cat_name}_{m_id}_{day_key_safe}", label_visibility="collapsed")
                new_skor = c6.text_input("Skor", value=bracket_score, key=f"s_{cat_name}_{m_id}_{day_key_safe}", label_visibility="collapsed")
                
                if new_saat != data.get("saat") or new_kort != data.get("kort"):
                    cat_d['schedule_data'][m_id] = {"saat": new_saat, "kort": new_kort}
                if new_skor != bracket_score:
                    cat_d['scores'][m_id] = clean_html_text(new_skor)

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
        if st.button(f"💾 {st.session_state.aktif_yas} Maç Programını Kaydet", use_container_width=True, key="btn_save_prog"):
            save_data()
            st.success("Maç programı başarıyla kaydedildi!")

    if pdf_program_data:
        st.divider()
        pdf_prog_df = pd.DataFrame(pdf_program_data)
        prog_col_widths = [29, 9, 21, 12, 12, 42, 42, 23]
        btn_pdf_prog = generate_pdf(pdf_prog_df, f"{st.session_state.aktif_yas} Mac Programi", col_widths=prog_col_widths)
        st.download_button("📥 Ekrandaki Maç Programını PDF Olarak İndir", data=btn_pdf_prog, file_name=f"{st.session_state.aktif_yas[:2]}_yas_program.pdf", mime="application/pdf")

# ==========================================
# TAB 3: SIRALAMA
# ==========================================
with tab_siralama:
    st.subheader(f"🇹🇷 {st.session_state.aktif_yas} Kesin Sıralama")
    
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
            player_name = clean_html_text(player_name)
            pdf_siralama_data.append({"Sıra": rank, "Kategori": k_adi, "Oyuncu Adı": player_name})
            
            c_no, c_isim = st.columns([0.5, 4])
            c_no.markdown(f"<div style='font-size:16px; font-weight:bold; padding:5px; background:#e0e0e0; text-align:center; border-radius:5px;'>{rank}</div>", unsafe_allow_html=True)
            c_isim.markdown(f"<div style='font-size:16px; padding:5px;'>{player_name}</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
    if pdf_siralama_data:
        st.divider()
        pdf_sir_df = pd.DataFrame(pdf_siralama_data)
        sir_col_widths = [15, 30, 145]
        btn_pdf_sir = generate_pdf(pdf_sir_df, f"{st.session_state.aktif_yas} Siralamasi ({sira_kategori})", col_widths=sir_col_widths)
        st.download_button("📥 Sıralamayı PDF Olarak İndir", data=btn_pdf_sir, file_name=f"{st.session_state.aktif_yas[:2]}_yas_siralama.pdf", mime="application/pdf")

# ==========================================
# TAB 4: YEDEKLEME VE DOSYA (Sadece Admin)
# ==========================================
with tab_dosya:
    if st.session_state.admin_mi:
        st.subheader("📥 Veri Yönetimi ve Oyuncu Listesi")
        
        st.markdown(f"**1. Esame Listesini Güncelle ({active_cat})**")
        
        mevcut_isimler = [clean_html_text(x) for x in cat_data['players']]
        txt = st.text_area("16 Oyuncu girin (1. Seribaşı en üstte):", value="\n".join(mevcut_isimler), height=150)
        
        if st.button("👥 Listeyi Kaydet"):
            temiz_isimler = []
            for name in txt.splitlines():
                temiz = clean_html_text(name)
                if temiz:
                    temiz_isimler.append(temiz)
                    
            cat_data['players'] = temiz_isimler
            clean_ghost_data(st.session_state.data)
            save_data()
            st.success("Liste güncellendi!")
            st.rerun()
            
        st.divider()
        st.markdown("**2. Sistemi Yedekle / Geri Yükle**")
        c_sv, c_ld = st.columns(2)
        
        data_to_save = json.dumps(st.session_state.data, ensure_ascii=False)
        c_sv.download_button(f"📥 {st.session_state.aktif_yas} Verisini Yedekle (.json)", data=data_to_save, file_name=DB_FILE)
        
        uploaded_file = c_ld.file_uploader(f"📤 {st.session_state.aktif_yas} Dosyasını Geri Yükle", type="json")
        if uploaded_file and c_ld.button("Yüklenen Veriyi Uygula"):
            try:
                yeni_veri = json.load(uploaded_file)
            except Exception:
                st.error("❌ Dosya geçerli bir JSON değil. Yükleme iptal edildi.")
                st.stop()

            gerekli_anahtarlar = {"Erkekler", "Kadınlar"}
            if not isinstance(yeni_veri, dict) or not gerekli_anahtarlar.issubset(yeni_veri.keys()):
                st.error("❌ Bu dosya beklenen turnuva yapısında değil ('Erkekler'/'Kadınlar' eksik). Yükleme iptal edildi, mevcut veriniz korundu.")
                st.stop()

            for cat in ["Erkekler", "Kadınlar"]:
                for alan, varsayilan in [("players", []), ("res", {}), ("scores", {}), ("schedule_data", {})]:
                    if alan not in yeni_veri[cat]:
                        yeni_veri[cat][alan] = varsayilan
            if "publish" not in yeni_veri:
                yeni_veri["publish"] = {"gun": "Tüm Günler", "filtre": "Tümü", "kategori": "Tümü", "dates": {}}
            if "dates" not in yeni_veri["publish"]:
                yeni_veri["publish"]["dates"] = {}

            st.session_state.data = yeni_veri
            save_data()
            st.success(f"{st.session_state.aktif_yas} verisi geri yüklendi!")
            st.rerun()
    else:
        st.warning("🔒 Bu panel sadece Başhakem erişimine açıktır.")
