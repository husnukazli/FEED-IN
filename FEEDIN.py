import streamlit as st

import json



st.set_page_config(layout="wide", page_title="Consolation Milli Takım Belirleme")

st.title("🎾 Consolation Milli Takım Belirleme")



# --- YARDIMCI FONKSİYONLAR ---

def spacer(height_px):

    st.markdown(f'<div style="height:{height_px}px;"></div>', unsafe_allow_html=True)



# --- KATEGORİ VE DURUM YÖNETİMİ ---

if 'data' not in st.session_state:

    st.session_state.data = {

        'Erkekler': {'players': [f"Oyuncu {i}" for i in range(1, 17)], 'res': {}, 'scores': {}, 'schedule_data': {}},

        'Kadınlar': {'players': [f"Oyuncu {i}" for i in range(1, 17)], 'res': {}, 'scores': {}, 'schedule_data': {}}

    }



active_cat = st.radio("Turnuva Kategorisi Seçiniz:", ["Erkekler", "Kadınlar"], horizontal=True)

cat_data = st.session_state.data[active_cat]



# --- VERİ YÖNETİMİ ---

with st.expander("⚙️ Veri Yönetimi"):

    col_save, col_load = st.columns(2)

    data_to_save = json.dumps(st.session_state.data)

    col_save.download_button("Tüm Veriyi Kaydet (JSON)", data=data_to_save, file_name="tum_turnuva_verisi.json")

    uploaded_file = col_load.file_uploader("Dosyayı Geri Yükle", type="json")

    if uploaded_file is not None and col_load.button("Yüklenen Veriyi Uygula"):

        st.session_state.data = json.load(uploaded_file)

        st.rerun()



# --- MAÇ KARTI FONKSİYONU ---

def match_card(m_id, p1, p2, label):

    st.session_state[f"match_players_{active_cat}_{m_id}"] = (p1, p2)

    st.markdown(f"<small><b>{label}</b></small>", unsafe_allow_html=True)

    name1 = p1 if p1 else "..."

    name2 = p2 if p2 else "..."

    st.markdown(f"""<div style="border: 1px solid #aaa; padding: 2px; border-radius: 3px; margin-bottom: 5px; font-size: 11px; background-color: #f9f9f9;">{name1}<br>{name2}</div>""", unsafe_allow_html=True)

    

    if p1 and p2:

        current_winner = cat_data['res'].get(m_id, {}).get("w", "-")

        options = ["-", p1, p2]

        idx = options.index(current_winner) if current_winner in options else 0

        winner = st.selectbox(f"W ({m_id})", options, index=idx, key=f"sel_{active_cat}_{m_id}", label_visibility="collapsed")

        score = st.text_input(f"Skor ({m_id})", value=cat_data['scores'].get(m_id, ""), key=f"score_{active_cat}_{m_id}", label_visibility="collapsed")

        cat_data['scores'][m_id] = score

        if winner != "-":

            loser = p2 if winner == p1 else p1

            cat_data['res'][m_id] = {"w": winner, "l": loser}

            return winner, loser

    return None, None



# --- TAB'LAR ---

tab_ana, tab_teselli, tab_siralama, tab_program = st.tabs(["🏆 Ana Tablo", "🔄 Teselli", "📊 Sıralama", "📅 Maç Programı"])



p = cat_data['players']



# --- ANA TABLO (SİMETRİK PİRAMİT) ---

with tab_ana:

    st.subheader(f"👥 {active_cat} - Oyuncu Listesi")

    txt = st.text_area("16 Oyuncu girin:", value="\n".join(p), height=70)

    if st.button("Listeyi Güncelle"):

        cat_data['players'] = [name.strip() for name in txt.splitlines() if name.strip()]

        st.rerun()

    st.divider()

    

    c1, c2, c3, c4 = st.columns([1, 1, 1, 1])

    

    with c1: # 8 Maç (R1)

        m_r1 = {i: match_card(f"MR1_{i}", p[i*2], p[i*2+1], f"R1-M{i+1}") for i in range(8)}

    

    with c2: # 4 Maç (ÇF)

        spacer(45) 

        m_qf = {}

        for i in range(4):

            m_qf[i] = match_card(f"MQF_{i}", m_r1[i*2][0], m_r1[i*2+1][0], f"ÇF-M{i+1}")

            spacer(185) 

            

    with c3: # 2 Maç (YF)

        spacer(230)

        m_sf = {}

        for i in range(2):

            m_sf[i] = match_card(f"MSF_{i}", m_qf[i*2][0], m_qf[i*2+1][0], f"YF-M{i+1}")

            spacer(560)

            

    with c4: # 1 Maç (FİNAL)

        spacer(505)

        res_main = match_card("FINAL_MAIN", m_sf[0][0], m_sf[1][0], "FİNAL")



# --- TESELLİ ---

with tab_teselli:

    c_col1, c_col2, c_col3, c_col4 = st.columns(4)

    with c_col1: c_r1 = {i: match_card(f"CR1_{i}", m_r1[i*2][1], m_r1[i*2+1][1], f"T-R1 M{i+1}") for i in range(4)}

    with c_col2:

        qf_losers_reversed = [m_qf[3][1], m_qf[2][1], m_qf[1][1], m_qf[0][1]]

        c_r2 = {i: match_card(f"CR2_{i}", c_r1[i][0], qf_losers_reversed[i], f"T-R2 M{i+1}") for i in range(4)}

    with c_col3:

        c_r3 = {i: match_card(f"CR3_{i}", c_r2[i*2][0], c_r2[i*2+1][0], f"T-R3 M{i+1}") for i in range(2)}

        res_78 = match_card("MATCH_7_8", c_r3[0][1], c_r3[1][1], "7.-8.'lik Maçı")

    with c_col4:

        c_r4 = {i: match_card(f"CR4_{i}", c_r3[i][0], m_sf[i][1], f"T-YF M{i+1}") for i in range(2)}

        res_final_teselli = match_card("FINAL_TESELLI", c_r4[0][0], c_r4[1][0], "Teselli Finali")

        res_56 = match_card("MATCH_5_6", c_r4[0][1], c_r4[1][1], "5.-6.'lık Maçı")



# --- SIRALAMA ---

with tab_siralama:

    st.header("Milli Takım Belirleme Sıralaması")

    res = cat_data['res']

    rankings = [("1.", "FINAL_MAIN", "w"), ("2.", "FINAL_MAIN", "l"), ("3.", "FINAL_TESELLI", "w"), ("4.", "FINAL_TESELLI", "l"), ("5.", "MATCH_5_6", "w"), ("6.", "MATCH_5_6", "l"), ("7.", "MATCH_7_8", "w"), ("8.", "MATCH_7_8", "l")]

    for rank, m_id, key in rankings:

        if m_id in res: st.write(f"{rank} {res[m_id][key]}")



# --- MAÇ PROGRAMI ---

with tab_program:

    st.header("📅 Ortak Maç Programı")

    secilen_gun = st.radio("🗓️ Görüntülemek İstediğiniz Günü Seçin:", ["Tüm Günler", "1. GÜN", "2. GÜN", "3. GÜN"], horizontal=True)

    st.divider()



    for cat in ['Erkekler', 'Kadınlar']:

        st.subheader(f"--- {cat} Turnuvası ---")

        def edit_day_schedule(matches, day_name):

            if secilen_gun in ["Tüm Günler", day_name]:

                st.markdown(f"#### 🗓️ {day_name}")

                h1, h2, h3, h4, h5, h6 = st.columns([1.5, 2, 2, 1, 1, 1])

                h1.markdown("**Maç**"); h2.markdown("**Oyuncu 1**"); h3.markdown("**Oyuncu 2**"); h4.markdown("**Maç Saati**"); h5.markdown("**Kort**"); h6.markdown("**Skor**")

                st.markdown("<div style='margin-top:-10px; margin-bottom:10px; border-bottom:1px solid #ddd;'></div>", unsafe_allow_html=True)

                for m_id, label in matches:

                    p1, p2 = st.session_state.get(f"match_players_{cat}_{m_id}", ("⏳", "⏳"))

                    winner = st.session_state.data[cat]['res'].get(m_id, {}).get("w", None)

                    p1_display = f"🏆 **{p1}**" if winner and p1 == winner else p1

                    p2_display = f"🏆 **{p2}**" if winner and p2 == winner else p2

                    data = st.session_state.data[cat]['schedule_data'].get(m_id, {"saat": "", "kort": "", "skor": ""})

                    c1, c2, c3, c4, c5, c6 = st.columns([1.5, 2, 2, 1, 1, 1])

                    c1.write(label); c2.write(p1_display); c3.write(p2_display)

                    new_saat = c4.text_input("Saat", value=data.get("saat", ""), key=f"time_{cat}_{m_id}", label_visibility="collapsed")

                    new_kort = c5.text_input("Kort", value=data.get("kort", ""), key=f"court_{cat}_{m_id}", label_visibility="collapsed")

                    new_skor = c6.text_input("Skor", value=data.get("skor", ""), key=f"prog_score_{cat}_{m_id}", label_visibility="collapsed")

                    st.session_state.data[cat]['schedule_data'][m_id] = {"saat": new_saat, "kort": new_kort, "skor": new_skor}

        

        edit_day_schedule([(f"CR1_{i}", f"T-R1 M{i+1}") for i in range(4)] + [(f"CR2_{i}", f"T-R2 M{i+1}") for i in range(4)], "1. GÜN")

        edit_day_schedule([(f"CR3_{i}", f"T-R3 M{i+1}") for i in range(2)] + [("MATCH_7_8", "7.-8.'lik Maçı")] + [(f"CR4_{i}", f"T-YF M{i+1}") for i in range(2)], "2. GÜN")

        edit_day_schedule([("FINAL_TESELLI", "Teselli Finali"), ("MATCH_5_6", "5.-6.'lık Maçı")], "3. GÜN") 

