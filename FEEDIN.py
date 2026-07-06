import streamlit as st
import json
import os
import pandas as pd
from fpdf import FPDF
import base64
import re

st.set_page_config(layout="wide", page_title="Consolation Milli Takım Belirleme", initial_sidebar_state="expanded")

# ==============================================================================
# 1. DOSYA VE FPDF YARDIMCI FONKSİYONLARI
# ==============================================================================
DB_FILE = "turnuva_db.json"
FONT_YUKLENDI = os.path.exists("arial.ttf")

def to_pdf_text(text):
    if FONT_YUKLENDI: return str(text)
    return str(text).encode('latin-1', 'replace').decode('latin-1')

def generate_pdf(df, baslik):
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
    
    if FONT_YUKLENDI: pdf.set_font("ArialTR", "", 10)
    else: pdf.set_font("Arial", '', 10)

    if not df.empty:
        col_width = 190 / len(df.columns)
        # Sütun başlıkları
        for col in df.columns:
            pdf.cell(col_width, 10, to_pdf_text(col), border=1, align='C')
        pdf.ln()
        
        if FONT_YUKLENDI: pdf.set_font("ArialTR", "", 9)
        else: pdf.set_font("Arial", '', 9)
            
        # Satırlar
        for _, row in df.iterrows():
            for item in row:
                pdf.cell(col_width, 8, to_pdf_text(str(item)), border=1, align='C')
            pdf.ln()
    return bytes(pdf.output())

# ==============================================================================
# 2. VERİ YÖNETİMİ
# ==============================================================================
def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {
        'Erkekler': {'players': [f"Oyuncu {i}" for i in range(1, 17)], 'res': {}, 'scores': {}, 'schedule_data': {}},
        'Kadınlar': {'players': [f"Oyuncu {i}" for i in range(1, 17)], 'res': {}, 'scores': {}, 'schedule_data': {}}
    }

def save_data():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.data, f)

if 'data' not in st.session_state:
    st.session_state.data = load_data()

# ==============================================================================
# 3. ŞİFRELİ GİRİŞ / MİSAFİR MODU (SİDEBAR)
# ==============================================================================
if "admin_mi" not in st.session_state:
    st.session_state.admin_mi = False

with st.sidebar:
    st.markdown("### 👨‍⚖️ Turnuva Yönetimi")
    if not st.session_state.admin_mi:
        st.info("👁️ Şu an **Misafir Modunda** izliyorsunuz.")
        girilen_sifre = st.text_input("Hakem Şifresi:", type="password")
        if st.button("🔒 Giriş Yap"):
            if girilen_sifre == "zonguldak2026": # Şifreyi buradan değiştirebilirsin
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
    active_cat = st.radio("🎾 Kategori:", ["Erkekler", "Kadınlar"])

cat_data = st.session_state.data[active_cat]

# ==============================================================================
# 4. ÖZEL CSS VE SİMETRİ YARDIMCILARI
# ==============================================================================
st.markdown("""
<style>
/* Kart yüksekliğini sabitliyoruz ki simetri kaymasın */
.match-wrapper { height: 105px; margin-bottom: 5px; }
.match-card {
    border: 1px solid #1f77b4; border-radius: 6px; padding: 6px; 
    background-color: #f8f9fa; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); height: 100%;
}
.match-label { font-size: 11px; font-weight: bold; color: #1f77b4; border-bottom: 1px solid #ddd; margin-bottom: 4px; padding-bottom: 2px; }
.player-name { font-size: 13px; font-weight: 500; color: #333; padding: 2px 0; overflow: hidden; white-space: nowrap; text-overflow: ellipsis;}
.player-separator { border-top: 1px dashed #ccc; margin: 2px 0; }
</style>
""", unsafe_allow_html=True)

def spacer(height_px):
    st.markdown(f'<div style="height:{height_px}px;"></div>', unsafe_allow_html=True)

# Simetri için Matematiksel Boşluklar (1 Kart = ~110px)
# R1: 0, R2: 55, R3: 165, Final: 385
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
            st.markdown(f"<div style='text-align:center; font-size:12px; color:green; margin-top:-5px;'><b>K:</b> {current_winner} <br> {current_score}</div>", unsafe_allow_html=True)
        return current_winner if current_winner != "-" else None, p2 if current_winner == p1 else (p1 if current_winner == p2 else None)
    
    # Admin Skor Girişi
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
# TAB 1: ANA TABLO (Mükemmel Simetri)
# ==========================================
with tab_ana:
    c_pdf, _ = st.columns([1, 3])
    if c_pdf.button("📄 Ana Tabloyu PDF İndir (Liste)", key="pdf_main"):
        # FPDF Tablo Verisi Hazırlama
        pdf_data = []
        for m_id, label in [(f"MR1_{i}", f"Son 16 M{i+1}") for i in range(8)] + [(f"MQF_{i}", f"Çeyrek Final M{i+1}") for i in range(4)] + [(f"MSF_{i}", f"Yarı Final M{i+1}") for i in range(2)] + [("FINAL_MAIN", "FİNAL")]:
            p1, p2 = st.session_state.get(f"match_players_{active_cat}_{m_id}", ("-", "-"))
            w = cat_data['res'].get(m_id, {}).get("w", "Oynanmadı")
            s = cat_data['scores'].get(m_id, "-")
            pdf_data.append({"Tur": label, "Oyuncu 1": p1, "Oyuncu 2": p2, "Skor": s, "Kazanan": w})
        
        pdf_bytes = generate_pdf(pd.DataFrame(pdf_data), f"{active_cat} Ana Tablo Fikstürü")
        st.download_button("📥 PDF İndir", data=pdf_bytes, file_name=f"{active_cat}_Anatablo.pdf", mime="application/pdf")

    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    m_r1, m_qf, m_sf = {}, {}, {}
    
    with c1: 
        st.markdown("<h5 style='text-align: center;'>Son 16</h5>", unsafe_allow_html=True)
        for i in range(4): m_r1[i] = match_card(f"MR1_{i}", p[i*2], p[i*2+1], f"R1-M{i+1}")
        spacer(60) # Merkez Eksen Boşluğu
        for i in range(4, 8): m_r1[i] = match_card(f"MR1_{i}", p[i*2], p[i*2+1], f"R1-M{i+1}")
            
    with c2: 
        st.markdown("<h5 style='text-align: center;'>Çeyrek Final</h5>", unsafe_allow_html=True)
        spacer(S_R2_TOP)
        m_qf[0] = match_card(f"MQF_0", m_r1[0][0], m_r1[1][0], "ÇF-M1")
        spacer(S_R2_GAP)
        m_qf[1] = match_card(f"MQF_1", m_r1[2][0], m_r1[3][0], "ÇF-M2")
        spacer(S_R2_GAP + 60) # Eksen geçişi
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
    c_pdf2, _ = st.columns([1, 3])
    if c_pdf2.button("📄 Teselli Tablosunu PDF İndir", key="pdf_teselli"):
        pdf_data2 = []
        for m_id, label in [(f"CR1_{i}", f"T-Son16 M{i+1}") for i in range(4)] + [(f"CR2_{i}", f"T-ÇF M{i+1}") for i in range(4)] + [("FINAL_TESELLI", "Teselli Finali"), ("MATCH_5_6", "5. ve 6. Maçı"), ("MATCH_7_8", "7. ve 8. Maçı")]:
            p1, p2 = st.session_state.get(f"match_players_{active_cat}_{m_id}", ("-", "-"))
            w = cat_data['res'].get(m_id, {}).get("w", "Oynanmadı")
            pdf_data2.append({"Tur": label, "Oyuncu 1": p1, "Oyuncu 2": p2, "Kazanan": w})
        st.download_button("📥 PDF İndir", data=generate_pdf(pd.DataFrame(pdf_data2), f"{active_cat} Teselli Fikstürü"), file_name=f"{active_cat}_Teselli.pdf", mime="application/pdf")

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
# TAB 3: PROGRAM VE SIRALAMA
# ==========================================
with tab_program:
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.subheader("📅 Maç Programı")
        df_program_data = []
        
        # Sadece günlere ayrılmış maç verilerini çekiyoruz
        gun1 = [(f"MR1_{i}", f"R1 M{i+1}") for i in range(8)] + [(f"CR1_{i}", f"T-R1 M{i+1}") for i in range(4)]
        gun2 = [(f"MQF_{i}", f"ÇF M{i+1}") for i in range(4)] + [(f"CR2_{i}", f"T-ÇF M{i+1}") for i in range(4)] + [(f"MSF_{i}", f"YF M{i+1}") for i in range(2)] + [("MATCH_7_8", "7.-8.'lik")]
        gun3 = [("FINAL_MAIN", "FİNAL"), ("FINAL_TESELLI", "3.-4.'lük"), ("MATCH_5_6", "5.-6.'lık")]
        
        for idx, (gun_adi, maclar) in enumerate([("1. GÜN", gun1), ("2. GÜN", gun2), ("3. GÜN", gun3)]):
            st.markdown(f"**🗓️ {gun_adi}**")
            for m_id, label in maclar:
                p1, p2 = st.session_state.get(f"match_players_{active_cat}_{m_id}", ("-", "-"))
                if p1 != "-" and p2 != "-":
                    skor = cat_data['scores'].get(m_id, "")
                    df_program_data.append({"Gün": gun_adi, "Tur": label, "Oyuncu 1": p1, "Oyuncu 2": p2, "Skor": skor})
                    st.write(f"▪️ {label}: {p1} - {p2} *(Skor: {skor if skor else 'Oynanmadı'})*")
        
        if st.button("📄 Programı PDF İndir"):
            pdf_bytes_prog = generate_pdf(pd.DataFrame(df_program_data), f"{active_cat} Maç Programı")
            st.download_button("📥 İndir", data=pdf_bytes_prog, file_name="Mac_Programi.pdf", mime="application/pdf")

    with col_p2:
        st.subheader("🇹🇷 Milli Takım Sıralaması")
        res = cat_data['res']
        rankings = [("1.", "FINAL_MAIN", "w"), ("2.", "FINAL_MAIN", "l"), ("3.", "FINAL_TESELLI", "w"), ("4.", "FINAL_TESELLI", "l"), 
                    ("5.", "MATCH_5_6", "w"), ("6.", "MATCH_5_6", "l"), ("7.", "MATCH_7_8", "w"), ("8.", "MATCH_7_8", "l")]
        
        siralama_data = []
        for rank, m_id, key in rankings:
            player_name = res[m_id][key] if m_id in res and key in res[m_id] else "Belli Değil"
            siralama_data.append({"Sıra": rank, "Oyuncu Adı": player_name})
            st.markdown(f"**{rank}** {player_name}")
            
        if st.button("📄 Sıralamayı PDF İndir"):
            pdf_bytes_sir = generate_pdf(pd.DataFrame(siralama_data), f"{active_cat} Sıralama Listesi")
            st.download_button("📥 İndir", data=pdf_bytes_sir, file_name="Siralama.pdf", mime="application/pdf")

# ==========================================
# TAB 4: YEDEKLEME VE DOSYA (Sadece Admin)
# ==========================================
with tab_dosya:
    if st.session_state.admin_mi:
        st.subheader("📥 Yedekleme ve Oyuncu Listesi")
        
        st.markdown("**1. Esame Listesini Güncelle**")
        txt = st.text_area(f"{active_cat} 16 Oyuncu girin (1. Seribaşı en üstte):", value="\n".join(p), height=150)
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
