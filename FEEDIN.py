import streamlit as st
import json
from fpdf import FPDF

# --- SAYFA AYARLARI ---
st.set_page_config(layout="wide", page_title="Tenis Turnuva Yönetim Sistemi")
st.title("🎾 Profesyonel Tenis Turnuva Yönetim Sistemi")

# --- CSS ---
st.markdown("""
    <style>
    .match-box { border: 1px solid #333; padding: 10px; border-radius: 5px; margin-bottom: 5px; font-size: 12px; background-color: #ffffff; text-align: center; width: 100%; }
    </style>
""", unsafe_allow_html=True)

# --- PDF GENERATOR (GELİŞMİŞ) ---
class TournamentPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Turnuva Fikstür ve Maç Programı', 0, 1, 'C')
        self.ln(10)
    
    def draw_match(self, x, y, p1, p2, m_name, score):
        self.set_font('Arial', '', 8)
        self.rect(x, y, 40, 15)
        self.text(x + 2, y + 5, f"{m_name}")
        self.text(x + 2, y + 10, f"1: {p1[:10]}")
        self.text(x + 2, y + 14, f"2: {p2[:10]}")
        self.text(x + 25, y + 10, f"{score}")

def create_tournament_pdf(title, structure_data):
    pdf = TournamentPDF(orientation='L') # Landscape
    pdf.add_page()
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, title, 0, 1, 'C')
    
    # Basit bir şematik çizim (X, Y koordinatları ile)
    pdf.set_font("Arial", size=10)
    # Burada Round 1'den Finale kadar olan maçları bir grid içine çiziyoruz
    pdf.cell(0, 10, "Turnuva Agaci (Ozet):", 0, 1)
    
    # Basit bir örnek yerleşim (Kullanıcı verisine göre dinamikleştirilebilir)
    pdf.set_font("Arial", size=8)
    for i, match in enumerate(structure_data):
        row = i // 4
        col = i % 4
        pdf.draw_match(10 + (col * 50), 30 + (row * 30), match['p1'], match['p2'], match['label'], match['score'])
        
    return bytes(pdf.output())

# --- VERİ YÖNETİMİ ---
if 'data' not in st.session_state:
    st.session_state.data = {
        'Erkekler': {'players': [f"Oyuncu {i}" for i in range(1, 17)], 'res': {}, 'scores': {}, 'schedule': {}},
        'Kadınlar': {'players': [f"Oyuncu {i}" for i in range(1, 17)], 'res': {}, 'scores': {}, 'schedule': {}}
    }

active_cat = st.radio("Kategori:", ["Erkekler", "Kadınlar"], horizontal=True)
cat_data = st.session_state.data[active_cat]

# --- MAÇ KARTI FONKSİYONU ---
def match_card(m_id, p1, p2, label):
    st.markdown(f"**{label}**")
    name1 = p1 if p1 else "..."
    name2 = p2 if p2 else "..."
    st.markdown(f'<div class="match-box">{name1}<br>vs<br>{name2}</div>', unsafe_allow_html=True)
    
    winner, loser = None, None
    if p1 and p2:
        current_res = cat_data['res'].get(m_id, {"w": "-", "l": "-"})
        options = ["-", p1, p2]
        idx = options.index(current_res['w']) if current_res['w'] in options else 0
        w_selection = st.selectbox(f"W_{m_id}", options, index=idx, key=f"sel_{active_cat}_{m_id}", label_visibility="collapsed")
        score = st.text_input(f"S_{m_id}", value=cat_data['scores'].get(m_id, ""), key=f"score_{active_cat}_{m_id}", placeholder="Skor")
        cat_data['scores'][m_id] = score
        
        if w_selection != "-":
            winner = w_selection
            loser = p2 if winner == p1 else p1
            cat_data['res'][m_id] = {"w": winner, "l": loser}
            return winner, loser
    return None, None

# --- UI TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["🏆 Ana Tablo", "🔄 Teselli", "📊 Sıralama", "📅 Maç Programı"])

with tab1:
    st.subheader("Ana Tablo Fikstürü")
    p = cat_data['players']
    c1, c2, c3, c4 = st.columns(4)
    # R1
    with c1: m_r1 = {i: match_card(f"MR1_{i}", p[i*2], p[i*2+1], f"R1-M{i+1}") for i in range(8)}
    # ÇF
    with c2: m_qf = {i: match_card(f"MQF_{i}", m_r1[i*2][0], m_r1[i*2+1][0], f"ÇF-M{i+1}") for i in range(4)}
    # YF
    with c3: m_sf = {i: match_card(f"MSF_{i}", m_qf[i*2][0], m_qf[i*2+1][0], f"YF-M{i+1}") for i in range(2)}
    # F
    with c4: m_f = match_card("FINAL_MAIN", m_sf[0][0], m_sf[1][0], "FİNAL")
    
    # PDF EXPORT
    st.divider()
    if st.button("📄 Ana Tablo PDF Hazırla"):
        # Veriyi PDF yapısına çevir
        struct = [{"label": f"R1-M{i+1}", "p1": p[i*2], "p2": p[i*2+1], "score": cat_data['scores'].get(f"MR1_{i}", "")} for i in range(8)]
        st.download_button("PDF İndir", data=create_tournament_pdf("ANA TABLO", struct), file_name="Ana_Tablo.pdf", mime="application/pdf")

with tab2:
    st.subheader("Teselli Tablosu Fikstürü")
    c1, c2, c3, c4 = st.columns(4)
    with c1: c_r1 = {i: match_card(f"CR1_{i}", m_r1[i*2][1], m_r1[i*2+1][1], f"T-R1 M{i+1}") for i in range(4)}
    with c2:
        qf_losers = [m_qf[3][1], m_qf[2][1], m_qf[1][1], m_qf[0][1]]
        c_r2 = {i: match_card(f"CR2_{i}", c_r1[i][0], qf_losers[i], f"T-R2 M{i+1}") for i in range(4)}
    with c3:
        c_r3 = {i: match_card(f"CR3_{i}", c_r2[i*2][0], c_r2[i*2+1][0], f"T-R3 M{i+1}") for i in range(2)}
    with c4:
        c_r4 = {i: match_card(f"CR4_{i}", c_r3[i][0], m_sf[i][1], f"T-YF M{i+1}") for i in range(2)}
    
    if st.button("📄 Teselli Tablosu PDF Hazırla"):
        struct = [{"label": f"T-R1-M{i+1}", "p1": "...", "p2": "...", "score": ""} for i in range(4)]
        st.download_button("PDF İndir", data=create_tournament_pdf("TESELLI TABLOSU", struct), file_name="Teselli_Tablosu.pdf", mime="application/pdf")

with tab3:
    st.header("Sıralama Tablosu")
    res = cat_data['res']
    rankings = [("1.", "FINAL_MAIN", "w"), ("2.", "FINAL_MAIN", "l"), ("3.", "FINAL_TESELLI", "w"), ("4.", "FINAL_TESELLI", "l"), ("5.", "MATCH_5_6", "w"), ("6.", "MATCH_5_6", "l"), ("7.", "MATCH_7_8", "w"), ("8.", "MATCH_7_8", "l")]
    
    # Tablo olarak göster
    data_table = []
    for r, mid, k in rankings:
        if mid in res: data_table.append({"Sıra": r, "Oyuncu": res[mid][k]})
    st.table(data_table)

with tab4:
    st.header("📅 Maç Programı")
    # Tablo olarak göster
    prog_data = []
    # Tüm maçları döngüye alıp ekle (Örnek: Sadece R1)
    for i in range(8):
        prog_data.append({"Maç": f"R1-M{i+1}", "Durum": "Planlandı"})
    st.table(prog_data)

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Veri Yönetimi")
    st.download_button("JSON Kaydet", data=json.dumps(st.session_state.data), file_name="turnuva.json")
    uploaded = st.file_uploader("JSON Yükle", type="json")
    if uploaded and st.button("Uygula"):
        st.session_state.data = json.load(uploaded)
        st.rerun()
