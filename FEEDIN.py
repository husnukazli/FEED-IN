import os
import json

# --- VERİ TABANI YÖNETİMİ (Sunucu Dosyası) ---
DB_FILE = "turnuva_db.json"

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # Dosya yoksa varsayılan boş veriyi oluştur
    return {
        'Erkekler': {'players': [f"Oyuncu {i}" for i in range(1, 17)], 'res': {}, 'scores': {}, 'schedule_data': {}},
        'Kadınlar': {'players': [f"Oyuncu {i}" for i in range(1, 17)], 'res': {}, 'scores': {}, 'schedule_data': {}}
    }

def save_data():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.data, f)

# Oturum verisini dosyadan yükle
if 'data' not in st.session_state:
    st.session_state.data = load_data()

active_cat = st.radio("Turnuva Kategorisi:", ["Erkekler", "Kadınlar"], horizontal=True) if not is_read_only else st.selectbox("Turnuva Kategorisi:", ["Erkekler", "Kadınlar"])
cat_data = st.session_state.data[active_cat]

# NOT: Skor veya Kazanan girilen her yere save_data() fonksiyonunu eklemelisin.
# Örneğin match_card fonksiyonunun içinde:
# cat_data['scores'][m_id] = score
# save_data() # <--- VERİYİ ANINDA DOSYAYA KAYDET
