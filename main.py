from neo4j import GraphDatabase
import json
import os

# Proje 3: Neo4j Film Veri Tabanı Uygulaması
# Yazar: [Adınız Soyadınız]
# Tarih: 2026

class FilmUygulamasi:
    def __init__(self, adres, kullanici, sifre):
        self.driver = None
        try:
            self.driver = GraphDatabase.driver(adres, auth=(kullanici, sifre))
            self.driver.verify_connectivity()
            print(">> Neo4j veritabanına başarıyla bağlanıldı.")
        except Exception as hata:
            print(f"!! Bağlantı hatası oluştu: {hata}")

        self.son_arama_sonuclari = []
        self.secili_film_adi = None

    def kapat(self):
        if self.driver:
            self.driver.close()

    # İster 1.3: Film Arama
    def film_ara(self, aranan_kelime):
        if not self.driver:
            print("Veritabanı bağlı değil!")
            return

        sorgu = """
        MATCH (m:Movie)
        WHERE toLower(m.title) CONTAINS toLower($k)
        RETURN m.title AS film_adi, m.released AS yil
        ORDER BY m.title
        """

        with self.driver.session() as oturum:
            sonuc = oturum.run(sorgu, k=aranan_kelime)
            filmler = [{"baslik": kayit["film_adi"], "yil": kayit["yil"]} for kayit in sonuc]

            self.son_arama_sonuclari = filmler

            if not filmler:
                print(f"'{aranan_kelime}' ile ilgili bir film bulunamadı.")
            else:
                print(f"\n--- '{aranan_kelime}' Arama Sonuçları ---")
                for sira, film in enumerate(filmler, 1):
                    print(f"{sira}) {film['baslik']} ({film['yil']})")

    # İster 1.4: Film Detay Gösterme
    def detay_goster(self, sira_no):
        if not self.son_arama_sonuclari:
            print("Lütfen önce bir film araması yapın.")
            return

        if sira_no < 1 or sira_no > len(self.son_arama_sonuclari):
            print("Hatalı seçim! Lütfen listedeki numaralardan birini girin.")
            return

        film_adi = self.son_arama_sonuclari[sira_no - 1]["baslik"]
        self.secili_film_adi = film_adi

        sorgu = """
        MATCH (m:Movie {title: $baslik})
        OPTIONAL MATCH (yonetmen:Person)-[:DIRECTED]->(m)
        OPTIONAL MATCH (oyuncu:Person)-[:ACTED_IN]->(m)
        RETURN m.title AS ad,
               m.released AS yil,
               m.tagline AS slogan,
               collect(DISTINCT yonetmen.name) AS yonetmenler,
               collect(DISTINCT oyuncu.name) AS oyuncular
        """

        with self.driver.session() as oturum:
            sonuc = oturum.run(sorgu, baslik=film_adi)
            kayit = sonuc.single()

            if kayit:
                print("\n" + "=" * 30)
                print(f"FILM: {kayit['ad']}")
                print(f"YIL: {kayit['yil']}")

                slogan = kayit['slogan'] if kayit['slogan'] else "Belirtilmemiş"
                print(f"SLOGAN: {slogan}")

                print("\nYÖNETMENLER:")
                for y in kayit['yonetmenler']:
                    print(f" - {y}")

                print("\nOYUNCULAR (İlk 5):")
                oyuncular = kayit['oyuncular']
                for o in oyuncular[:5]:
                    print(f" * {o}")

                kalan = len(oyuncular) - 5
                if kalan > 0:
                    print(f" ... ve {kalan} oyuncu daha.")

                print("=" * 30)

    # İster 1.5: Graph JSON Oluşturma
    def json_cikti_al(self):
        if not self.secili_film_adi:
            print("Önce 'Film Detayı Göster' seçeneği ile bir film seçmelisiniz.")
            return

        print(f"'{self.secili_film_adi}' için veriler hazırlanıyor...")

        sorgu = """
        MATCH (m:Movie {title: $baslik})
        OPTIONAL MATCH (kisi:Person)-[iliski:ACTED_IN|DIRECTED]->(m)
        RETURN m, kisi, type(iliski) AS iliski_tipi
        """

        dugumler = []
        baglantilar = []
        eklenen_idler = set()

        with self.driver.session() as oturum:
            sonuclar = oturum.run(sorgu, baslik=self.secili_film_adi)

            for satir in sonuclar:
                film_node = satir["m"]
                kisi_node = satir["kisi"]
                iliski_tipi = satir["iliski_tipi"]

                if film_node.element_id not in eklenen_idler:
                    dugumler.append({
                        "id": film_node.element_id,
                        "label": "Movie",
                        "title": film_node["title"],
                        "released": film_node["released"]
                    })
                    eklenen_idler.add(film_node.element_id)

                if kisi_node:
                    if kisi_node.element_id not in eklenen_idler:
                        dugumler.append({
                            "id": kisi_node.element_id,
                            "label": "Person",
                            "name": kisi_node["name"]
                        })
                        eklenen_idler.add(kisi_node.element_id)

                    baglantilar.append({
                        "source": kisi_node.element_id,
                        "target": film_node.element_id,
                        "type": iliski_tipi
                    })

        json_verisi = {"nodes": dugumler, "links": baglantilar}

        klasor = "exports"
        if not os.path.exists(klasor):
            os.makedirs(klasor)

        dosya_yolu = f"{klasor}/graph.json"

        try:
            with open(dosya_yolu, "w", encoding="utf-8") as dosya:
                json.dump(json_verisi, dosya, indent=4, ensure_ascii=False)
            print(f"BAŞARILI! Dosya oluşturuldu: {dosya_yolu}")
        except Exception as e:
            print(f"Dosya yazılırken hata oluştu: {e}")


# Ana Program
def calistir():
    neo4j_adres = "bolt://localhost:7687"
    kullanici_adi = "neo4j"
    sifre = "eliftun4141"

    uygulama = FilmUygulamasi(neo4j_adres, kullanici_adi, sifre)

    if not uygulama.driver:
        return

    while True:
        print("\n--- FİLM GRAF SİSTEMİ ---")
        print("1) Film Ara")
        print("2) Film Detayı Göster")
        print("3) Seçili Film için graph.json Oluştur")
        print("4) Çıkış")

        secim = input("Yapmak istediğiniz işlem (1-4): ")

        if secim == "1":
            kelime = input("Aranacak film adı: ").strip()
            if kelime:
                uygulama.film_ara(kelime)
            else:
                print("Boş bırakmayınız.")

        elif secim == "2":
            try:
                sayi = int(input("Listeden film numarasını giriniz: "))
                uygulama.detay_goster(sayi)
            except ValueError:
                print("Lütfen geçerli bir sayı girin.")

        elif secim == "3":
            uygulama.json_cikti_al()

        elif secim == "4":
            print("Programdan çıkılıyor...")
            uygulama.kapat()
            break

        else:
            print("Geçersiz seçenek.")


if __name__ == "__main__":
    calistir()
