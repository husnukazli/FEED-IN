# --- ANA TABLO (YENİ SİMETRİK HİZALAMA) ---
with tab_ana:
    st.subheader(f"👥 {active_cat} - Oyuncu Listesi")
    txt = st.text_area("16 Oyuncu girin:", value="\n".join(p), height=70)
    if st.button("Listeyi Güncelle"):
        cat_data['players'] = [name.strip() for name in txt.splitlines() if name.strip()]
        st.rerun()
    st.divider()
    
    # 4 Sütunlu simetrik yapı
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
    
    # HİZALAMA MATEMATİĞİ:
    # Kart yüksekliği yaklaşık 85px kabul edilmiştir.
    # ÇF'nin YF'nin tam ortasına oturması için yukarıdan boşluk (Offset) ve maç araları (Gap) hesaplandı.
    
    with c1: # 8 Maç (R1) - Offset yok, liste başından başlar
        m_r1 = {i: match_card(f"MR1_{i}", p[i*2], p[i*2+1], f"R1-M{i+1}") for i in range(8)}
    
    with c2: # 4 Maç (ÇF)
        spacer(45) # R1-M1 ve R1-M2'nin ortasına gelmesi için 45px aşağı it
        m_qf = {}
        for i in range(4):
            m_qf[i] = match_card(f"MQF_{i}", m_r1[i*2][0], m_r1[i*2+1][0], f"ÇF-M{i+1}")
            spacer(185) # ÇF maçları arası boşluk
            
    with c3: # 2 Maç (YF)
        spacer(230) # ÇF-M1 ve ÇF-M2'nin ortasına gelmesi için 230px aşağı it
        m_sf = {}
        for i in range(2):
            m_sf[i] = match_card(f"MSF_{i}", m_qf[i*2][0], m_qf[i*2+1][0], f"YF-M{i+1}")
            spacer(560) # YF maçları arası boşluk
            
    with c4: # 1 Maç (Final)
        spacer(505) # YF-M1 ve YF-M2'nin ortasına gelmesi için 505px aşağı it
        res_main = match_card("FINAL_MAIN", m_sf[0][0], m_sf[1][0], "FİNAL")
