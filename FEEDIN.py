import streamlit as st
import graphviz

st.set_page_config(layout="wide", page_title="Fikstür Simülasyonu")

st.title("🎾 16'lı Ana Tablo ve Feed-In Teselli Fikstürü")
st.markdown("""
Bu şema, **16 oyunculu Ana Tablo** ve kaybedenlerin dahil olduğu **Teselli (Consolation)** ağacını göstermektedir.
* **Mavi Oklar:** Maçı kazanan oyuncunun bir sonraki tura ilerleyişini gösterir.
* **Kırmızı Kesik Oklar:** Maçı kaybeden oyuncunun teselli tablosuna (Feed-In) geçişini gösterir.
""")

def draw_fixture():
    # Graphviz nesnesi oluştur (Soldan sağa doğru akış)
    dot = graphviz.Digraph(node_attr={'shape': 'box', 'style': 'rounded,filled', 'fillcolor': '#f0f2f6', 'fontname': 'Helvetica'})
    dot.attr(rankdir='LR', splines='ortho')

    # --- ANA TABLO (MAIN DRAW) ---
    with dot.subgraph(name='cluster_main') as main:
        main.attr(label='ANA TABLO (Main Draw)', style='filled', color='#e6f2ff')
        
        # 1. Tur (Son 16) - 8 Maç
        for i in range(1, 9):
            main.node(f'M_R1_{i}', f'Ana Tablo 1. Tur\nMaç {i}')
            
        # Çeyrek Final - 4 Maç
        for i in range(1, 5):
            main.node(f'M_QF_{i}', f'Çeyrek Final\nMaç {i}')
            
        # Yarı Final - 2 Maç
        for i in range(1, 3):
            main.node(f'M_SF_{i}', f'Yarı Final\nMaç {i}')
            
        # Final
        main.node('M_F', 'Ana Tablo\nFİNALİ')

        # Ana Tablo Kazananlar Akışı (Mavi Oklar)
        for i in range(1, 5):
            main.edge(f'M_R1_{i*2-1}', f'M_QF_{i}', color='blue', penwidth='2')
            main.edge(f'M_R1_{i*2}', f'M_QF_{i}', color='blue', penwidth='2')
            
        for i in range(1, 3):
            main.edge(f'M_QF_{i*2-1}', f'M_SF_{i}', color='blue', penwidth='2')
            main.edge(f'M_QF_{i*2}', f'M_SF_{i}', color='blue', penwidth='2')
            
        main.edge('M_SF_1', 'M_F', color='blue', penwidth='2')
        main.edge('M_SF_2', 'M_F', color='blue', penwidth='2')

    # --- TESELLİ TABLOSU (CONSOLATION DRAW) ---
    with dot.subgraph(name='cluster_cons') as cons:
        cons.attr(label='TESELLİ TABLOSU (Consolation)', style='filled', color='#fff0e6')
        
        # Teselli 1. Tur (Ana Tablo 1. Tur kaybedenleri kendi aralarında oynar) - 4 Maç
        for i in range(1, 5):
            cons.node(f'C_R1_{i}', f'Teselli 1. Tur\nMaç {i}')
            
        # Teselli 2. Tur (Feed-in: Teselli 1. Tur Kazananları vs Ana Tablo Çeyrek Final Kaybedenleri) - 4 Maç
        for i in range(1, 5):
            cons.node(f'C_R2_{i}', f'Teselli 2. Tur (Feed-in)\nMaç {i}')
            
        # Teselli Çeyrek Final - 2 Maç
        for i in range(1, 3):
            cons.node(f'C_QF_{i}', f'Teselli Yarı Final\nMaç {i}')
            
        # Teselli Final
        cons.node('C_F', 'Teselli\nFİNALİ')

        # Teselli Kazananlar Akışı
        for i in range(1, 5):
            cons.edge(f'C_R1_{i}', f'C_R2_{i}', color='blue', penwidth='2')
            
        for i in range(1, 3):
            cons.edge(f'C_R2_{i*2-1}', f'C_QF_{i}', color='blue', penwidth='2')
            cons.edge(f'C_R2_{i*2}', f'C_QF_{i}', color='blue', penwidth='2')
            
        cons.edge('C_QF_1', 'C_F', color='blue', penwidth='2')
        cons.edge('C_QF_2', 'C_F', color='blue', penwidth='2')

    # --- FEED-IN BAĞLANTILARI (KAYBEDENLERİN GEÇİŞİ) ---
    # 1. Tur Kaybedenleri Teselli 1. Tura Düşer (Kırmızı Oklar)
    for i in range(1, 5):
        dot.edge(f'M_R1_{i*2-1}', f'C_R1_{i}', color='red', style='dashed')
        dot.edge(f'M_R1_{i*2}', f'C_R1_{i}', color='red', style='dashed')

    # Çeyrek Final Kaybedenleri Teselli 2. Tura Düşer (Çapraz eşleşme prensibi eklenebilir, şimdilik direkt eşleşme)
    for i in range(1, 5):
        dot.edge(f'M_QF_{i}', f'C_R2_{i}', color='red', style='dashed')

    return dot

# Grafiği Streamlit üzerinde göster
st.graphviz_chart(draw_fixture(), use_container_width=True)
