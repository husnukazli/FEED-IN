import streamlit as st
import json
from fpdf import FPDF

# --- SAYFA AYARLARI ---
st.set_page_config(layout="wide", page_title="Tenis Turnuva Yönetim Sistemi")
st.title("🎾 Tenis Turnuva Yönetim Sistemi")

# --- CSS ---
st.markdown("""
    <style>
    .match-box { border: 1px solid #aaa; padding: 5px; border-radius: 5px; margin-bottom: 10px; font-size: 11px; background-color: #f9f9f9; text-align: center; }
    .stTextInput > label { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# --- PDF GENERATOR CLASS ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Turnuva Raporu', 0, 1, 'C')
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Sayfa {self.page_no()}', 0, 0, 'C')

def generate_pdf_bytes(title, data_dict):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.ln(10)
    for k, v in data_dict.items():
        pdf.cell(200, 10, txt=f"{k}: {v}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- VERİ BAŞLATMA ---
if 'data' not in st.session_state:
    st.session_state.data = {
        'Erkekler': {'players': [f"Oyuncu {i}" for i in range(1, 17)], 'res': {}, 'scores': {}, 'schedule': {}},
        'Kadınlar': {'players': [f"Oyuncu {i}" for i in range(1, 17)], 'res': {}, 'scores': {}, 'schedule': {}}
    }

active_cat = st.radio("Kategori:", ["Erkekler", "Kadınlar"], horizontal=True)
cat_data = st.session_state.data[active_cat]

# --- MAÇ KARTI ---
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

# --- PDF WIDGET ---
def pdf_export(title, data):
    if st.download_button(f"📄 {title} PDF İndir", data=generate_pdf_bytes(title, data), file_name=f"{title}.pdf"):
        st.success("PDF Hazır!")

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["🏆 Ana Tablo", "🔄 Teselli", "📊 Sıralama", "📅 Maç Programı"])

with tab1:
    st.subheader("Ana Tablo")
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
    pdf_export("Ana_Tablo", cat_data['res'])

with tab2:
    st.subheader("Teselli Tablosu")
    c1, c2, c3, c4 = st.columns(4)
    # R1 Teselli
    with c1: c_r1 = {i: match_card(f"CR1_{i}", m_r1[i*2][1], m_r1[i*2+1][1], f"T-R1 M{i+1}") for i in range(4)}
    # R2 Teselli
    with c2:
        qf_losers = [m_qf[3][1], m_qf[2][1], m_qf[1][1], m_qf[0][1]]
        c_r2 = {i: match_card(f"CR2_{i}", c_r1[i][0], qf_losers[i], f"T-R2 M{i+1}") for i in range(4)}
    # R3 Teselli
    with c3:
        c_r3 = {i: match_card(f"CR3_{i}", c_r2[i*2][0], c_r2[i*2+1][0], f"T-R3 M{i+1}") for i in range(2)}
        m_78 = match_card("MATCH_7_8", c_r3[0][1], c_r3[1][1], "7.-8.'lik Maçı")
    # Final Teselli
    with c4:
        c_r4 = {i: match_card(f"CR4_{i}", c_r3[i][0], m_sf[i][1], f"T-YF M{i+1}") for i in range(2)}
        m_tes_f = match_card("FINAL_TESELLI", c_r4[0][0], c_r4[1][0], "Teselli Finali")
        m_56 = match_card("MATCH_5_6", c_r4[0][1], c_r4[1][1], "5.-6.'lık Maçı")
    pdf_export("Teselli_Tablosu", cat_data['res'])

with tab3:
    st.header("Sıralama")
    res = cat_data['res']
    rankings = [("1.", "FINAL_MAIN", "w"), ("2.", "FINAL_MAIN", "l"), ("3.", "FINAL_TESELLI", "w"), ("4.", "FINAL_TESELLI", "l"), ("5.", "MATCH_5_6", "w"), ("6.", "MATCH_5_6", "l"), ("7.", "MATCH_7_8", "w"), ("8.", "MATCH_7_8", "l")]
    for r, mid, k in rankings:
        if mid in res: st.write(f"{r} {res[mid][k]}")
    pdf_export("Siralama", res)

with tab4:
    st.header("📅 Maç Programı")
    st_ana, st_tes = st.tabs(["Ana Tablo Maçları", "Teselli Maçları"])
    
    def render_prog(matches):
        h1, h2, h3, h4 = st.columns([2, 2, 2, 2])
        h1.write("**Maç**"); h2.write("**Oyuncu 1**"); h3.write("**Oyuncu 2**"); h4.write("**Detay (Saat/Kort/Skor)**")
        for mid, lbl in matches:
            c1, c2, c3, c4 = st.columns([2, 2, 2, 2])
            c1.write(lbl)
            p1_val, p2_val = st.session_state.get(f"match_players_{active_cat}_{mid}", ("?", "?"))
            c2.write(str(p1_val)); c3.write(str(p2_val))
            c4.text_input("Detay", key=f"prog_{active_cat}_{mid}", label_visibility="collapsed")
            
    with st_ana:
        render_prog([("MR1_0", "R1-M1"), ("MR1_1", "R1-M2"), ("MR1_2", "R1-M3"), ("MR1_3", "R1-M4"), ("MR1_4", "R1-M5"), ("MR1_5", "R1-M6"), ("MR1_6", "R1-M7"), ("MR1_7", "R1-M8"), ("MQF_0", "ÇF-M1"), ("MQF_1", "ÇF-M2"), ("MQF_2", "ÇF-M3"), ("MQF_3", "ÇF-M4"), ("MSF_0", "YF-M1"), ("MSF_1", "YF-M2"), ("FINAL_MAIN", "FİNAL")])
    with st_tes:
        render_prog([("CR1_0", "T-R1 M1"), ("CR1_1", "T-R1 M2"), ("CR1_2", "T-R1 M3"), ("CR1_3", "T-R1 M4"), ("CR2_0", "T-R2 M1"), ("CR2_1", "T-R2 M2"), ("CR2_2", "T-R2 M3"), ("CR2_3", "T-R2 M4"), ("CR3_0", "T-R3 M1"), ("CR3_1", "T-R3 M2"), ("MATCH_7_8", "7.-8.'lik"), ("CR4_0", "T-YF M1"), ("CR4_1", "T-YF M2"), ("FINAL_TESELLI", "Teselli Finali"), ("MATCH_5_6", "5.-6.'lık")])
    pdf_export("Mac_Programi", {"Program": "Detaylar dolu"})

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Veri Yönetimi")
    st.download_button("JSON Kaydet", data=json.dumps(st.session_state.data), file_name="turnuva.json")
    uploaded = st.file_uploader("JSON Yükle", type="json")
    if uploaded and st.button("Uygula"):
        st.session_state.data = json.load(uploaded)
        st.rerun()
