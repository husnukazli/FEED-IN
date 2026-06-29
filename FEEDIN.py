import streamlit as st

st.set_page_config(page_title="Turnuva Fikstürü", layout="wide")
st.title("🎾 16'lı Etkileşimli Fikstür ve Sıralama Sistemi")

# --- VERİ VE DURUM YÖNETİMİ ---
if 'players' not in st.session_state:
    st.session_state.players = [f"Oyuncu {i}" for i in range(1, 17)]
if 'winners' not in st.session_state:
    st.session_state.winners = {}
if 'scores' not in st.session_state:
    st.session_state.scores = {}

# --- YENİ MAÇ KARTI TASARIMI (Görünürlük Sorunu Çözüldü) ---
def match_card(match_id, p1, p2, label):
    # Kutu tasarımı ve eşleşen oyuncuların net gösterimi
    st.markdown(f"<div style='background-color:#f8f9fa; padding:10px; border-radius:6px; border-left: 5px solid #1f77b4; margin-bottom: 5px;'>", unsafe_allow_html=True)
    st.markdown(f"<span style='font-size:0.85em; color:#6c757d; font-weight:bold;'>{label}</span>", unsafe_allow_html=True)
    
    name1 = p1 if p1 else "⏳ Bekleniyor..."
    name2 = p2 if p2 else "⏳ Bekleniyor..."
    
    # Kimin kiminle oynadığı her zaman görünür olacak
    st.markdown(f"<div style='margin-top:5px; margin-bottom:10px;'><b>1:</b> {name1}<br><b>2:</b> {name2}</div>", unsafe_allow_html=True)
    
    if p1 and p2:
        options = ["Seçim Yapılmadı", p1, p2]
        current_winner = st.session_state.winners.get(match_id, "Seçim Yapılmadı")
        if current_winner not in options: current_winner = "Seçim Yapılmadı"
        
        # Seçim aracı
        winner_choice = st.selectbox("Kazananı Seç:", options, index=options.index(current_winner), key=f"win_{match_id}")
        score_val = st.session_state.scores.get(match_id, "")
        new_score = st.text_input("Maç Skoru:", value=score_val, key=f"score_{match_id}", placeholder="Örn: 6-4 6-2")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        if winner_choice != "Seçim Yapılmadı":
            st.session_state.winners[match_id] = winner_choice
            st.session_state.scores[match_id] = new_score
            loser = p2 if winner_choice == p1 else p1
            return winner_choice, loser
        else:
            if match_id in st.session_state.winners: del st.session_state.winners[match_id]
            return None, None
    else:
        st.markdown("</div>", unsafe_allow_html=True)
        return None, None

# --- SEKMELER ---
tab_players, tab_main, tab_cons = st.tabs(["👥 Oyuncu Listesi", "🏆 Ana Tablo", "🔄 Teselli & Klasman (5.-8.)"])

with tab_players:
    st.subheader("16 Oyuncuyu Sırasıyla Girin")
    st.info("Oyuncuları girdiğiniz sıra, fikstürdeki 1'den 16'ya kadar olan yerleşim sırasını belirler.")
    players_input = st.text_area("Her satıra bir oyuncu gelecek şekilde yazın:", value="\n".join(st.session_state.players), height=350)
    if st.button("Listeyi Kaydet"):
        new_list = [p.strip() for p in players_input.split('\n') if p.strip()]
        if len(new_list) == 16:
            st.session_state.players = new_list
            st.success("Liste kaydedildi! Sekmelerden eşleşmeleri kontrol edebilirsiniz.")
        else:
            st.error(f"Eksik veya fazla oyuncu! Tam olarak 16 isim girmelisiniz. (Şu an: {len(new_list)})")

p = st.session_state.players

with tab_main:
    col1, col2, col3, col4 = st.columns(4)
    
    m_w, m_l = [None]*9, [None]*9
    with col1:
        st.subheader("1. Tur")
        for i in range(1, 9):
            p1, p2 = p[(i-1)*2], p[(i-1)*2+1]
            m_w[i], m_l[i] = match_card(f"M_R1_{i}", p1, p2, f"Maç {i}")
            
    qf_w, qf_l = [None]*5, [None]*5
    with col2:
        st.subheader("Çeyrek Final")
        for i in range(1, 5):
            qf_w[i], qf_l[i] = match_card(f"M_QF_{i}", m_w[i*2-1], m_w[i*2], f"Çeyrek Final {i}")

    sf_w, sf_l = [None]*3, [None]*3
    with col3:
        st.subheader("Yarı Final")
        for i in range(1, 3):
            sf_w[i], sf_l[i] = match_card(f"M_SF_{i}", qf_w[i*2-1], qf_w[i*2], f"Yarı Final {i}")

    with col4:
        st.subheader("Final")
        champ, runner_up = match_card("M_F", sf_w[1], sf_w[2], "ŞAMPİYONLUK MAÇI")
        if champ:
            st.success(f"🏆 1. {champ}\n\n🥈 2. {runner_up}")

with tab_cons:
    col_c1, col_c2, col_c3, col_c4 = st.columns(4)
    
    cr1_w, cr1_l = [None]*5, [None]*5
    with col_c1:
        st.subheader("Teselli 1. Tur")
        st.caption("Ana tablo 1. Tur kaybedenleri")
        for i in range(1, 5):
            cr1_w[i], cr1_l[i] = match_card(f"C_R1_{i}", m_l[i*2-1], m_l[i*2], f"Teselli Maç {i}")
            
    cr2_w, cr2_l = [None]*5, [None]*5
    with col_c2:
        st.subheader("Feed-In Çeyrek Final")
        st.caption("Ana tablo ÇF kaybedenleri (Tersten)")
        # Çapraz eşleşme (Tersten yerleşim)
        cr2_w[1], cr2_l[1] = match_card("C_R2_1", cr1_w[1], qf_l[4], "Feed-In Maç 1")
        cr2_w[2], cr2_l[2] = match_card("C_R2_2", cr1_w[2], qf_l[3], "Feed-In Maç 2")
        cr2_w[3], cr2_l[3] = match_card("C_R2_3", cr1_w[3], qf_l[2], "Feed-In Maç 3")
        cr2_w[4], cr2_l[4] = match_card("C_R2_4", cr1_w[4], qf_l[1], "Feed-In Maç 4")

    csf_w, csf_l = [None]*3, [None]*3
    with col_c3:
        st.subheader("Teselli Yarı Final")
        for i in range(1, 3):
            csf_w[i], csf_l[i] = match_card(f"C_SF_{i}", cr2_w[i*2-1], cr2_w[i*2], f"Teselli YF {i}")

    with col_c4:
        st.subheader("5. - 6.'lık Maçı")
        st.caption("Teselli Finali")
        p5, p6 = match_card("C_F_5_6", csf_w[1], csf_w[2], "5. - 6. Klasman")
        if p5: 
            st.info(f"5️⃣ {p5}\n\n6️⃣ {p6}")

        st.markdown("<hr>", unsafe_allow_html=True)

        st.subheader("7. - 8.'lik Maçı")
        st.caption("Teselli YF Kaybedenleri")
        p7, p8 = match_card("C_F_7_8", csf_l[1], csf_l[2], "7. - 8. Klasman")
        if p7: 
            st.warning(f"7️⃣ {p7}\n\n8️⃣ {p8}")
