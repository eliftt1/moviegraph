import os
import time
# Ana proje dosyanın adının 'main.py' olduğunu varsayıyoruz
from main import FilmUygulamasi

def test_raporu_yazdir(adim_adi, durum, detay=""):
    """Çıktıları düzenli göstermek için yardımcı fonksiyon"""
    sonuc = "✅ BAŞARILI" if durum else "❌ BAŞARISIZ"
    print(f"\nTEST ADIMI: {adim_adi}")
    print(f"DURUM     : {sonuc}")
    if detay:
        print(f"DETAY     : {detay}")
    print("-" * 40)

def manuel_test_baslat():
    print("=" * 50)
    print("PROJE 3 - SİSTEM FONKSİYON TESTLERİ BAŞLIYOR")
    print("=" * 50)

    # --- AYARLAR ---
    adres = "bolt://localhost:7687"
    kullanici = "neo4j"
    sifre = "buraya_sifreni_yaz" # !!! ŞİFRENİ GİRMEYİ UNUTMA

    # 1. BAĞLANTI TESTİ
    print("\n>>> [1] Veritabanı Bağlantısı Kuruluyor...")
    try:
        app = FilmUygulamasi(adres, kullanici, sifre)
        if app.driver:
            test_raporu_yazdir("Neo4j Bağlantısı", True, "Driver nesnesi oluşturuldu.")
        else:
            test_raporu_yazdir("Neo4j Bağlantısı", False, "Bağlantı sağlanamadı.")
            return # Bağlantı yoksa diğer testlere geçme
    except Exception as e:
        test_raporu_yazdir("Neo4j Bağlantısı", False, f"Hata: {e}")
        return

    # 2. ARAMA TESTİ (BAŞARILI SENARYO)
    print("\n>>> [2] 'Matrix' filmi aranıyor...")
    app.film_ara("Matrix")
    
    # Hafızadaki listeyi kontrol et
    if len(app.son_arama_sonuclari) > 0:
        test_raporu_yazdir("Film Arama (Pozitif)", True, f"{len(app.son_arama_sonuclari)} adet kayıt bulundu.")
    else:
        test_raporu_yazdir("Film Arama (Pozitif)", False, "Liste boş döndü.")

    # 3. ARAMA TESTİ (BOŞ SENARYO)
    print("\n>>> [3] Olmayan bir film aranıyor...")
    app.film_ara("BuFilmKesinlikleYok12345")
    
    if len(app.son_arama_sonuclari) == 0:
        test_raporu_yazdir("Film Arama (Negatif)", True, "Beklendiği gibi sonuç bulunamadı.")
    else:
        test_raporu_yazdir("Film Arama (Negatif)", False, "Olmayan film için sonuç döndü!")

    # 4. DETAY GÖSTERME TESTİ
    print("\n>>> [4] Detay gösterme testi hazırlanıyor...")
    # Önce tekrar geçerli bir arama yapalım ki liste dolsun
    app.film_ara("Matrix")
    print("... Listeden 1. sıradaki film seçiliyor ...")
    
    try:
        app.detay_goster(1) # 1. sıradaki filmi seç
        if app.secili_film_adi is not None:
            test_raporu_yazdir("Detay Gösterme", True, f"Seçilen Film: {app.secili_film_adi}")
        else:
            test_raporu_yazdir("Detay Gösterme", False, "Seçili film hafızaya alınamadı.")
    except Exception as e:
        test_raporu_yazdir("Detay Gösterme", False, f"Program hata verdi: {e}")

    # 5. HATALI SEÇİM TESTİ (HATA YÖNETİMİ)
    print("\n>>> [5] Liste dışı seçim (999) deneniyor...")
    try:
        app.detay_goster(999)
        # Eğer buraya kadar kod çökmeden geldiyse başarılıdır
        test_raporu_yazdir("Hatalı Giriş Kontrolü", True, "Program çökmedi, kullanıcı uyarıldı.")
    except Exception as e:
        test_raporu_yazdir("Hatalı Giriş Kontrolü", False, f"Program çöktü: {e}")

    # 6. JSON ÇIKTI TESTİ
    print("\n>>> [6] graph.json oluşturuluyor...")
    
    # Dosya varsa önce silelim ki test gerçekçi olsun
    dosya_yolu = "exports/graph.json"
    if os.path.exists(dosya_yolu):
        os.remove(dosya_yolu)
        
    app.json_cikti_al()
    
    # Dosya oluştu mu kontrol et
    if os.path.exists(dosya_yolu):
        boyut = os.path.getsize(dosya_yolu)
        test_raporu_yazdir("JSON Dosya Üretimi", True, f"Dosya mevcut. Boyut: {boyut} byte.")
    else:
        test_raporu_yazdir("JSON Dosya Üretimi", False, "Dosya oluşturulamadı.")

    # KAPANIŞ
    app.kapat()
    print("\n" + "=" * 50)
    print("TÜM TESTLER TAMAMLANDI")
    print("=" * 50)

if __name__ == "__main__":
    manuel_test_baslat()