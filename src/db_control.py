import sqlite3
import os

# main.py'deki yol ile aynı şekilde hesaplayın.
# Eğer main.py src/ klasöründeyse, bu yol src'nin bir üst klasöründeki data klasörüne işaret eder.
# Bu kısmı kendi dosya yapınıza göre ayarlamanız gerekebilir.
db_path = os.path.join(os.getcwd(), "data", "universite.db")
print(f"Veritabanı yolu kontrol ediliyor: {db_path}")

try:
    if not os.path.exists(db_path):
        print("HATA: Veritabanı dosyası bulunamadı!")
    else:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Üniversiteler tablosundaki kayıt sayısını kontrol et
        cursor.execute("SELECT COUNT(*) FROM Üniversiteler")
        node_count = cursor.fetchone()[0]
        conn.close()

        print(f"Üniversiteler tablosunda {node_count} adet kayıt bulundu.")

        if node_count == 0:
            print("❗ Sorun: Kayıt sayısı 0. Lütfen üniversite ekleyin.")
        else:
            print("✅ Veritabanında veri var. Sorun, muhtemelen DataLoader'dadır.")

except sqlite3.OperationalError as e:
    print(f"HATA: Veritabanına erişirken sorun oluştu: {e}")
except Exception as e:
    print(f"Beklenmedik bir hata oluştu: {e}")