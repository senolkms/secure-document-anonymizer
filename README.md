# 🛡 Güvenli Belge Anonimleştirme Sistemi

Bu proje, **akademik makale yükleme, anonimleştirme ve değerlendirme sürecini güvenli bir şekilde yönetmek** amacıyla geliştirilmiş bir **web tabanlı sistemdir**.  
Yazarlar makalelerini yükleyebilir, editörler anonimleştirme işlemlerini yapabilir, hakemler ise anonim şekilde değerlendirme yapabilir.  

🛠 **Backend:** Python-Django  
🗄 **Veritabanı:** MySQL  
🎨 **Frontend:** HTML, CSS, JavaScript, Bootstrap  
🔐 **Güvenlik:** RSA, SHA-256, HTTPS  

---

## 📌 Özellikler

### 🖊 Yazar İşlemleri
- Üye olmadan PDF formatında makale yükleme  
- Geçerli e-posta ile kayıt  
- Makale takip numarası ile durum sorgulama  
- Editöre mesaj gönderme  
- Revize edilmiş makale yükleme  

### 🛠 Editör (Yönetici) İşlemleri
- Yüklenen makaleleri görüntüleme  
- Anahtar kelimelere göre alan atama  
- Yazar/kurum bilgilerini tespit etme (Regex, NER)  
- Anonimleştirme ve düzenleme  
- Hakem ataması yapma  
- Hakem değerlendirmelerini yazara iletme  
- Log kayıtlarını görüntüleme  

### 📄 Hakem (Değerlendirici) İşlemleri
- Kendisine atanan anonimleştirilmiş makaleyi görüntüleme  
- Değerlendirme raporu oluşturma  
- Ek açıklama ekleme  

---

## 🔐 Güvenlik & Anonimlik
- **RSA** ile güvenli veri iletimi  
- **SHA-256** ile veri bütünlüğü kontrolü  
- Görsellerde blur anonimleştirme  
- Bağlam kontrollü anonimleştirme (gereksiz sansürden kaçınma)  
- Editör tarafından hakem yorumlarının değiştirilememesi  

---

## 📂 Veritabanı Tasarımı
Bu proje ilişkisel bir veritabanı modeline sahiptir ve **1NF, 2NF, 3NF normalizasyon kurallarına** uygundur.

---

## 🖥 Kullanıcı Arayüzü (GUI)
- 📌 **Makale Yükleme Sayfası:** PDF yükleme, e-posta doğrulama  
- 📋 **Durum Sorgulama Paneli:** Makale takip numarası ile durum görüntüleme  
- 🔍 **Editör Paneli:** Anonimleştirme, hakem atama, log inceleme  
- 📝 **Hakem Paneli:** Değerlendirme raporu oluşturma  

💡 **Dinamik Bileşenler:**  
✔ **Regex & NER** – Otomatik bilgi tespiti  
✔ **Blur Görüntü İşleme** – Yazar görsellerinin anonimleştirilmesi  
✔ **Log Sistemi** – Tüm işlem geçmişinin kaydı  
