"""
Bracket agaci icin kesin koordinat hesaplayici.
Hem SVG (ekran) hem FPDF (PDF) tarafi AYNI bu fonksiyonlari kullanacak,
boylece ikisi birebir ayni gorunecek.
"""

BOX_W = 150
BOX_H = 50
R1_PITCH = 64   # bir R1 kutusunun kapladigi dikey alan (kutu + bosluk)

def r1_center(i):
    return 25 + R1_PITCH * i + BOX_H/2 - 25  # basitce: ilk kutunun merkezi 25+BOX_H/2

def compute_main_bracket():
    """8 R1 -> 4 CF -> 2 YF -> 1 Final. Koordinatlar (x,y_center) olarak, y sadece dikey eksen birimi (0-1 araligina normalize edilecek disaridan)."""
    r1 = []
    for i in range(8):
        top = 20 + R1_PITCH * i
        center = top + BOX_H/2
        r1.append({"id": f"MR1_{i}", "top": top, "center": center})

    qf = []
    for j in range(4):
        c = (r1[2*j]["center"] + r1[2*j+1]["center"]) / 2
        qf.append({"id": f"MQF_{j}", "top": c - BOX_H/2, "center": c})

    sf = []
    for k in range(2):
        c = (qf[2*k]["center"] + qf[2*k+1]["center"]) / 2
        sf.append({"id": f"MSF_{k}", "top": c - BOX_H/2, "center": c})

    final_c = (sf[0]["center"] + sf[1]["center"]) / 2
    final = {"id": "FINAL_MAIN", "top": final_c - BOX_H/2, "center": final_c}

    total_h = r1[-1]["top"] + BOX_H + 20
    return {"r1": r1, "qf": qf, "sf": sf, "final": final, "height": total_h}

def compute_consolation_bracket(main):
    """
    T-R1 (4) -> T-CF (4) -> T-YF1 (2) -> T-YF2 (2) -> 3 yerlesim mac (3-4 / 5-6 / 7-8)
    Gercek koddaki besleme mantigina birebir uyacak sekilde.
    """
    r1 = main["r1"]; qf = main["qf"]; sf = main["sf"]
    # T-R1: kaybeden(R1_2j) vs kaybeden(R1_2j+1)  -> ayni y hizasinda R1 ile
    t_r1 = []
    for j in range(4):
        c = (r1[2*j]["center"] + r1[2*j+1]["center"]) / 2  # QF ile ayni hiza (dogal)
        t_r1.append({"id": f"CR1_{j}", "top": c - BOX_H/2, "center": c})

    # T-CF: kazanan(T-R1_i) vs kaybeden(QF, ters sirali)  -> T-R1 ile ayni hiza
    t_cf = []
    for i in range(4):
        c = t_r1[i]["center"]
        t_cf.append({"id": f"CR2_{i}", "top": c - BOX_H/2, "center": c})

    # T-YF1: kazanan(T-CF_2k) vs kazanan(T-CF_2k+1)
    t_yf1 = []
    for k in range(2):
        c = (t_cf[2*k]["center"] + t_cf[2*k+1]["center"]) / 2
        t_yf1.append({"id": f"CR3_{k}", "top": c - BOX_H/2, "center": c})

    # T-YF2: kazanan(T-YF1_k) vs kaybeden(SF_k)
    t_yf2 = []
    for k in range(2):
        c = t_yf1[k]["center"]
        t_yf2.append({"id": f"CR4_{k}", "top": c - BOX_H/2, "center": c})

    # Yerlesim maclari: kendi sutunlarinda, ust uste binmeyecek sekilde ayri ayri istiflenir.
    final_teselli = {"id": "FINAL_TESELLI", "top": 160, "center": 160 + BOX_H/2}
    m56 = {"id": "MATCH_5_6", "top": 160 + R1_PITCH, "center": 160 + R1_PITCH + BOX_H/2}
    m78 = {"id": "MATCH_7_8", "top": 160 + 2*R1_PITCH, "center": 160 + 2*R1_PITCH + BOX_H/2}

    return {"t_r1": t_r1, "t_cf": t_cf, "t_yf1": t_yf1, "t_yf2": t_yf2,
            "final_teselli": final_teselli, "m56": m56, "m78": m78}

if __name__ == "__main__":
    main = compute_main_bracket()
    cons = compute_consolation_bracket(main)
    print("Ana tablo yukseklik:", main["height"])
    for k, v in main.items():
        if k != "height":
            print(k, [round(x["center"],1) for x in (v if isinstance(v, list) else [v])])
    print("---Teselli---")
    for k, v in cons.items():
        print(k, [round(x["center"],1) for x in (v if isinstance(v, list) else [v])])
