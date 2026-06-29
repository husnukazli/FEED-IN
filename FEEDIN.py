try:
    import openpyxl
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Turnuva Fikstürü"

    # Başlıklar
    headers = ["Maç ID", "Tur", "Oyuncu 1", "Skor 1", "Skor 2", "Oyuncu 2", "Kazanan", "Kaybeden"]
    ws.append(headers)

    # Satır 2 - 9: Ana Tablo Son 16
    for i in range(1, 9):
        row_num = i + 1
        ws.append([
            f"M{i}", "Ana Tablo - Son 16", f"Oyuncu {2*i-1}", 0, 0, f"Oyuncu {2*i}", 
            f"=IF(D{row_num}>E{row_num},C{row_num},F{row_num})", 
            f"=IF(D{row_num}>E{row_num},F{row_num},C{row_num})"
        ])

    ws.append([]) # Satır 10 Boş

    # Satır 11 - 14: Ana Tablo Çeyrek Final
    ws.append(["M9", "Ana Tablo - Çeyrek Final", "=G2", 0, 0, "=G3", "=IF(D11>E11,C11,F11)", "=IF(D11>E11,F11,C11)"])
    ws.append(["M10", "Ana Tablo - Çeyrek Final", "=G4", 0, 0, "=G5", "=IF(D12>E12,C12,F12)", "=IF(D12>E12,F12,C12)"])
    ws.append(["M11", "Ana Tablo - Çeyrek Final", "=G6", 0, 0, "=G7", "=IF(D13>E13,C13,F13)", "=IF(D13>E13,F13,C13)"])
    ws.append(["M12", "Ana Tablo - Çeyrek Final", "=G8", 0, 0, "=G9", "=IF(D14>E14,C14,F14)", "=IF(D14>E14,F14,C14)"])

    ws.append([]) # Satır 15 Boş

    # Satır 16 - 19: Teselli 1. Tur
    ws.append(["M13", "Teselli - 1. Tur", "=H2", 0, 0, "=H3", "=IF(D16>E16,C16,F16)", "=IF(D16>E16,F16,C16)"])
    ws.append(["M14", "Teselli - 1. Tur", "=H4", 0, 0, "=H5", "=IF(D17>E17,C17,F17)", "=IF(D17>E17,F17,C17)"])
    ws.append(["M15", "Teselli - 1. Tur", "=H6", 0, 0, "=H7", "=IF(D18>E18,C18,F18)", "=IF(D18>E18,F18,C18)"])
    ws.append(["M16", "Teselli - 1. Tur", "=H8", 0, 0, "=H9", "=IF(D19>E19,C19,F19)", "=IF(D19>E19,F19,C19)"])

    ws.append([]) # Satır 20 Boş

    # Satır 21 - 24: Teselli 1. Birleşme
    ws.append(["M17", "Teselli - 1. Birleşme", "=G16", 0, 0, "=H14", "=IF(D21>E21,C21,F21)", "=IF(D21>E21,F21,C21)"])
    ws.append(["M18", "Teselli - 1. Birleşme", "=G17", 0, 0, "=H13", "=IF(D22>E22,C22,F22)", "=IF(D22>E22,F22,C22)"])
    ws.append(["M19", "Teselli - 1. Birleşme", "=G18", 0, 0, "=H12", "=IF(D23>E23,C23,F23)", "=IF(D23>E23,F23,C23)"])
    ws.append(["M20", "Teselli - 1. Birleşme", "=G19", 0, 0, "=H11", "=IF(D24>E24,C24,F24)", "=IF(D24>E24,F24,C24)"])

    ws.append([]) # Satır 25 Boş

    # Satır 26 - 27: Ana Tablo Yarı Final
    ws.append(["M21", "Ana Tablo - Yarı Final", "=G11", 0, 0, "=G12", "=IF(D26>E26,C26,F26)", "=IF(D26>E26,F26,C26)"])
    ws.append(["M22", "Ana Tablo - Yarı Final", "=G13", 0, 0, "=G14", "=IF(D27>E27,C27,F27)", "=IF(D27>E27,F27,C27)"])

    ws.append([]) # Satır 28 Boş

    # Satır 29 - 30: Teselli Yarı Final
    ws.append(["M23", "Teselli - Yarı Final", "=G21", 0, 0, "=G22", "=IF(D29>E29,C29,F29)", "=IF(D29>E29,F29,C29)"])
    ws.append(["M24", "Teselli - Yarı Final", "=G23", 0, 0, "=G24", "=IF(D30>E30,C30,F30)", "=IF(D30>E30,F30,C30)"])

    ws.append([]) # Satır 31 Boş

    # Satır 32 - 33: Teselli 2. Birleşme
    ws.append(["M25", "Teselli - 2. Birleşme", "=G29", 0, 0, "=H27", "=IF(D32>E32,C32,F32)", "=IF(D32>E32,F32,C32)"])
    ws.append(["M26", "Teselli - 2. Birleşme", "=G30", 0, 0, "=H26", "=IF(D33>E33,C33,F33)", "=IF(D33>E33,F33,C33)"])

    ws.append([]) # Satır 34 Boş

    # Satır 35 - 38: Final ve Derece Maçları
    ws.append(["M27", "Ana Tablo Finali (1.-2.lik)", "=G26", 0, 0, "=G27", "=IF(D35>E35,C35,F35)", "=IF(D35>E35,F35,C35)"])
    ws.append(["M28", "Teselli Finali (3.-4.lük)", "=G32", 0, 0, "=G33", "=IF(D36>E36,C36,F36)", "=IF(D36>E36,F36,C36)"])
    ws.append(["M29", "5.-6.lık Maçı", "=H29", 0, 0, "=H30", "=IF(D37>E37,C37,F37)", "=IF(D37>E37,F37,C37)"])
    ws.append(["M30", "7.-8.lik Maçı", "=H32", 0, 0, "=H33", "=IF(D38>E38,C38,F38)", "=IF(D38>E38,F38,C38)"])

    wb.save("Turnuva_Fiksturu.xlsx")
    print("\n[BAŞARILI] Canlı formüllü Excel dosyası yan klasörde oluşturuldu!")

except ModuleNotFoundError:
    print("\n[HATA] 'openpyxl' kütüphanesi yüklenmemiş.")
    print("Lütfen terminale/CMD'ye şu komutu yazıp yükleyin: pip install openpyxl")
except Exception as e:
    print(f"\n[HATA OLUŞTU]: {e}")

# Pencerenin hemen kapanmasını engelleyen satır:
input("\nPencereyi kapatmak için ENTER'a basın...")