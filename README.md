# secure-document-anonymizer
🛡 Güvenli Belge Anonimleştirme Sistemi
Bu proje, akademik makale yükleme ve değerlendirme sürecini güvenli, anonim ve şeffaf bir şekilde yönetmek amacıyla geliştirilmiş web tabanlı bir sistemdir.
Yazarlar makalelerini yükleyebilir, editörler anonimleştirme işlemlerini yapabilir ve hakemler anonim olarak değerlendirme yapabilir.

🚀 Teknolojiler
Backend: Python (Django)

Frontend: HTML, CSS, JavaScript

Veritabanı: MySQL

Şifreleme: RSA (asimetrik şifreleme), SHA-256 (hashleme)

Anonimleştirme: Regex, NER (Named Entity Recognition)

👥 Kullanıcı Roller ve Özellikler
🖊 Yazar
Üye olmadan PDF formatında makale yükleyebilir.

Geçerli e-posta adresi girmek zorundadır.

Makale yükleme sonrası benzersiz bir makale takip numarası alır.

Editöre mesaj gönderebilir, değerlendirme sürecini takip edebilir.

Sonuç ve hakem geri bildirimlerini alabilir.

Gerekirse revize edilmiş makaleyi tekrar yükleyebilir.

🛠 Editör (Yönetici)
Tüm makaleleri görüntüleyebilir ve anahtar kelimelere göre alan ataması yapabilir.

Makale içerisindeki yazar/kurum bilgilerini otomatik tespit eder.

Anonimleştirilecek bilgileri seçer ve düzenler.

Anonimleştirilmiş makaleyi hakeme iletir.

Hakem değerlendirmelerini alır, yazar bilgilerini geri yükleyerek sonucu yazara iletir.

Log kayıtlarını inceleyebilir (yükleme tarihi, atama, değerlendirme vb.).

📄 Hakem (Değerlendirici)
Kendisine atanan anonimleştirilmiş makaleyi inceleyip değerlendirme yapar.

Değerlendirmesini sisteme yükler, gerekirse ek açıklama ekler.

🔐 Güvenlik ve Anonimlik
RSA: Makale verilerinin güvenli şekilde iletilmesi için asimetrik şifreleme yöntemi.

SHA-256: E-posta ve dosya bütünlüğü kontrolü için güçlü hash algoritması.

Yazar adı-soyadı, iletişim bilgileri ve kurum bilgileri anonimleştirilir.

Anonimleştirilmiş görüntüler bulanıklaştırılır (blur).

Kurum bilgileri yalnızca bağlama göre anonimleştirilir, gereksiz sansür önlenir.

Hakem, yazar bilgilerini asla göremez.

Editör, hakem değerlendirmelerini değiştiremez.

📌 Önemli Notlar
Hazır yapay zeka API’leri anonimleştirme için kullanılmaz (sadece arayüz puanı alınır).

“Giriş”, “İlgili Çalışmalar”, “Referanslar” ve “Teşekkür” bölümleri yazar isimleri içerdiğinden özel işlem yapılır.

Her makale sadece bir hakeme atanır.

Giriş kontrolü (login) yoktur; demo esnasında şifre ekranı olmayacak.

🗂 Örnek İş Akışı
Yazar makaleyi PDF formatında yükler.

Sistem PDF içeriğini tarar, yazar/kurum bilgilerini tespit eder.

Editör anonimleştirilecek alanları seçer.

Anonimleştirilmiş makale hakeme iletilir.

Hakem değerlendirme yapar ve sisteme yükler.

Editör yazar bilgilerini geri yükleyerek sonucu yazara iletir.

