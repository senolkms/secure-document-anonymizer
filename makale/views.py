from arrow import now
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from .models import Makaleler, Mesaj,EditorAtama,HakemDegerlendirme
import os
import random
import PyPDF2
import spacy
import PyPDF2
import re
from pdfminer.high_level import extract_text
from cryptography.fernet import Fernet
from django.core.files.storage import default_storage
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import fitz 
from django.http import HttpResponse
from django.urls import reverse
from Crypto.PublicKey import RSA
import base64, os, fitz, hashlib
from Crypto.Random import get_random_bytes
import json
import cv2
import numpy as np
# Spacy dil modeli
nlp = spacy.load("en_core_web_sm")

# AES şifreleme anahtarı oluştur
key = Fernet.generate_key()
cipher_suite = Fernet(key)



# Ana sayfa fonksiyonu
def ana_sayfa(request):
    return render(request, 'index.html')  # Ana sayfa gösterilir

# Makale yükleme sayfasını açan fonksiyon
def makale_yukleme_sayfasi(request):
    return render(request, 'makale_yukle.html')  # HTML şablonunu yükler

# Makale yükleme işlemi
@csrf_exempt
def makale_yukle(request):
    if request.method == "POST":
        email = request.POST.get("email")
        pdf_file = request.FILES.get("file")

        # 1. PDF kontrolü
        if not pdf_file.name.endswith('.pdf'):
            return JsonResponse({"error": "Sadece PDF dosyaları yüklenebilir!"}, status=400)

        # 2. Dosya boyutu kontrolü (5MB sınırı)
        if pdf_file.size > 5 * 1024 * 1024:
            return JsonResponse({"error": "Dosya boyutu 5MB'ı geçemez!"}, status=400)

        # 3. Takip numarası oluştur (10 haneli rastgele sayı)
        takip_no = ''.join([str(random.randint(0, 9)) for _ in range(10)])

        # 4. Dosyayı belirlenen dizine kaydet
        file_path = f"makaleler/{email}/"
        file_name = default_storage.save(os.path.join(file_path, pdf_file.name), pdf_file)

        # 5. Veritabanına makale kaydetme
        makale = Makaleler.objects.create(
            takip_no=takip_no,
            yazar_eposta=email,
            orijinal_dosya=file_name
        )

        return JsonResponse({"message": "Makale başarıyla yüklendi!", "takip_no": takip_no})

    return JsonResponse({"error": "Geçersiz istek"}, status=400)

def makale_sorgulama_sayfasi(request):
    return render(request, 'makale_sorgula.html')

def makale_sorgula(request):
    takip_no = request.GET.get("takip_no")

    if not takip_no:
        return JsonResponse({"error": "Lütfen bir takip numarası girin!"}, status=400)

    try:
        makale = Makaleler.objects.get(takip_no=takip_no)
        return JsonResponse({
            "takip_no": makale.takip_no,
            "durum": makale.durum,
            "yazar_eposta": makale.yazar_eposta
        })
    except Makaleler.DoesNotExist:
        return JsonResponse({"error": "Böyle bir makale bulunamadı!"}, status=404)
    
def mesaj_gonderme_sayfasi(request):
    takip_no = request.GET.get("takip_no")
    eposta = request.GET.get("eposta")
    return render(request, 'mesaj_gonder.html', {"takip_no": takip_no, "eposta": eposta})

# Editöre mesaj gönderme API
@csrf_exempt
def mesaj_gonder(request):
    if request.method == "POST":
        takip_no = request.POST.get("takip_no")
        gonderen_eposta = request.POST.get("gonderen_eposta")
        mesaj_icerik = request.POST.get("mesaj")

        if not takip_no:
            return JsonResponse({"error": "Takip numarası eksik!"}, status=400)
        if not gonderen_eposta or not mesaj_icerik:
            return JsonResponse({"error": "Lütfen tüm alanları doldurun!"}, status=400)

        # Mesajı veritabanına kaydet
        mesaj = Mesaj.objects.create(
            takip_no=takip_no,
            gonderen_eposta=gonderen_eposta,
            mesaj=mesaj_icerik
        )

        return JsonResponse({"message": "Mesaj başarıyla gönderildi!"})

    elif request.method == "GET":
        takip_no = request.GET.get("takip_no")
        if not takip_no:
            return JsonResponse({"error": "Takip numarası eksik!"}, status=400)

        # Veritabanından ilgili makale için mesajları al
        mesajlar = Mesaj.objects.filter(takip_no=takip_no).order_by("tarih")
        mesaj_listesi = [
            {"gonderen": mesaj.gonderen_eposta, "icerik": mesaj.mesaj, "tarih": mesaj.tarih.strftime("%d-%m-%Y %H:%M")}
            for mesaj in mesajlar
        ]

        return JsonResponse({"mesajlar": mesaj_listesi})
    
    return JsonResponse({"error": "Geçersiz istek!"}, status=400)

def editor_paneli(request):
    makaleler = Makaleler.objects.all().order_by('-id')  # En yeni makaleler üstte gözüksün
    return render(request, 'editor_panel.html', {'makaleler': makaleler})

def editor_mesaj(request):
    takip_no = request.GET.get("takip_no")

    if not takip_no:
        return HttpResponse("Takip numarası eksik!", status=400)

    makale = Makaleler.objects.filter(takip_no=takip_no).first()
    if not makale:
        return HttpResponse("Makale bulunamadı!", status=404)

    if request.method == "POST":
        mesaj_icerik = request.POST.get("mesaj")
        if not mesaj_icerik:
            return render(request, "editor_mesaj.html", {
                "takip_no": takip_no,
                "mesajlar": [],
                "error": "Mesaj içeriği boş olamaz!"
            })

        # Mesajı kaydet
        Mesaj.objects.create(
            takip_no=takip_no,
            gonderen_eposta="editor@example.com",
            mesaj=mesaj_icerik
        )
        return redirect(f"/editor_mesaj/?takip_no={takip_no}")

    mesajlar = Mesaj.objects.filter(takip_no=takip_no).order_by("tarih")
    return render(request, "editor_mesaj.html", {
        "takip_no": takip_no,
        "mesajlar": mesajlar
    })
    
ALANLAR = {
    "Bilgisayar Bilimleri": ["machine learning", "deep learning", "neural network", "AI", "artificial intelligence", "algorithm", "data science"],
    "Makine Öğrenmesi": ["regression", "classification", "supervised learning", "unsupervised learning", "reinforcement learning"],
    "Veri Bilimi": ["data mining", "big data", "data analysis", "statistical modeling"],
    "Elektrik Elektronik": ["circuit", "voltage", "current", "electrical", "signal processing", "microcontroller"],
    "Fizik": ["quantum", "mechanics", "relativity", "particle physics"],
    "Biyoloji": ["genetics", "DNA", "RNA", "biotechnology", "bioinformatics"]
}

def otomatik_alan_atama(makale_metni):
    """ PDF içeriğine göre en uygun akademik alanı belirler. """
    alan_skorlari = {alan: 0 for alan in ALANLAR}

    for alan, anahtar_kelime_listesi in ALANLAR.items():
        for kelime in anahtar_kelime_listesi:
            if re.search(r'\b' + re.escape(kelime) + r'\b', makale_metni, re.IGNORECASE):
                alan_skorlari[alan] += 1

    # En yüksek puanı alan alanı belirle
    en_iyi_alan = max(alan_skorlari, key=alan_skorlari.get)
    return en_iyi_alan if alan_skorlari[en_iyi_alan] > 0 else "Diğer"

def alan_atama(request):
    takip_no = request.GET.get("takip_no")

    if not takip_no:
        return render(request, 'editor_panel.html', {"error": "Takip numarası bulunamadı!"})

    try:
        makale = Makaleler.objects.get(takip_no=takip_no)
        pdf_path = makale.orijinal_dosya.path

        # PDF içeriğini çıkar
        makale_metni = extract_text(pdf_path)

        # Spacy kullanarak önemli kelimeleri belirle
        doc_nlp = nlp(makale_metni)
        anahtar_kelime_listesi = [token.text.lower() for token in doc_nlp if not token.is_stop and token.is_alpha]

        # Alanı belirle
        otomatik_alan = otomatik_alan_atama(" ".join(anahtar_kelime_listesi))

        # Makalenin alanını güncelle
        makale.alan = otomatik_alan
        
        # Durum güncellemesi
        if makale.durum == "incelemede":
            makale.durum = "incelemede"  # Durum aynı kalabilir veya başka bir duruma geçirilebilir
        
        makale.save()

        return render(request, 'alan_atama.html', {'makale': makale, 'atanan_alan': otomatik_alan})

    except Makaleler.DoesNotExist:
        return render(request, 'editor_panel.html', {"error": "Makale bulunamadı!"})
    
def makale_detay(request):
    takip_no = request.GET.get("takip_no")

    if not takip_no:
        return render(request, 'editor_panel.html', {"error": "Takip numarası bulunamadı!"})

    try:
        makale = Makaleler.objects.get(takip_no=takip_no)
        pdf_path = makale.orijinal_dosya.path

        # PDF içeriğini çıkar
        makale_metni = extract_text(pdf_path)

        # Spacy kullanarak yazar ve kurum isimlerini belirle
        doc_nlp = nlp(makale_metni)
        yazarlar = set()
        kurumlar = set()

        for ent in doc_nlp.ents:
            if ent.label_ == "PERSON":  # Yazar isimleri
                yazarlar.add(ent.text)
            elif ent.label_ == "ORG":  # Kurum isimleri
                kurumlar.add(ent.text)

        # Tespit edilen bilgileri modele kaydet
        makale.yazar_bilgileri = ", ".join(yazarlar)
        makale.kurum_bilgileri = ", ".join(kurumlar)
        makale.save()

        # Alan atama
        if request.method == "POST":
            atanan_alan = request.POST.get("alan")
            makale.alan = atanan_alan
            makale.save()
            return redirect('/editor_panel/')

        return render(request, 'makale_detay.html', {'makale': makale, 'yazarlar': yazarlar, 'kurumlar': kurumlar})

    except Makaleler.DoesNotExist:
        return render(request, 'editor_panel.html', {"error": "Makale bulunamadı!"})
    
def hakeme_ata(request):
    takip_no = request.GET.get("takip_no")
    if not takip_no:
        return redirect("/editor_panel/")

    try:
        makale = Makaleler.objects.get(takip_no=takip_no)

        if not makale.anonim_makale:
            return render(request, "hakeme_ata.html", {
                "makale": makale,
                "error": "❗ Bu makalenin anonimleştirilmiş hali bulunmuyor!"
            })

        alan = makale.alan.lower() if makale.alan else None
        if not alan:
            return render(request, "hakeme_ata.html", {
                "makale": makale,
                "error": "❗ Makalenin alanı atanmadığı için uygun hakem bulunamadı."
            })

        # ALANA GÖRE FİLTRELİ HAKEM LİSTESİ
        uygun_hakemler = []
        for hakem in HakemDegerlendirme.objects.all():
            if hakem.ilgi_alanlari:
                alanlar = [a.strip().lower() for a in hakem.ilgi_alanlari.split(",")]
                if alan in alanlar:
                    uygun_hakemler.append(hakem)

        if request.method == "POST":
            secilen_eposta = request.POST.get("hakem_eposta")
            if not secilen_eposta:
                return render(request, "hakeme_ata.html", {
                    "makale": makale,
                    "hakemler": hakem,
                    "error": "Lütfen bir hakem seçin."
                })

            EditorAtama.objects.create(
                makale=makale,
                editör_eposta="editor@example.com",
                hakem_eposta=secilen_eposta,
                atama_tarihi=now()
            )

            HakemDegerlendirme.objects.create(
                hakem_eposta=secilen_eposta,
                anonim_makale=makale.anonim_makale,
                ilgi_alanlari=""  # opsiyonel
            )

            makale.hakem_eposta = secilen_eposta
            makale.durum = "hakemde"
            makale.save()

            return redirect("/editor_panel/")

        return render(request, "hakeme_ata.html", {
            "makale": makale,
            "hakemler": uygun_hakemler
        })

    except Makaleler.DoesNotExist:
        return redirect("/editor_panel/")
    
def hakem_giris(request):
    return render(request, "hakem_giris.html")

def hakem_panel(request):
    if request.method == "POST":
        eposta = request.POST.get("eposta")
        if not eposta:
            return render(request, "hakem_giris.html", {"error": "Lütfen e-posta giriniz!"})

        makaleler = HakemDegerlendirme.objects.filter(hakem_eposta=eposta)
        return render(request, "hakem_panel.html", {"makaleler": makaleler, "eposta": eposta})
    
    # Hatalı reverse nedeniyle burası bozuluyordu, düzeltildi:
    return redirect(reverse("makale:hakem_giris"))
    

def ekle_degerlendirme_sayfasi(orijinal_pdf_path, degerlendirme_metin, takip_no, aciklama=None, karar=None):
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_OAEP
    import base64, hashlib, json

    output_path = f"degerlendirmeli_pdf/deg_{takip_no}.pdf"
    output_full_path = f"media/{output_path}"

    doc = fitz.open(orijinal_pdf_path)
    yeni_sayfa = doc.new_page()

    # Sayfa başlığı
    baslik = "RESMI HAKEM DEGERLENDIRME RAPORU"
    yeni_sayfa.insert_text((50, 50), baslik, fontsize=18, fontname="helv", color=(0, 0, 0.8))

    # Tarih bilgisi
    from datetime import datetime
    tarih_str = datetime.now().strftime("%d.%m.%Y")
    yeni_sayfa.insert_text((450, 50), f"Tarih: {tarih_str}", fontsize=10, fontname="helv", color=(0, 0, 0))

    # Referans numarası
    yeni_sayfa.insert_text((50, 80), f"Ref No: {takip_no}", fontsize=10, fontname="helv", color=(0, 0, 0))

    # Karar durumu
    karar_metin = ""
    karar_renk = (0, 0, 0)
    if karar == "yayınlandı":
        karar_metin = "KABUL EDILDI ✓"
        karar_renk = (0, 0.5, 0)
    elif karar == "revizyon":
        karar_metin = "REVIZYON GEREKLI ⟳"
        karar_renk = (0.9, 0.6, 0)
    elif karar == "reddedildi":
        karar_metin = "REDDEDILDI ✗"
        karar_renk = (0.8, 0, 0)

    if karar_metin:
        yeni_sayfa.insert_text((350, 80), karar_metin, fontsize=12, fontname="helv", color=karar_renk)

    # Değerlendirme alanları
    yeni_sayfa.draw_line((50, 100), (550, 100))  # Üst çizgi

    # Hakem değerlendirmesini şifrele ve gizli yazı olarak ekle
    with open("keys/editor_public.pem", "rb") as f:
        rsa_public_key = RSA.import_key(f.read())
        rsa_cipher = PKCS1_OAEP.new(rsa_public_key)

        if degerlendirme_metin:
            sifreli = rsa_cipher.encrypt(degerlendirme_metin.encode())
            sifreli_base64 = base64.b64encode(sifreli).decode()
            hash_val = hashlib.sha256(degerlendirme_metin.encode()).hexdigest()

            # Sadece işaretleme için görünür yazı
            yeni_sayfa.insert_text((50, 120), "Şifreli hakem değerlendirmesi eklendi.", fontsize=11, fontname="helv", color=(0, 0, 0))

            # Log kaydı
            os.makedirs("media/anonim_makaleler", exist_ok=True)
            with open(f"media/anonim_makaleler/log_{takip_no}.txt", "a", encoding="utf-8") as f_log:
                f_log.write(json.dumps({
                    "tip": "HakemDegerlendirme",
                    "sifreli_veri": sifreli_base64,
                    "hash": hash_val,
                    "sayfa": len(doc) - 1,
                    "konum": [50, 140, 550, 700]
                }) + "\n")

    # Alt çizgi ve özet
    yeni_sayfa.draw_line((50, 730), (550, 730))

    # Özet bilgiler
    ozet_metin = "Bu degerlendirme raporu, akademik icerigin bilimsel degerlendirilmesi amaciyla hazirlanmistir. "

    yeni_sayfa.insert_text((50, 750), ozet_metin, fontsize=9, fontname="helv", color=(0.4, 0.4, 0.4))

    os.makedirs("media/degerlendirmeli_pdf", exist_ok=True)
    doc.save(output_full_path)
    doc.close()

    return output_path

def hakem_degerlendir(request):
    id = request.GET.get("id")
    try:
        makale = HakemDegerlendirme.objects.get(id=id)
    except HakemDegerlendirme.DoesNotExist:
        return HttpResponse("❌ Makale bulunamadı!", status=404)

    if request.method == "POST":
        degerlendirme_metni = request.POST.get("degerlendirme")
        aciklama = request.POST.get("aciklama")
        hakem_karari = request.POST.get("karar", "revizyon")
        
        # Değerlendirme verilerini kaydet
        makale.degerlendirme = degerlendirme_metni
        makale.aciklama = aciklama
        
 
        # PDF oluştur
        orijinal_path = f"media/{makale.anonim_makale}"
        takip_no = makale.anonim_makale.name.split("_")[-1].replace(".pdf", "")
        yeni_pdf_yolu = ekle_degerlendirme_sayfasi(
            orijinal_path, 
            makale.degerlendirme, 
            takip_no,
            aciklama=makale.aciklama,
            karar=hakem_karari
        )

        makale.son_hali = yeni_pdf_yolu
        makale.degerlendirme_tamamlandi = True  # Yeni alan
        makale.save()
        
        # İlgili makaleyi bul ve durumunu güncelle
        try:
            orijinal_makale = Makaleler.objects.get(takip_no=takip_no)
            orijinal_makale.durum = hakem_karari
            orijinal_makale.save()
        except Makaleler.DoesNotExist:
            pass

        return redirect(reverse("makale:hakem_panel"))

    return render(request, "hakem_degerlendir.html", {"makale": makale})



def anonimlestir_makale(request):
    from Crypto.Cipher import PKCS1_OAEP
    from Crypto.PublicKey import RSA
    import base64, hashlib
    
    def sifrele_veri(veri, rsa_public_key):
        rsa_cipher = PKCS1_OAEP.new(rsa_public_key)
        encrypted = rsa_cipher.encrypt(veri.encode())
        return {
            "sifreli_veri": base64.b64encode(encrypted).decode(),
            "hash": hashlib.sha256(veri.encode()).hexdigest()
        }
        
    def tespit_et_fotograflar(page):
        """Sayfada fotoğraf/görsel olup olmadığını tespit eder"""
        img_list = page.get_images(full=True)
        gorseller = []
        
        for img_index, img in enumerate(img_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            
            # OpenCV ile görüntüyü analiz et
            nparr = np.frombuffer(image_bytes, np.uint8)
            img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Yüz tespiti yap
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            if len(faces) > 0:  # Yüz tespit edildiyse
                for (x, y, w, h) in faces:
                    # Görsel koordinatlarını sayfadaki konuma çevir
                    rect = page.get_image_rects(xref)[0]  # Görsel konumu
                    yuz_konum = {
                        "xref": xref,
                        "img_index": img_index,
                        "rect": [rect.x0, rect.y0, rect.x1, rect.y1],
                        "yuz": [x, y, w, h]
                    }
                    gorseller.append(yuz_konum)
                    
        return gorseller

    if request.method == "POST":
        takip_no = request.POST.get("takip_no")
        anonim_yazarlar = request.POST.getlist("anonim_yazarlar")
        anonim_kurumlar = request.POST.getlist("anonim_kurumlar")
        anonim_fotograflar = request.POST.get("anonim_fotograflar", "true")  # Varsayılan olarak fotoğrafları anonimleştir

        if not takip_no:
            return redirect('/editor_panel/')

        try:
            makale = Makaleler.objects.get(takip_no=takip_no)
            orijinal_path = makale.orijinal_dosya.path
            yeni_dosya_adı = f"anonim_{makale.takip_no}.pdf"
            anonim_klasor = "media/anonim_makaleler/"

            if not os.path.exists(anonim_klasor):
                os.makedirs(anonim_klasor)

            anonim_path = os.path.join(anonim_klasor, yeni_dosya_adı)

            doc = fitz.open(orijinal_path)

            with open("keys/editor_public.pem", "rb") as f:
                rsa_public_key = RSA.import_key(f.read())

            loglar = []

            # Metin anonimleştirme
            for page_number, page in enumerate(doc):
                for hedef_kelime, tipi in zip(anonim_yazarlar + anonim_kurumlar,
                                          ["Yazar"] * len(anonim_yazarlar) + ["Kurum"] * len(anonim_kurumlar)):
                    text_instances = page.search_for(hedef_kelime)
                    for inst in text_instances:
                        # Veriyi şifrele
                        sonuc = sifrele_veri(hedef_kelime, rsa_public_key)

                        # Blur alanı (beyaz dikdörtgen)
                        page.draw_rect(inst, color=(1, 1, 1), fill=(1, 1, 1))

                        # Alan bilgilerini logla
                        loglar.append({
                            "tip": tipi,
                            "orijinal": hedef_kelime,
                            **sonuc,
                            "sayfa": page_number,
                            "konum": [inst.x0, inst.y0, inst.x1, inst.y1]
                        })
                
                # Fotoğraf anonimleştirme
                if anonim_fotograflar == "true":
                    fotograflar = tespit_et_fotograflar(page)
                    for foto in fotograflar:
                        xref = foto["xref"]
                        rect = fitz.Rect(*foto["rect"])
                        
                        # Fotoğrafı beyaz dikdörtgen ile kapat
                        page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
                        
                        # "ANONYMOUS AUTHOR" yazısı ekle
                        text_point = fitz.Point(rect.x0 + 5, rect.y0 + (rect.height / 2))
                        page.insert_text(text_point, "ANONYMOUS AUTHOR", 
                                        fontsize=12, color=(0.5, 0.5, 0.5))
                        
                        # Fotoğraf bilgilerini logla
                        loglar.append({
                            "tip": "Fotograf",
                            "orijinal": f"Fotograf-{xref}",
                            "sayfa": page_number,
                            "konum": [rect.x0, rect.y0, rect.x1, rect.y1]
                        })

            doc.save(anonim_path)
            doc.close()

            makale.anonim_makale.name = f"anonim_makaleler/{yeni_dosya_adı}"
            makale.durum = "incelemede"
            makale.save()

            with open(f"media/anonim_makaleler/log_{makale.takip_no}.txt", "w", encoding="utf-8") as f:
                for log in loglar:
                    f.write(json.dumps(log) + "\n")

            return redirect('/editor_panel/')

        except Makaleler.DoesNotExist:
            return redirect('/editor_panel/')

def desifre_et(request):
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_OAEP
    import base64, json, fitz, os

    takip_no = request.GET.get("takip_no")
    if not takip_no:
        return HttpResponse("Takip numarası belirtilmedi!", status=400)

    log_dosyasi = f"media/anonim_makaleler/log_{takip_no}.txt"
    private_key_path = "keys/editor_private.pem"
    orijinal_pdf_path = f"media/degerlendirmeli_pdf/deg_{takip_no}.pdf"
    desifreli_pdf_path = f"media/degerlendirmeli_pdf/deg_{takip_no}_desifreli.pdf"
    pdf_url = f"/media/degerlendirmeli_pdf/deg_{takip_no}_desifreli.pdf"
    
    # Orijinal makalenin yolunu da al - görselleri buradan alacağız
    try:
        makale = Makaleler.objects.get(takip_no=takip_no)
        orijinal_makale_path = makale.orijinal_dosya.path
    except Makaleler.DoesNotExist:
        orijinal_makale_path = None

    try:
        with open(private_key_path, "rb") as key_file:
            private_key = RSA.import_key(key_file.read())
        rsa_cipher = PKCS1_OAEP.new(private_key)
    except Exception as e:
        return HttpResponse(f"Özel anahtar yüklenemedi: {e}", status=500)

    cozulmus_veriler = []

    try:
        with open(log_dosyasi, "r", encoding="utf-8") as log:
            log_veriler = [eval(satir.strip()) for satir in log if satir.strip()]
    except FileNotFoundError:
        return HttpResponse("Log dosyası bulunamadı!", status=404)

    try:
        # Deşifre edilecek dosyayı aç
        doc = fitz.open(orijinal_pdf_path)
        
        # Orijinal makaleyi de aç (görselleri kopyalamak için)
        if orijinal_makale_path and os.path.exists(orijinal_makale_path):
            orijinal_doc = fitz.open(orijinal_makale_path)
        else:
            orijinal_doc = None

        for veri in log_veriler:
            try:
                sayfa = int(veri["sayfa"])
                konum = fitz.Rect(*veri["konum"])
                
                # Sayfa indeksini kontrol et
                if sayfa >= len(doc):
                    cozulmus_veriler.append({
                        "tip": veri.get("tip", "Bilinmiyor"),
                        "cozulen": f"Çözülemedi: Sayfa bulunamadı ({sayfa})",
                        "hash": "-"
                    })
                    continue
                    
                page = doc[sayfa]
                
                # Fotoğraf kontrolü
                if veri.get("tip") == "Fotograf":
                    # Orijinal makale varsa, görseli orijinal makaleden kopyala
                    if orijinal_doc and sayfa < len(orijinal_doc):
                        orijinal_sayfa = orijinal_doc[sayfa]
                        
                        # Orijinal sayfadan görseli bul 
                        img_list = orijinal_sayfa.get_images(full=True)
                        for img in img_list:
                            # Hata kontrolü
                            try:
                                img_rect = orijinal_sayfa.get_image_rects(img[0])[0]
                                
                                # Konumlar çok yakın mı kontrol et (tamamen aynı değil, yaklaşık)
                                if (abs(img_rect.x0 - konum.x0) < 20 and 
                                    abs(img_rect.y0 - konum.y0) < 20):
                                    
                                    # Görseli çıkar
                                    xref = img[0]
                                    base_image = orijinal_doc.extract_image(xref)
                                    img_bytes = base_image["image"]
                                    
                                    # Deşifre edilmiş dosyaya yerleştir
                                    # Widget silme kodu hata verdiği için atlıyoruz
                                    page.draw_rect(konum, color=(1, 1, 1), fill=(1, 1, 1))  # Eski yeri temizle
                                    
                                    # Görüntüyü ekle
                                    try:
                                        page.insert_image(konum, stream=img_bytes)
                                        cozulmus_veriler.append({
                                            "tip": "Fotograf",
                                            "cozulen": "Yazar fotoğrafı geri yüklendi",
                                            "hash": veri.get("hash", "-")
                                        })
                                    except Exception as img_err:
                                        # Görüntü eklenemezse sadece boş alan bırak
                                        cozulmus_veriler.append({
                                            "tip": "Fotograf",
                                            "cozulen": f"Görüntü eklenemedi: {str(img_err)}",
                                            "hash": veri.get("hash", "-")
                                        })
                                    break
                            except Exception as img_rect_err:
                                # Görüntü dikdörtgeni alınamazsa devam et
                                continue
                                
                        # Eğer görüntü bulunamadıysa bildir
                        if len(img_list) == 0:
                            cozulmus_veriler.append({
                                "tip": "Fotograf",
                                "cozulen": "Orijinal görüntü bulunamadı",
                                "hash": veri.get("hash", "-")
                            })
                else:
                    # Metin deşifreleme
                    sifreli_veri = base64.b64decode(veri["sifreli_veri"])
                    cozulmus = rsa_cipher.decrypt(sifreli_veri).decode(errors="ignore")

                    # Blur alanını beyaza boya
                    page.draw_rect(konum, fill=(1, 1, 1), overlay=True)

                    # Yazının başlangıç noktası: sol üst köşe
                    yaz_x = konum.x0 + 1
                    yaz_y = konum.y1 - 1
                    
                    # Metni doğrudan ekle, font belirtmeden
                    page.insert_text((yaz_x, yaz_y), cozulmus, fontsize=10, color=(0, 0, 0))

                    cozulmus_veriler.append({
                        "tip": veri.get("tip", "Bilinmiyor"),
                        "cozulen": cozulmus,
                        "hash": veri.get("hash", "-")
                    })

            except Exception as e:
                cozulmus_veriler.append({
                    "tip": veri.get("tip", "Bilinmiyor"),
                    "cozulen": f"Çözülemedi: {str(e)}",
                    "hash": "-"
                })
  # 🔓 GÜNCELLENEN KISIM – Hakem değerlendirmesi deşifre işlemi
        degerlendirme_log_path = f"media/degerlendirmeli_pdf/degerlendirme_log_{takip_no}.txt"
        if os.path.exists(degerlendirme_log_path):
            try:
                with open(degerlendirme_log_path, "r", encoding="utf-8") as f:
                    sifreli_degerlendirme = f.read().strip()
                    cozulmus_degerlendirme = rsa_cipher.decrypt(base64.b64decode(sifreli_degerlendirme)).decode("utf-8")

                yeni_sayfa = doc.new_page()
                yeni_sayfa.insert_text((50, 50), "🔓 HAKEM DEĞERLENDİRMESİ (DEŞİFRE EDİLDİ):", fontsize=14, fontname="helv", color=(0, 0, 0))
                y = 80
                for satir in cozulmus_degerlendirme.splitlines():
                    if satir.strip():
                        yeni_sayfa.insert_text((50, y), satir.strip(), fontsize=11, fontname="helv", color=(0, 0, 0))
                        y += 18

                cozulmus_veriler.append({
                    "tip": "Hakem Raporu",
                    "cozulen": "Hakem değerlendirmesi başarıyla deşifre edildi.",
                    "hash": "-"
                })
            except Exception as e:
                cozulmus_veriler.append({
                    "tip": "Hakem Raporu",
                    "cozulen": f"Değerlendirme deşifre edilemedi: {str(e)}",
                    "hash": "-"
                })


        # PDF'i kaydet
        doc.save(desifreli_pdf_path)
        doc.close()
        
        # Orijinal dokümanı kapat
        if orijinal_doc:
            orijinal_doc.close()

    except Exception as e:
        return HttpResponse(f"PDF oluşturulamadı: {e}", status=500)

 

    return render(request, "desifre_sonuc.html", {
        "takip_no": takip_no,
        "veriler": cozulmus_veriler,
        "pdf_url": pdf_url
    })