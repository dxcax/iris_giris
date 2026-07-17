# IrisGuard - İris Tabanlı Biyometrik Kimlik Doğrulama Sistemi

IrisGuard, iris biyometrisini kullanarak kimlik doğrulama gerçekleştiren yapay zekâ destekli bir biyometrik doğrulama sistemidir. Projede, derin öğrenme ve görüntü işleme teknikleri bir araya getirilerek güvenilir ve yüksek doğruluk oranına sahip bir iris tanıma altyapısı geliştirilmiştir.

## Proje Özellikleri

* ResNet18 modeli ile iris görüntülerinden öznitelik çıkarımı
* Sağ ve sol gözün otomatik olarak tespit edilmesi
* İris görüntülerinin kalite analizinin yapılması
* Cosine Similarity yöntemi ile biyometrik eşleştirme
* Kullanıcı dostu Streamlit arayüzü
* Modüler ve geliştirilebilir proje yapısı

## Kullanılan Teknolojiler

* Python
* PyTorch
* OpenCV
* NumPy
* Scikit-learn
* Streamlit

## Veri Seti

Projede **CASIA-Iris-Thousand** veri seti kullanılmıştır. Veri seti yaklaşık **20.000 iris görüntüsü** ve **1.000 farklı kişiye** ait sağ ve sol göz örneklerinden oluşmaktadır.

## Çalışma Akışı

1. İris görüntüsünün sisteme yüklenmesi
2. Görüntünün ön işleme adımlarından geçirilmesi
3. Sağ veya sol göz bilgisinin belirlenmesi
4. ResNet18 modeli ile öznitelik vektörünün oluşturulması
5. Cosine Similarity kullanılarak benzerlik skorunun hesaplanması
6. Kimlik doğrulama kararının verilmesi
7. Sonuçların Streamlit arayüzü üzerinden kullanıcıya sunulması

## Projenin Amacı

Bu projenin amacı, iris biyometrisini kullanarak güvenilir ve yüksek doğrulukta çalışan bir kimlik doğrulama sistemi geliştirmektir. Derin öğrenme tabanlı öznitelik çıkarımı ile biyometrik eşleştirme yöntemlerini bir araya getirerek eğitim ve araştırma amaçlı kullanılabilecek modern bir iris tanıma sistemi ortaya koymaktadır.
