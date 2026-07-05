import streamlit as st
import json

st.set_page_config(layout="wide", page_title="Consolation Milli Takım Belirleme")
st.title("🎾 Consolation Milli Takım Belirleme")

# --- YARDIMCI FONKSİYONLAR ---
def get_or_create_data():
    if 'data' not in st.session_state:
        st.session_state.data = {
            'Erkekler': {'players': [f"Oyuncu {i}" for i in range(1, 17)], 'res': {}, 'scores': {}, 'schedule_data': {}},
            'Kadınlar': {'players': [f"Oyuncu {i}" for i in range(1, 17)], 'res': {}, 'scores': {}, 'schedule_data': {}}
        }
    return st.session_state.data

# --- DURUM YÖNETİMİ ---
data = get_or_create_data()
active_cat = st.radio("Turnuva Kategorisi Seçiniz:", ["Erkekler", "Kadınlar"], horizontal=True)
cat_data = data[active_cat]

# --- MAÇ KARTI FONKSİYONU ---
def match_card(m_id, p1, p2, label):
    # Ekrana yazdırma ve giriş alma
    st.markdown(f"<small><b>{label}</b></small>", unsafe_allow_html=True)
    
    # Maç verilerini saklamak için benzersiz key'ler
    name1 = p1 if p1 else "..."
    name2 = p2 if p2 else "..."
    
    st.markdown(f"""
        <div style="border: 1px solid #aaa; padding: 5px; border-radius: 5px; margin-bottom: 10px; font-size: 12px; background-color: #f9f9f9;">
            {name1}<br>{name2}
        </div>
    """, unsafe_allow_html=True)
    
    winner, loser = None, None
    if p1 and p2:
        current_res = cat_data['res'].get(m_id, {"w": "-", "l": "-"})
        options = ["-", p1, p2]
        
        # Seçim yapma
        w_selection = st.selectbox(
            f"Kazanan ({m_id})", 
            options, 
            index=options.index(current_res['w']) if current_res['w'] in options else 0,
            key=f"sel_{active_cat}_{m_id}", 
            label_visibility="collapsed"
        )
        
        # Skor girişi
        score = st.text_input(f"Skor ({m_id})", value=cat_data['scores'].get(m_id, ""), key=f"score_{active_cat}_{m_id}", label_visibility="collapsed")
        cat_data['scores'][m_id] = score
        
        if w_selection != "-":
            winner = w_selection
            loser = p2 if winner == p1 else p1
            cat_data['res'][m_id] = {"w": winner, "l": loser}
            return winner, loser
            
    return None, None

# --- ANA ARAYÜZ ---
tab_ana, tab_teselli, tab_siralama, tab_program = st.tabs(["🏆 Ana Tablo", "🔄 Teselli", "📊 Sıralama", "📅 Maç Programı"])

p = cat_data['players']

with tab_ana:
    # (Buradaki çizim mantığın aynı kalabilir, sadece match_card çağrılarını yukarıdaki temizlenmiş yapı destekler)
    # Örnek:
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        m_r1 = {i: match_card(f"MR1_{i}", p[i*2], p[i*2+1], f"R1-M{i+1}") for i in range(8)}
    # ... diğer sütunları benzer şekilde devam ettirebilirsin
    st.info("Diğer sütunları (ÇF, YF, F) aynı mantıkla eklemeye devam et.")

# --- VERİ YÖNETİMİ (Footer) ---
with st.sidebar:
    st.subheader("Dosya İşlemleri")
    data_to_save = json.dumps(st.session_state.data)
    st.download_button("JSON Olarak Kaydet", data=data_to_save, file_name="turnuva_verisi.json")
    uploaded_file = st.file_uploader("JSON Yükle", type="json")
    if uploaded_file and st.button("Veriyi Yükle"):
        st.session_state.data = json.load(uploaded_file)
        st.rerun()
