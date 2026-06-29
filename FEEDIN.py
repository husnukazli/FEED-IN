import streamlit as st

# Sayfa ayarları
st.set_page_config(page_title="Etkileşimli Fikstür", layout="wide")
st.title("🎾 16'lı İnteraktif Fikstür ve Teselli Sistemi")

# --- 1. VERİ VE DURUM YÖNETİMİ (STATE) ---
# Oyuncu listesi ve maç sonuçlarının sayfada kalıcı olması için session_state kullanılır.
if 'players' not in st.session_state:
    st.session_state.players = [f"Oyuncu {i}" for i in range(1, 17)]
if 'winners' not in st.session_state:
    st.session_state.winners = {} # Kazananları tutar
if 'scores' not in st.session_state:
    st.session_state.scores = {} # Skorları tutar

# Maç kartını oluşturan ve sonucu döndüren yardımcı fonksiyon
def match_card(match_id, p1, p2, label):
    st.markdown(f"<div style='background-color:#f0f2f6; padding:10px; border-radius:8px; margin-bottom:15px;'>", unsafe_allow_html=True)
    st.markdown(f"**{label}**")
    
    if p1 and p2:
        # Oyuncu seçenekleri
        options = ["Maç Bekleniyor", p1, p2]
        current_winner = st.session_state.winners.get(match_id, "Maç Bekleniyor")
        if current_winner not in options: current_winner = "Maç Bekleniyor"
        
        # Kazanan Seçimi
        winner_choice = st.selectbox("Kazanan:", options, index=options.index(current_winner), key=f"win_{match_id}", label_visibility="collapsed")
        
        # Skor Girişi
        score_val = st.session_state.scores.get(match_id, "")
        new_score = st.text_input("Skor:", value=score_val, key=f"score_{match_id}", placeholder="Örn: 6-2 6-4", label_visibility="collapsed")
        
        # Durumu güncelle
        if winner_choice != "Maç Bekleniyor":
            st.session_state.winners[match_id] = winner_choice
            st.session_state.scores[match_id] = new_score
            loser = p2 if winner_choice == p1 else p1
            st.markdown("</div>", unsafe_allow_html=True)
            return winner_choice, loser
        else:
            if match_id in st.session_state.winners: del st.session_state.winners[match_id]
            st.markdown("</div>", unsafe_allow_html=True)
            return None, None
    else:
        st.write(f"{p1 or '---'} vs {p2 or '---'}")
        st.markdown("</div>", unsafe_allow_html=True)
        return None, None

# --- 2. KULLANICI ARAYÜZÜ (SEKMELER) ---
tab_players, tab_main, tab_cons = st.tabs(["👥 Oyuncular", "🏆 Ana Tablo", "🔄 Teselli Tablosu"])

with tab_players:
    st.subheader("16 Oyuncuyu Girin")
    players_input = st.text_area("Her satıra bir oyuncu gelecek şekilde yazın:", value="\n".join(st.session_state.players), height=350)
    if st.button("Oyuncuları Kaydet ve Fikstürü Güncelle"):
        new_list = [p.strip() for p in players_input.split('\n') if p.strip()]
        if len(new_list) == 16:
            st.session_state.players = new_list
            st.success("Oyuncular başarıyla kaydedildi! Sekmelerden fikstüre geçebilirsiniz.")
        else:
            st.error(f"Tam olarak 16 oyuncu girmelisiniz. Şu an {len(new_list)} oyuncu var.")

p = st.session_state.players

with tab_main:
    col1, col2, col3, col4 = st.columns(4)
    
    # --- ANA TABLO 1. TUR (Son 16) ---
    m_w, m_l = [None]*9, [None]*9
    with col1:
        st.subheader("1. Tur")
        for i in range(1, 9):
            p1, p2 = p[(i-1)*2], p[(i-1)*2+1]
            m_w[i], m_l[i] = match_card(f"M_R1_{i}", p1, p2, f"Maç {i}")
            
    # --- ANA TABLO ÇEYREK FİNAL ---
    qf_w, qf_l = [None]*5, [None]*5
    with col2:
        st.subheader("Çeyrek Final")
        for i in range(1, 5):
            qf_w[i], qf_l[i] = match_card(f"M_QF_{i}", m_w[i*2-1], m_w[i*2], f"Çeyrek Final {i}")

    # --- ANA TABLO YARI FİNAL ---
    sf_w, sf_l = [None]*3, [None]*3
    with col3:
        st.subheader("Yarı Final")
        for i in range(1, 3):
            sf_w[i], sf_l[i] = match_card(f"M_SF_{i}", qf_w[i*2-1], qf_w[i*2], f"Yarı Final {i}")

    # --- ANA TABLO FİNAL ---
    with col4:
        st.subheader("Final")
        champ, _ = match_card("M_F", sf_w[1], sf_w[2], "ŞAMPİYONLUK MAÇI")
        if champ:
            st.success(f"🏆 ŞAMPİYON: {champ}")

with tab_cons:
    col_c1, col_c2, col_c3, col_c4 = st.columns(4)
    
    # --- TESELLİ 1. TUR (Ana Tablo 1. Tur Kaybedenleri Kendi Arasında) ---
    cr1_w, cr1_l = [None]*5, [None]*5
    with col_c1:
        st.subheader("Teselli 1. Tur")
        for i in range(1, 5):
            # Ana tablodan düşen kaybedenler eşleşiyor
            cr1_w[i], cr1_l[i] = match_card(f"C_R1_{i}", m_l[i*2-1], m_l[i*2], f"Teselli Maç {i}")
            
    # --- TESELLİ ÇEYREK FİNAL (Feed-In Mekanizması - TERSTEN SIRALAMA) ---
    cr2_w, cr2_l = [None]*5, [None]*5
    with col_c2:
        st.subheader("Feed-In (Çeyrek Final)")
        st.caption("Ana tablo ÇF kaybedenleri tersten çaprazlanır.")
        # DİKKAT: Ana tablodaki çeyrek final kaybedenleri (qf_l) tersten (4,3,2,1) olarak eşleşiyor.
        cr2_w[1], cr2_l[1] = match_card("C_R2_1", cr1_w[1], qf_l[4], "Feed-In Maç 1")
        cr2_w[2], cr2_l[2] = match_card("C_R2_2", cr1_w[2], qf_l[3], "Feed-In Maç 2")
        cr2_w[3], cr2_l[3] = match_card("C_R2_3", cr1_w[3], qf_l[2], "Feed-In Maç 3")
        cr2_w[4], cr2_l[4] = match_card("C_R2_4", cr1_w[4], qf_l[1], "Feed-In Maç 4")

    # --- TESELLİ YARI FİNAL ---
    csf_w, csf_l = [None]*3, [None]*3
    with col_c3:
        st.subheader("Teselli Yarı Final")
        for i in range(1, 3):
            csf_w[i], csf_l[i] = match_card(f"C_SF_{i}", cr2_w[i*2-1], cr2_w[i*2], f"Teselli YF {i}")

    # --- TESELLİ FİNAL ---
    with col_c4:
        st.subheader("Teselli Finali")
        cons_champ, _ = match_card("C_F", csf_w[1], csf_w[2], "TESELLİ ŞAMPİYONLUĞU")
        if cons_champ:
            st.info(f"🏅 TESELLİ ŞAMPİYONU: {cons_champ}")
