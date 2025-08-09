from django.db import models

# Makale Modeli
class Makaleler(models.Model):
    STATUS_CHOICES = [
        ('incelemede', 'İncelemede'),
        ('hakemde', 'Hakeme Atandı'),
        ('revizyon', 'Revizyon Bekleniyor'),
        ('yayınlandı', 'Yayınlandı'),
        ('reddedildi', 'Reddedildi'),
    ]

    takip_no = models.CharField(max_length=20, unique=True, verbose_name="Takip Numarası")
    yazar_eposta = models.EmailField(verbose_name="Yazar E-posta")
    orijinal_dosya = models.FileField(upload_to="makaleler/", verbose_name="Orijinal Makale")
    anonim_makale = models.FileField(upload_to="anonim_makaleler/", null=True, blank=True, verbose_name="Anonimleştirilmiş Makale")
    hakem_eposta = models.EmailField(null=True, blank=True, verbose_name="Atanan Hakem E-posta")
    durum = models.CharField(max_length=20, choices=STATUS_CHOICES, default='incelemede', verbose_name="Makale Durumu")
    alan = models.CharField(max_length=50, verbose_name="Atanan Alan", null=True, blank=True)
    yazar_bilgileri = models.TextField(verbose_name="Tespit Edilen Yazarlar", null=True, blank=True)
    kurum_bilgileri = models.TextField(verbose_name="Tespit Edilen Kurumlar", null=True, blank=True)
    
    def __str__(self):
        return f"{self.takip_no} - {self.yazar_eposta} - {self.durum}"
    
# Mesajlaşma Modeli
class Mesaj(models.Model):
    takip_no = models.CharField(max_length=20, verbose_name="Makale Takip Numarası")
    gonderen_eposta = models.EmailField(verbose_name="Gönderen E-posta")
    mesaj = models.TextField(verbose_name="Mesaj İçeriği")
    tarih = models.DateTimeField(auto_now_add=True, verbose_name="Gönderim Tarihi")

    def __str__(self):
        return f"{self.takip_no} - {self.gonderen_eposta}: {self.mesaj[:30]}"

# Hakem Değerlendirme Modeli
class HakemDegerlendirme(models.Model):
    hakem_eposta = models.EmailField(verbose_name="Hakem E-posta")
    anonim_makale = models.FileField(upload_to="hakem_makaleler/", verbose_name="Anonimleştirilmiş Makale")
    degerlendirme = models.TextField(null=True, blank=True, verbose_name="Hakem Değerlendirme")
    aciklama = models.TextField(null=True, blank=True, verbose_name="Ek Açıklama")
    son_hali = models.FileField(upload_to="son_makaleler/", null=True, blank=True, verbose_name="Son Değerlendirme Makalesi")
    ilgi_alanlari = models.CharField(max_length=200)  # Virgül ile ayrılabilir: "Veri Bilimi, Makine Öğrenmesi"

    def __str__(self):
        return f"{self.hakem_eposta} - Değerlendirme"

# Editör Atama Modeli
class EditorAtama(models.Model):
    makale = models.ForeignKey(Makaleler, on_delete=models.CASCADE, verbose_name="Makale")
    editör_eposta = models.EmailField(verbose_name="Editör E-posta")
    hakem_eposta = models.EmailField(verbose_name="Atanan Hakem")
    atama_tarihi = models.DateTimeField(auto_now_add=True, verbose_name="Atama Tarihi")

    def __str__(self):
        return f"{self.makale.takip_no} - {self.hakem_eposta}"
