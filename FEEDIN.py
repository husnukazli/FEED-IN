import sys
import subprocess
import os

# ==============================================================================
# 0. OTOMATİK KÜTÜPHANE YÜKLEYİCİ
# ==============================================================================
try:
    import PyPDF2
except ImportError:
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyPDF2"])
        import PyPDF2
    except:
        pass

try:
    import fitz  
except ImportError:
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyMuPDF"])
        import fitz
    except:
        pass

try:
    from PIL import Image
except ImportError:
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    except:
        pass

import streamlit as st
import json
import shutil
import pandas as pd
import datetime
import re
import html
import copy
import base64
import io
from fpdf import FPDF

import bracket_engine
from bracket_engine import compute_bracket_state

import bracket_pdf
from bracket_svg import render_main_bracket_svg, render_consolation_bracket_svg
from bracket_pdf import generate_bracket_pdf

st.set_page_config(layout="wide", page_title="Milli Takım Belirleme Turnuvaları", initial_sidebar_state="collapsed")

# ==============================================================================
# 1. DOSYA VE FONKSİYONLAR
# ==============================================================================
FONT_YUKLENDI = os.path.exists("arial.ttf")

BOLD_FONT_FILE = None
for fname in ["arialbd.ttf", "ArialBD.ttf", "ARIALBD.TTF", "arial bd.ttf", "Arial BD.ttf"]:
    if os.path.exists(fname):
        BOLD_FONT_FILE = fname
        break

FONT_BOLD_YUKLENDI = BOLD_FONT_FILE is not None

class TurnuvaFPDF(FPDF):
    def header(self):
        try:
            if os.path.exists("ttf_logo.png"):
                wm_path = "ttf_logo_wm.png"
                if not os.path.exists(wm_path):
                    from PIL import Image
                    img = Image.open("ttf_logo.png").convert("RGBA")
                    alpha = img.split()[3]
                    alpha = alpha.point(lambda p: p * 0.05)
                    img.putalpha(alpha)
                    img.save(wm_path, "PNG")
                
                img_w = 110
                x = (self.w - img_w) / 2
                y = (self.h - img_w) / 2
                self.image(wm_path, x=x, y=y, w=img_w)
        except:
            pass

    def set_font(self, family=None, style='', size=0):
        if not hasattr(self, '_fonts_injected'):
            self._fonts_injected = False
            
        if FONT_YUKLENDI:
            if not self._fonts_injected:
                try:
                    self.add_font("ArialTR", "", "arial.ttf", uni=True)
                    if FONT_BOLD_YUKLENDI:
                        self.add_font("ArialTR", "B", BOLD_FONT_FILE, uni=True)
                except:
                    pass
                self._fonts_injected = True
            
            family = "ArialTR"
            if not isinstance(style, str):
                style = getattr(style, 'name', '')
            if style == 'NONE' or style == 'REGULAR':
                style = ''
            if 'B' in style and not FONT_BOLD_YUKLENDI:
                style = style.replace('B', '')
        
        super().set_font(family, style, size)

SIFRELER = {
    "12 Yaş": "hakem12",
    "14 Yaş": "hakem14",
    "16 Yaş": "hakem16",
    "18 Yaş": "hakem18"
}

SRC_MAP = {
    "MQF_0_p1": "M1 Kazananı", "MQF_0_p2": "M2 Kazananı", "MQF_1_p1": "M3 Kazananı", "MQF_1_p2": "M4 Kazananı",
    "MQF_2_p1": "M5 Kazananı", "MQF_2_p2": "M6 Kazananı", "MQF_3_p1": "M7 Kazananı", "MQF_3_p2": "M8 Kazananı",
    "MSF_0_p1": "M9 Kazananı", "MSF_0_p2": "M10 Kazananı", "MSF_1_p1": "M11 Kazananı", "MSF_1_p2": "M12 Kazananı",
    "FINAL_MAIN_p1": "M13 Kazananı", "FINAL_MAIN_p2": "M14 Kazananı",
    "CR1_0_p1": "M1 Kaybedeni", "CR1_0_p2": "M2 Kaybedeni", "CR1_1_p1": "M3 Kaybedeni", "CR1_1_p2": "M4 Kaybedeni",
    "CR1_2_p1": "M5 Kaybedeni", "CR1_2_p2": "M6 Kaybedeni", "CR1_3_p1": "M7 Kaybedeni", "CR1_3_p2": "M8 Kaybedeni",
    "CR2_0_p1": "M16 Kazananı", "CR2_0_p2": "M12 Kaybedeni", "CR2_1_p1": "M17 Kazananı", "CR2_1_p2": "M11 Kaybedeni",
    "CR2_2_p1": "M18 Kazananı", "CR2_2_p2": "M10 Kaybedeni", "CR2_3_p1": "M19 Kazananı", "CR2_3_p2": "M9 Kazananı",
    "CR3_0_p1": "M20 Kazananı", "CR3_0_p2": "M21 Kazananı", "CR3_1_p1": "M22 Kazananı", "CR3_1_p2": "M23 Kazananı",
    "CR4_0_p1": "M24 Kazananı", "CR4_0_p2": "M13 Kaybedeni", "CR4_1_p1": "M25 Kazananı", "CR4_1_p2": "M14 Kaybedeni",
    "FINAL_TESELLI_p1": "M26 Kazananı", "FINAL_TESELLI_p2": "M27 Kazananı",
    "MATCH_5_6_p1": "M26 Kaybedeni", "MATCH_5_6_p2": "M27 Kaybedeni",
    "MATCH_7_8_p1": "M24 Kaybedeni", "MATCH_7_8_p2": "M25 Kaybedeni",
}

if 'aktif_yas' not in st.session_state: st.session_state.aktif_yas = "Seçilmedi"
if "admin_mi" not in st.session_state: st.session_state.admin_mi = False
if "active_cat" not in st.session_state: st.session_state.active_cat = "Erkekler"
if "secilen_gun_tab2" not in st.session_state: st.session_state.secilen_gun_tab2 = "Tüm Günler"

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

def get_sorted_matches(matches_list, cat_d, filtre):
    filtered = []
    sort_pref = st.session_state.data['publish'].get('sort_by', 'match_no')
    
    for idx, (m_id, label) in enumerate(matches_list):
        is_cons = m_id.startswith("CR") or "TESELLI" in m_id or "5_6" in m_id or "7_8" in m_id
        if filtre == "Sadece Ana Tablo" and is_cons: continue
        if filtre == "Sadece FEED IN" and not is_cons: continue
        
        time_val = 999999 
        if sort_pref == "time":
            saat_str = cat_d['schedule_data'].get(m_id, {}).get("saat", "")
            m = re.search(r'(\d{1,2})[:.](\d{2})', saat_str)
            if m: time_val = int(m.group(1)) * 60 + int(m.group(2))
        
        filtered.append((m_id, label, idx, time_val))
        
    if sort_pref == "time": filtered.sort(key=lambda x: (x[3], x[2]))
    else: filtered.sort(key=lambda x: x[2])
    return [(x[0], x[1]) for x in filtered]

def clean_html_text(text):
    if not isinstance(text, str): return str(text)
    t = html.unescape(text)
    t = re.sub(r'<[^>]+>', '', t)
    return t.strip()

DB_FILE = f"turnuva_db_{st.session_state.aktif_yas[:2]}.json"

def load_data():
    default_data = {
        'Erkekler': {'players': [f"Oyuncu {i}" for i in range(1, 17)], 'res': {}, 'scores': {}, 'schedule_data': {}},
        'Kadınlar': {'players': [f"Oyuncu {i}" for i in range(1, 17)], 'res': {}, 'scores': {}, 'schedule_data': {}},
        'publish': {'gun': 'Tüm Günler', 'filtre': 'Tümü', 'kategori': 'Tümü', 'dates': {}, 'ikort_link': '', 'sort_by': 'match_no'}
    }
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if 'publish' not in data: data['publish'] = default_data['publish']
                return data
        except Exception:
            pass
    return default_data

def save_data():
    if os.path.exists(DB_FILE):
        try: shutil.copyfile(DB_FILE, DB_FILE + ".bak")
        except: pass
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
                l = res_dict.get("l")
                
                # Hepsi WO seçeneği ghost player koruması (silinmesini engeller)
                if w and (w != p1 and w != p2 and w != "Hepsi WO"):
                    keys_to_delete.append(mid)
                    cleaned_in_loop = True; degisiklik_oldu = True
                elif l and (l != p1 and l != p2 and l != "Hepsi WO"):
                    keys_to_delete.append(mid)
                    cleaned_in_loop = True; degisiklik_oldu = True
                    
            for k in set(keys_to_delete):
                if k in data[cat]['res']: del data[cat]['res'][k]
            if not cleaned_in_loop: break
    return degisiklik_oldu

if 'data' not in st.session_state:
    st.session_state.data = load_data()
    for cat in ['Erkekler', 'Kadınlar']:
        temiz_liste = [clean_html_text(p) for p in st.session_state.data[cat]['players'] if clean_html_text(p)]
        while len(temiz_liste) < 16: temiz_liste.append(f"Oyuncu {len(temiz_liste)+1}")
        st.session_state.data[cat]['players'] = temiz_liste[:16]
    if clean_ghost_data(st.session_state.data): save_data()

def format_date_tr(date_str):
    if not date_str: return ""
    try:
        d = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
        return f"{d.strftime('%d.%m.%Y')} {gunler[d.weekday()]}"
    except: return date_str

def to_pdf_text(text):
    if FONT_YUKLENDI: return str(text)
    t = str(text).replace("İ", "I").replace("ı", "i").replace("Ş", "S").replace("ş", "s").replace("Ğ", "G").replace("ğ", "g").replace("Ç", "C").replace("ç", "c").replace("Ö", "O").replace("ö", "o").replace("Ü", "U").replace("ü", "u")
    return t.encode('latin-1', 'replace').decode('latin-1')

def generate_pdf(df, baslik, col_widths=None, aligns=None):
    pdf = TurnuvaFPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("ArialTR", 'B', 16)
    pdf.cell(0, 10, to_pdf_text(baslik), ln=True, align='C')
    pdf.ln(5)
    if not df.empty:
        w = col_widths if col_widths else [190 / len(df.columns)] * len(df.columns)
        if not aligns: aligns = ['C'] * len(df.columns)
        pdf.set_fill_color(31, 119, 180); pdf.set_text_color(255, 255, 255); pdf.set_font("ArialTR", 'B', 11)
        for i, col in enumerate(df.columns): pdf.cell(w[i], 8, to_pdf_text(col), border=1, align=aligns[i], fill=True)
        pdf.ln(); pdf.set_text_color(0, 0, 0)
        for row_idx, row in df.iterrows():
            pdf.set_fill_color(255, 255, 255) if row_idx % 2 == 0 else pdf.set_fill_color(242, 246, 250)
            for i, item in enumerate(row):
                align = aligns[i]; text = str(item); is_bold = False
                if text.startswith("**") and text.endswith("**"):
                    is_bold = True; text = text[2:-2]
                pdf_text = to_pdf_text(text)
                cell_style = 'B' if is_bold else ""
                cur_size = 11; pdf.set_font("ArialTR", cell_style, cur_size)
                while pdf.get_string_width(pdf_text) > (w[i] - 2) and cur_size > 5:
                    cur_size -= 0.5; pdf.set_font("ArialTR", cell_style, cur_size)
                if pdf.get_string_width(pdf_text) > (w[i] - 2):
                    while pdf.get_string_width(pdf_text + "..") > (w[i] - 2) and len(pdf_text) > 0: pdf_text = pdf_text[:-1]
                    pdf_text += ".."
                pdf.cell(w[i], 7.5, pdf_text, border=1, align=align, fill=True)
            pdf.ln()
    return bytes(pdf.output())

# ==============================================================================
# UI BAŞLANGIÇ
# ==============================================================================
if st.session_state.aktif_yas == "Seçilmedi":
    ttf_b64 = get_base64_image("ttf_logo.png")
    if ttf_b64: st.markdown(f'<div style="text-align: center; margin-bottom: 10px;"><img src="data:image/png;base64,{ttf_b64}" width="150"></div>', unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #1f77b4;'>Milli Takım Belirleme Turnuvaları</h1>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    st.markdown('<style>div[data-testid="column"] button { height: 80px; font-size: 20px !important; font-weight: bold; border-radius: 10px; }</style>', unsafe_allow_html=True)
    if c1.button("🎾 12 YAŞ", use_container_width=True): st.session_state.aktif_yas = "12 Yaş"; st.rerun()
    if c2.button("🎾 14 YAŞ", use_container_width=True): st.session_state.aktif_yas = "14 Yaş"; st.rerun()
    if c3.button("🎾 16 YAŞ", use_container_width=True): st.session_state.aktif_yas = "16 Yaş"; st.rerun()
    if c4.button("🎾 18 YAŞ", use_container_width=True): st.session_state.aktif_yas = "18 Yaş"; st.rerun()
    st.stop()

with st.sidebar:
    st.markdown("### 👨‍⚖️ Hakem Yönetim Paneli")
    if not st.session_state.admin_mi:
        st.info(f"👁️ **{st.session_state.aktif_yas}** İzleyici Modu")
        girilen_sifre = st.text_input("Başhakem Şifresi:", type="password")
        if st.button("🔒 Giriş Yap"):
            if girilen_sifre == SIFRELER.get(st.session_state.aktif_yas):
                st.session_state.admin_mi = True; st.rerun()
            else: st.error("❌ Hatalı Şifre!")
    else:
        st.success(f"🟢 **Aktif Mod:** {st.session_state.aktif_yas} Başhakem")
        if st.button("🔓 Çıkış Yap"): st.session_state.admin_mi = False; st.rerun()

st.markdown("""<style>
.mobile-table th { background-color: #f0f2f6; color: #31333F; padding: 10px; text-align: left; border-bottom: 2px solid #ddd; }
.mobile-table td { padding: 8px 10px; border-bottom: 1px solid #eee; }
@media print { header, footer, [data-testid="stSidebar"], .stTabs [data-baseweb="tab-list"], button, .no-print { display: none !important; } }
</style>""", unsafe_allow_html=True)

c_logo, c_title = st.columns([1, 8])
with c_logo:
    ttf_b64 = get_base64_image("ttf_logo.png")
    if ttf_b64: st.markdown(f'<img src="data:image/png;base64,{ttf_b64}" style="max-width:100%;">', unsafe_allow_html=True)
with c_title:
    st.title(f"{st.session_state.aktif_yas} Milli Takım Belirleme Turnuvası")
    ikort_url = st.session_state.data['publish'].get('ikort_link', '')
    if ikort_url: st.link_button("🔗 Turnuvanın i-Kort Sayfasına Git", ikort_url)

active_cat = st.session_state.active_cat = st.radio("**Kategori Seçimi:**", ["Erkekler", "Kadınlar"], horizontal=True)
cat_data = st.session_state.data[active_cat]

if st.session_state.admin_mi: tab_fikstur, tab_program, tab_siralama, tab_dosya = st.tabs(["🏆 Fikstürler", "📅 Maç Programı", "🇹🇷 Sıralama", "⚙️ Veri Yönetimi"])
else: tab_fikstur, tab_program, tab_siralama = st.tabs(["🏆 Fikstürler", "📅 Maç Programı", "🇹🇷 Sıralama"]); tab_dosya = None

with tab_fikstur:
    c_view1, c_view2 = st.columns([3, 1])
    with c_view1: gorunum = st.radio("Görünüm:", ["İkisini de Göster", "Sadece Ana Tablo", "Sadece FEED IN"], horizontal=True, label_visibility="collapsed")
    
    bracket_state = compute_bracket_state(cat_data)
    display_bracket_state = copy.deepcopy(bracket_state)
    for mid, d in display_bracket_state.items():
        if not d.get("p1"): display_bracket_state[mid]["p1"] = SRC_MAP.get(f"{mid}_p1", "Bekleniyor...")
        if not d.get("p2"): display_bracket_state[mid]["p2"] = SRC_MAP.get(f"{mid}_p2", "Bekleniyor...")

    with c_view2:
        if st.session_state.admin_mi:
            pdf_bytes = None
            try:
                def display_compute(cat_d):
                    state = compute_bracket_state(cat_d)
                    for m_id, d_ in state.items():
                        if not d_.get("p1"): d_["p1"] = SRC_MAP.get(f"{m_id}_p1", "Bekleniyor...")
                        if not d_.get("p2"): d_["p2"] = SRC_MAP.get(f"{m_id}_p2", "Bekleniyor...")
                    return state
                bracket_engine.compute_bracket_state = display_compute
                if hasattr(bracket_pdf, 'compute_bracket_state'): bracket_pdf.compute_bracket_state = display_compute
                pdf_bytes = generate_bracket_pdf(cat_data, active_cat, TurnuvaFPDF, to_pdf_text, FONT_YUKLENDI)
            except Exception as e: pass
            finally:
                bracket_engine.compute_bracket_state = compute_bracket_state
                if hasattr(bracket_pdf, 'compute_bracket_state'): bracket_pdf.compute_bracket_state = compute_bracket_state
            if pdf_bytes: st.download_button("📄 Fikstürü PDF İndir", data=pdf_bytes, file_name=f"{st.session_state.aktif_yas[:2]}_{active_cat}_fikstur.pdf", mime="application/pdf")

    st.divider()
    if gorunum in ["İkisini de Göster", "Sadece Ana Tablo"]:
        st.markdown(f"#### {active_cat} Ana Tablosu")
        st.markdown(render_main_bracket_svg(display_bracket_state, active_cat), unsafe_allow_html=True)
    if gorunum in ["İkisini de Göster", "Sadece FEED IN"]:
        st.markdown(f"#### {active_cat} FEED IN Tablosu")
        st.markdown(render_consolation_bracket_svg(display_bracket_state, active_cat), unsafe_allow_html=True)

    if st.session_state.admin_mi:
        st.markdown("### ✏️ Günlük Skor Girişi")
        GUNLUK_MACLAR = {
            "1. GÜN MAÇLARI": [("MR1_0","AT-R1","M1"),("MR1_1","AT-R1","M2"),("MR1_2","AT-R1","M3"),("MR1_3","AT-R1","M4"),("MR1_4","AT-R1","M5"),("MR1_5","AT-R1","M6"),("MR1_6","AT-R1","M7"),("MR1_7","AT-R1","M8")],
            "2. GÜN MAÇLARI": [("MQF_0","AT-ÇF","M9"),("MQF_1","AT-ÇF","M10"),("MQF_2","AT-ÇF","M11"),("MQF_3","AT-ÇF","M12"),("CR1_0","FC-R1","M16"),("CR1_1","FC-R1","M17"),("CR1_2","FC-R1","M18"),("CR1_3","FC-R1","M19"),("CR2_0","FC-ÇF","M20"),("CR2_1","FC-ÇF","M21"),("CR2_2","FC-ÇF","M22"),("CR2_3","FC-ÇF","M23")],
            "3. GÜN MAÇLARI": [("MSF_0","AT-YF","M13"),("MSF_1","AT-YF","M14"),("CR3_0","FC-YF1","M24"),("CR3_1","FC-YF1","M25"),("CR4_0","FC-YF2","M26"),("CR4_1","FC-YF2","M27"),("MATCH_7_8","FC-7/8","M30")],
            "4. GÜN MAÇLARI": [("FINAL_MAIN","AT-FİNAL","M15"),("FINAL_TESELLI","FC-3/4","M28"),("MATCH_5_6","FC-5/6","M29")]
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
                        
                        # Açılır menüye "Hepsi WO" seçeneğini ekle
                        secenekler = []
                        for opt in ["-", p1, p2, "Hepsi WO"]:
                            if opt not in secenekler: secenekler.append(opt)
                            
                        idx = secenekler.index(mevcut_kazanan) if mevcut_kazanan in secenekler else 0
                        secilen = cw.selectbox(f"{lbl} · {mno}: {p1}  vs  {p2}", secenekler, index=idx, key=f"sel_{active_cat}_{mid}")
                        skor = cs.text_input("Skor", value=mevcut_skor, key=f"sk_{active_cat}_{mid}", label_visibility="collapsed", placeholder="Skor")
                        
                        if secilen != mevcut_kazanan or skor != mevcut_skor:
                            if secilen == "Hepsi WO" and secilen != mevcut_kazanan and not skor:
                                skor = "Double W/O"
                                
                            cat_data['scores'][mid] = clean_html_text(skor)
                            
                            if secilen != "-":
                                if secilen == "Hepsi WO":
                                    cat_data['res'][mid] = {"w": "Hepsi WO", "l": "Hepsi WO"}
                                else:
                                    kaybeden = p2 if secilen == p1 else p1
                                    cat_data['res'][mid] = {"w": secilen, "l": kaybeden}
                            elif mid in cat_data['res']:
                                del cat_data['res'][mid]
                            degisti = True
                    else:
                        p1_disp = p1 if p1 else SRC_MAP.get(f"{mid}_p1", "Bekleniyor...")
                        p2_disp = p2 if p2 else SRC_MAP.get(f"{mid}_p2", "Bekleniyor...")
                        cw.markdown(f"<div style='padding-top:8px;'>{lbl} · {mno}: <b>{p1_disp}</b> vs <b>{p2_disp}</b></div>", unsafe_allow_html=True)
                        cs.text_input("Skor", value="", key=f"dis_{active_cat}_{mid}", disabled=True, label_visibility="collapsed")
        
        if degisti: bracket_state = compute_bracket_state(cat_data)
        if st.button(f"💾 Skorları Kaydet", use_container_width=True): save_data(); st.rerun()

with tab_program:
    st.subheader("📅 Ortak Maç Programı")
    tablo_filtresi = "İkisini de Göster"
    
    if st.session_state.admin_mi:
        c_ayar1, c_ayar2 = st.columns(2)
        tablo_filtresi = c_ayar1.selectbox("📊 Tablo Gösterimi:", ["İkisini de Göster", "Sadece Ana Tablo", "Sadece FEED IN"])
        mevcut_siralama = st.session_state.data['publish'].get('sort_by', 'match_no')
        sec_sir = c_ayar2.selectbox("↕️ Yayın Sıralaması:", ["🔢 Maç Numarasına Göre", "🕒 Maç Saatine Göre"], index=0 if mevcut_siralama == 'match_no' else 1)
        if (yeni_sort := 'match_no' if "Numara" in sec_sir else 'time') != mevcut_siralama:
            st.session_state.data['publish']['sort_by'] = yeni_sort; save_data(); st.rerun()

    gunler_btn = [{"key":"Tüm Günler", "label": "Tüm Program"}] + [{"key": f"{i}. GÜN", "label": f"{i}. GÜN"} for i in range(1, 5)]
    cols = st.columns(len(gunler_btn))
    for i, g_info in enumerate(gunler_btn):
        if cols[i].button(g_info["label"], use_container_width=True, type="primary" if st.session_state.secilen_gun_tab2 == g_info["key"] else "secondary"):
            st.session_state.secilen_gun_tab2 = g_info["key"]; st.rerun()
            
    secilen_gun = st.session_state.secilen_gun_tab2
    pdf_program_data = []

    def draw_schedule(cat_name, matches, day_name):
        cat_d = st.session_state.data[cat_name]
        b_state = compute_bracket_state(cat_d)
        filtered_matches = get_sorted_matches(matches, cat_d, tablo_filtresi)
        if not filtered_matches: return

        st.markdown(f"<h5 style='color:#1f77b4; margin-top:10px;'>🎾 {cat_name} - {day_name}</h5>", unsafe_allow_html=True)
        html_rows = ""
        
        if st.session_state.admin_mi:
            h1, h2, h3, h4, h5, h6 = st.columns([1.5, 2, 2, 1, 1, 1])
            h1.markdown("**Maç Türü**"); h2.markdown("**Oyuncu 1**"); h3.markdown("**Oyuncu 2**"); h4.markdown("**Saat**"); h5.markdown("**Kort**"); h6.markdown("**Skor**")

        for m_id, label in filtered_matches:
            match_data = b_state.get(m_id, {})
            p1_raw = match_data.get("p1")
            p2_raw = match_data.get("p2")
            
            p1_disp = p1_raw if p1_raw else SRC_MAP.get(f"{m_id}_p1", "Bekleniyor...")
            p2_disp = p2_raw if p2_raw else SRC_MAP.get(f"{m_id}_p2", "Bekleniyor...")
            
            winner = cat_d['res'].get(m_id, {}).get("w", None)
            
            p1_clean = clean_html_text(p1_disp)
            p2_clean = clean_html_text(p2_disp)
            
            # Hayalet Oyuncu Ekranda Gösterimi
            if p1_clean == "Hepsi WO": p1_clean = "❌ Çift W/O"
            if p2_clean == "Hepsi WO": p2_clean = "❌ Çift W/O"
            
            is_p1_winner = (winner and p1_raw == winner and winner != "Hepsi WO")
            is_p2_winner = (winner and p2_raw == winner and winner != "Hepsi WO")
            
            pdf_p1 = f"**{p1_clean}**" if is_p1_winner else p1_clean
            pdf_p2 = f"**{p2_clean}**" if is_p2_winner else p2_clean
            ui_p1 = f"<b>{p1_clean}</b>" if is_p1_winner else p1_clean
            ui_p2 = f"<b>{p2_clean}</b>" if is_p2_winner else p2_clean
            
            bracket_score = cat_d['scores'].get(m_id, "")
            data = cat_d['schedule_data'].get(m_id, {"saat": "", "kort": ""}) 
            saat_val = data.get("saat", "") or "-"
            kort_val = data.get("kort", "") or "-"
            skor_val = bracket_score or "-"
            
            pdf_program_data.append({"Kat.": "E" if cat_name=="Erkekler" else "K", "Tur": label, "Saat": saat_val, "Kort": kort_val, "Oyuncu 1": pdf_p1, "Oyuncu 2": pdf_p2, "Skor": skor_val})

            bg_style = ""
            if m_id.startswith("MQF_") or m_id.startswith("CR1_") or m_id.startswith("MSF_") or m_id.startswith("CR3_"):
                bg_style = f"background-color: #f0f2f6; color: #000; padding: 4px; border-radius: 4px;"

            if st.session_state.admin_mi:
                c1, c2, c3, c4, c5, c6 = st.columns([1.5, 2, 2, 1, 1, 1])
                c1.markdown(f"<div style='{bg_style}'><b>{label}</b></div>" if bg_style else label, unsafe_allow_html=True)
                c2.markdown(f"<div style='{bg_style}'>{ui_p1}</div>" if bg_style else ui_p1, unsafe_allow_html=True)
                c3.markdown(f"<div style='{bg_style}'>{ui_p2}</div>" if bg_style else ui_p2, unsafe_allow_html=True)
                new_saat = c4.text_input("Saat", value=data.get("saat", ""), key=f"t_{cat_name}_{m_id}_{day_name}", label_visibility="collapsed")
                new_kort = c5.text_input("Kort", value=data.get("kort", ""), key=f"c_{cat_name}_{m_id}_{day_name}", label_visibility="collapsed")
                c6.markdown(f"<div style='padding-top: 8px; text-align: center;'>{skor_val}</div>", unsafe_allow_html=True)
                if new_saat != data.get("saat", "") or new_kort != data.get("kort", ""):
                    cat_d['schedule_data'][m_id] = {"saat": new_saat, "kort": new_kort}
            else:
                tr_style = f" style='background-color:#f0f2f6;'" if bg_style else ""
                html_rows += f"<tr{tr_style}><td><b>{label}</b></td><td>{ui_p1}</td><td>{ui_p2}</td><td style='text-align:center;'>{saat_val}</td><td style='text-align:center;'>{kort_val}</td><td style='text-align:center;'>{skor_val}</td></tr>"

        if not st.session_state.admin_mi and html_rows:
            st.markdown(f"""<div class="mobile-table-container"><table width="100%" class="mobile-table">
            <tr><th>Maç Türü</th><th>Oyuncu 1</th><th>Oyuncu 2</th><th>Saat</th><th>Kort</th><th>Skor</th></tr>{html_rows}</table></div>""", unsafe_allow_html=True)

    g_maclar = {
        "1. GÜN": [(f"MR1_{i}", f"AT-R1 (M{i+1})") for i in range(8)],
        "2. GÜN": [(f"MQF_{i}", f"AT-ÇF (M{i+9})") for i in range(4)] + [(f"CR1_{i}", f"FC-R1 (M{i+16})") for i in range(4)] + [(f"CR2_{i}", f"FC-ÇF (M{i+20})") for i in range(4)],
        "3. GÜN": [(f"MSF_{i}", f"AT-YF (M{i+13})") for i in range(2)] + [(f"CR3_{i}", f"FC-YF1 (M{i+24})") for i in range(2)] + [(f"CR4_{i}", f"FC-YF2 (M{i+26})") for i in range(2)] + [("MATCH_7_8", "FC-7/8 (M30)")],
        "4. GÜN": [("FINAL_MAIN", "AT-FİNAL (M15)"), ("FINAL_TESELLI", "FC-3/4 (M28)"), ("MATCH_5_6", "FC-5/6 (M29)")]
    }

    gunler_to_show = ["1. GÜN", "2. GÜN", "3. GÜN", "4. GÜN"] if secilen_gun == "Tüm Günler" else [secilen_gun]
    for g_adi in gunler_to_show: draw_schedule(active_cat, g_maclar[g_adi], g_adi)
            
    if st.session_state.admin_mi:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 Programı Kaydet", use_container_width=True): save_data(); st.rerun()
        if pdf_program_data:
            btn_pdf = generate_pdf(pd.DataFrame(pdf_program_data), f"{active_cat} Programı", [10, 22, 28, 16, 44, 44, 26], ['C', 'C', 'C', 'C', 'L', 'L', 'C'])
            st.download_button("📥 Program PDF İndir", data=btn_pdf, file_name=f"program.pdf", mime="application/pdf")

with tab_siralama:
    st.subheader(f"🇹🇷 {st.session_state.aktif_yas} ({active_cat}) Kesin Sıralama")
    pdf_siralama_data = []
    res = cat_data['res']
    b_state = compute_bracket_state(cat_data)
    
    rankings = [("1.", "FINAL_MAIN", "w"), ("2.", "FINAL_MAIN", "l"), ("3.", "FINAL_TESELLI", "w"), ("4.", "FINAL_TESELLI", "l"), 
                ("5.", "MATCH_5_6", "w"), ("6.", "MATCH_5_6", "l"), ("7.", "MATCH_7_8", "w"), ("8.", "MATCH_7_8", "l")]
    
    html_rankings = "<div style='max-width: 600px; margin: 0 auto;'>"
    
    for rank_idx, (rank, m_id, key) in enumerate(rankings):
        player_name = "Belli Değil"
        display_rank = rank
        
        if m_id in res and "w" in res[m_id]:
            w_name = res[m_id]["w"]
            p1 = b_state.get(m_id, {}).get("p1", "")
            p2 = b_state.get(m_id, {}).get("p2", "")
            
            # --- HAYALET OYUNCU (DOUBLE W/O) SIRALAMA EŞİTLEME ---
            if w_name == "Hepsi WO":
                if key == "l": display_rank = rankings[rank_idx - 1][0] # Kaybedene de Kazananın sırasını ver
                if key == "w": player_name = p1
                elif key == "l": player_name = p2
            else:
                if key == "w": player_name = w_name
                elif key == "l":
                    if w_name == p1 and p2: player_name = p2
                    elif w_name == p2 and p1: player_name = p1
                    else: player_name = res[m_id].get("l", "Belli Değil")
        
        player_name = clean_html_text(player_name)
        if player_name == "Hepsi WO": player_name = "Çift W/O"
        
        pdf_siralama_data.append({"Sıra": display_rank, "Kategori": active_cat, "Oyuncu Adı": player_name})
        bg_color = "#ffffff" if rank_idx % 2 == 0 else "#f8f9fa"
        rank_num = display_rank.replace(".", "")
        html_rankings += f"<div style='display:flex; align-items:center; padding:10px; margin-bottom:6px; background-color:{bg_color}; border:1px solid #e0e0e0; border-radius:8px;'><div style='width:35px; height:35px; background-color:#1f77b4; color:white; font-weight:bold; font-size:16px; border-radius:50%; margin-right:15px; display:flex; justify-content:center; align-items:center;'>{rank_num}</div><div style='font-size:16px; font-weight:500;'>{player_name}</div></div>"
        
    html_rankings += "</div>"
    st.markdown(html_rankings, unsafe_allow_html=True)
        
    if st.session_state.admin_mi and pdf_siralama_data:
        st.divider()
        btn_pdf_sir = generate_pdf(pd.DataFrame(pdf_siralama_data), f"{active_cat} Siralamasi", [15, 30, 145], ['C', 'C', 'L'])
        st.download_button("📥 Sıralamayı PDF Olarak İndir", data=btn_pdf_sir, file_name=f"siralama.pdf", mime="application/pdf")

if st.session_state.admin_mi and tab_dosya:
    with tab_dosya:
        st.subheader("📥 Veri Yönetimi")
        giris_sekli = st.radio("Oyuncu Listesi Yükle:", ["📋 Toplu Yapıştır (Tavsiye Edilen)", "📄 Akıllı PDF (Resimli)"], horizontal=True)
        
        if giris_sekli == "📋 Toplu Yapıştır (Tavsiye Edilen)":
            txt = st.text_area("16 İsmi Alt Alta Yapıştırın:", value="\n".join([clean_html_text(x) for x in cat_data['players']]), height=350)
            if st.button("💾 Kaydet"):
                temiz_isimler = [clean_html_text(n) for n in txt.splitlines() if clean_html_text(n)]
                while len(temiz_isimler) < 16: temiz_isimler.append(f"Oyuncu {len(temiz_isimler)+1}")
                cat_data['players'] = temiz_isimler[:16]; save_data(); st.rerun()

        elif giris_sekli == "📄 Akıllı PDF (Resimli)":
            uploaded_pdf = st.file_uploader("PDF Yükle", type="pdf")
            if uploaded_pdf:
                try:
                    import PyPDF2; raw_text = ""
                    for p in PyPDF2.PdfReader(uploaded_pdf).pages: raw_text += p.extract_text() + "\n"
                    all_names = []
                    for t in [re.sub(r'^(\d+|S\d*|E\d*|WCK?|LL|Q\d*|\[\d+\])\s*', '', l).strip() for l in raw_text.split('\n') if l.strip()]:
                        t = re.sub(r'^(\d+|S\d*|E\d*|WCK?|LL|Q\d*|\[\d+\])\s*', '', t).strip()
                        if re.match(r'^[A-ZÇĞİÖŞÜ][A-ZÇĞİÖŞÜa-zçğıöşü\s\.\']+$', t) and len(t)>4 and not any(b in t.upper() for b in ["KULÜB", "TURNUVA", "TABLO"]):
                            if t not in all_names: all_names.append(t)
                    while len(all_names)<16: all_names.append("")
                    
                    c_pdf, c_list = st.columns([1.6, 1])
                    with c_pdf:
                        try:
                            uploaded_pdf.seek(0); doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
                            st.image(doc.load_page(0).get_pixmap(dpi=200).tobytes("png"), use_container_width=True)
                        except: st.warning("Görsel motoru yüklenemedi.")
                    with c_list:
                        with st.form("pdf_form"):
                            yeni_liste_datalar = []
                            for i in range(16):
                                cs, ci = st.columns([1, 4])
                                yeni_liste_datalar.append((cs.selectbox(f"S{i}", range(1,17), index=i, label_visibility="collapsed"), ci.text_input(f"İ{i}", value=all_names[i] if i<len(all_names) else "", label_visibility="collapsed")))
                            if st.form_submit_button("💾 Kaydet", use_container_width=True):
                                if len(set([x[0] for x in yeni_liste_datalar])) != 16: st.error("Aynı sıra numarasını tekrar kullandınız!")
                                else:
                                    temiz_isimler = [clean_html_text(n) or f"Oyuncu {s}" for s, n in sorted(yeni_liste_datalar, key=lambda x: x[0])]
                                    cat_data['players'] = temiz_isimler[:16]; save_data(); st.rerun()
                except Exception as e: st.error(f"Hata: {e}")

        st.divider()
        c_sv, c_ld = st.columns(2)
        c_sv.download_button(f"📥 Yedek Al", data=json.dumps(st.session_state.data, ensure_ascii=False), file_name=DB_FILE)
        uf = c_ld.file_uploader(f"📤 Geri Yükle", type="json")
        if uf and c_ld.button("Uygula"): st.session_state.data = json.load(uf); save_data(); st.rerun()
