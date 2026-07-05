import streamlit as st
import json
import unicodedata
from fpdf import FPDF

# --- TÜRKÇE KARAKTER DÜZELTİCİ ---
def clean_text(text):
    if not isinstance(text, str): text = str(text)
    normalized = unicodedata.normalize('NFKD', text)
    return normalized.encode('ascii', 'ignore').decode('ascii')

# --- PDF GENERATOR ---
class TournamentPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, clean_text('Turnuva Fikstur Raporu'), 0, 1, 'C')
        self.ln(10)
    
    def draw_match(self, x, y, p1, p2, m_name, score):
        self.set_font('Arial', '', 8)
        self.rect(x, y, 40, 15)
        self.text(x + 2, y + 5, clean_text(f"{m_name}"))
        self.text(x + 2, y + 10, clean_text(f"1: {p1[:10]}"))
        self.text(x + 2, y + 14, clean_text(f"2: {p2[:10]}"))
        self.text(x + 25, y + 10, clean_text(f"{score}"))

def create_tournament_pdf(title, structure_data):
    pdf = TournamentPDF(orientation='L')
    pdf.add_page()
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, clean_text(title), 0, 1, 'C')
    pdf.ln(10)
    pdf.set_font("Arial", size=8)
    for i, match in enumerate(structure_data):
        row = i // 4
        col = i % 4
        pdf.draw_match(10 + (col * 50), 30 + (row * 30), match['p1'], match['p2'], match['label'], match['score'])
    return pdf.output(dest='S')

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
    # Winner highlighting
    winner = cat_data['res'].get(m_id, {}).get('w')
    style1 = "color:green; font-weight:bold;" if name1 == winner else ""
    style2 = "color:green; font-weight:bold;" if name2 == winner else ""
    
    st.markdown(f'<div style="border:1px solid #ccc; padding:5px; border-radius:5px;">'
                f'<span style="{style1}">{name1}</span><br>vs<br><span style="{style2}">{name2}</span></div>', unsafe_allow_html=True)
    
    if p1 and p2:
        current_res = cat_data['res'].get(m_id, {"w": "-", "l": "-"})
        options = ["-", p1, p2]
        idx = options.index(current_res['w']) if current_res['w'] in options else 0
        w_selection = st.selectbox(f"W_{m_id}", options, index=idx, key=f"sel_{active_cat}_{m_id}", label_visibility="collapsed")
        score = st.text_input(f"S_{m_id}", value=cat_data['scores'].get(m_id, ""), key=f"score_{active_cat}_{m_id}", placeholder="Skor")
        cat_data['scores'][m_id] = score
        if w_selection != "-":
            cat_data['res'][m_id] = {"w": w_selection, "l": (p2 if w_selection == p1 else p1)}
    return None, None

# --- UI TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["🏆 Ana Tablo", "🔄 Teselli", "📊 Sıralama", "📅 Maç Programı"])

with tab1:
    st.subheader("Ana Tablo")
    p = cat_data['players']
    cols = st.columns(4)
    # Basit bir döngü ile görselleştirme
    with cols[0]:
        m_r1 = {i: match_card(f"MR1_{i}", p[i*2], p[i*2+1], f"R1-M{i+1}") for i in range(8)}
    with cols[1]:
        m_qf = {i: match_card(f"MQF_{i}", m_r1[i*2][0] if m_r1[i*2] else "...", m_r1[i*2+1][0] if m_r1[i*2+1] else "...", f"ÇF-M{i+1}") for i in range(4)}

with tab2:
    st.subheader("Teselli Tablosu")
    st.write("Teselli işlemleri burada...")

with tab3:
    st.header("Sıralama")
    res = cat_data['res']
    rankings = [("1.", "FINAL_MAIN", "w"), ("2.", "FINAL_MAIN", "l"), ("3.", "FINAL_TESELLI", "w")]
    data_table = [{"Sira": r, "Oyuncu": res[mid][k]} for r, mid, k in rankings if mid in res]
    st.table(data_table)
    
    # PDF Butonu Eklendi
    st.download_button("📄 Sıralama PDF İndir", data=create_tournament_pdf("SIRALAMA", []), file_name="Siralama.pdf", mime="application/pdf")

with tab4:
    st.header("📅 Maç Programı")
    st.write("Düzenleme yapmak için ilgili satırı kullanın:")
    
    # Başlıklar
    c1, c2, c3, c4, c5 = st.columns([2, 2, 1, 1, 1])
    c1.write("**Maç**"); c2.write("**Oyuncular**"); c3.write("**Saat**"); c4.write("**Kort**"); c5.write("**Skor**")
    
    # Örnek Satır (Tüm maçlarınız için bu döngüyü genişletebilirsiniz)
    for i in range(8):
        m_id = f"MR1_{i}"
        row = st.columns([2, 2, 1, 1, 1])
        row[0].write(f"R1-M{i+1}")
        row[1].write(f"{cat_data['players'][i*2]} - {cat_data['players'][i*2+1]}")
        
        # Giriş kutuları
        cat_data['schedule'].setdefault(m_id, {"saat": "", "kort": "", "skor": ""})
        cat_data['schedule'][m_id]['saat'] = row[2].text_input(f"saat_{m_id}", value=cat_data['schedule'][m_id]['saat'], label_visibility="collapsed")
        cat_data['schedule'][m_id]['kort'] = row[3].text_input(f"kort_{m_id}", value=cat_data['schedule'][m_id]['kort'], label_visibility="collapsed")
        cat_data['schedule'][m_id]['skor'] = row[4].text_input(f"skor_{m_id}", value=cat_data['schedule'][m_id]['skor'], label_visibility="collapsed")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Veri")
    if st.button("JSON Kaydet"):
        st.download_button("İndir", data=json.dumps(st.session_state.data), file_name="turnuva.json")
