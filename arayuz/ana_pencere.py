import os
import shutil
import cv2
import numpy as np

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage, QTextCursor
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QLineEdit, QFileDialog,
    QVBoxLayout, QHBoxLayout, QFrame, QTextEdit, QSizePolicy,
    QStackedWidget, QGridLayout
)

from mantik.iris_isleme import IrisIsleyici
from mantik.veritabani import VeriTabani


class AnaPencere(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("IrisGuard | ResNet18 Sağ-Sol İris Doğrulama")
        self.setMinimumSize(1450, 900)
        self.showMaximized()

        self.iris_isleyici = IrisIsleyici()
        self.veritabani = VeriTabani()

        self.kayit_sag_goz_yolu = ""
        self.kayit_sol_goz_yolu = ""
        self.giris_sag_goz_yolu = ""
        self.giris_sol_goz_yolu = ""

        self.stack = QStackedWidget()
        self.menu_btn = {}
        self.metrikler = {}

        self.arayuzu_hazirla()
        self.setStyleSheet(self.stil())

    def stil(self):
        return """
            QWidget {
                background-color: #07111f;
                color: #e5e7eb;
                font-family: Segoe UI;
                font-size: 14px;
            }

            QFrame#sidebar {
                background-color: #0b1628;
                border: none;
                border-right: 1px solid #1e293b;
                border-radius: 0;
            }

            QFrame#pageCard {
                background-color: #0f1b2d;
                border: 1px solid #1e293b;
                border-radius: 24px;
            }

            QFrame#softCard {
                background-color: #101f33;
                border: 1px solid #21324a;
                border-radius: 20px;
            }

            QFrame#metricCard {
                background-color: #0b1628;
                border: 1px solid #1f334d;
                border-radius: 18px;
            }

            QLabel {
                background-color: transparent;
                border: none;
            }

            QLabel#appTitle {
                color: #f8fafc;
                font-size: 26px;
                font-weight: 800;
            }

            QLabel#appSubTitle {
                color: #64748b;
                font-size: 12px;
                font-weight: 600;
            }

            QLabel#pageTitle {
                color: #f8fafc;
                font-size: 28px;
                font-weight: 800;
            }

            QLabel#pageDesc {
                color: #94a3b8;
                font-size: 14px;
            }

            QLabel#sectionTitle {
                color: #f8fafc;
                font-size: 17px;
                font-weight: 700;
            }

            QLabel#fieldLabel {
                color: #cbd5e1;
                font-size: 13px;
                font-weight: 700;
            }

            QLabel#hintText {
                color: #64748b;
                font-size: 12px;
            }

            QLabel#imageBox {
                background-color: #081120;
                border: 1px dashed #334155;
                border-radius: 18px;
                color: #64748b;
                font-size: 13px;
                font-weight: 600;
            }

            QLabel#metricTitle {
                color: #94a3b8;
                font-size: 12px;
                font-weight: 700;
            }

            QLabel#metricValue {
                color: #f8fafc;
                font-size: 22px;
                font-weight: 800;
            }

            QLabel#statusBox {
                background-color: #0b1628;
                color: #e5e7eb;
                border: 1px solid #334155;
                border-radius: 22px;
                font-size: 24px;
                font-weight: 900;
                padding: 22px;
            }

            QLineEdit {
                background-color: #081120;
                color: #f8fafc;
                border: 1px solid #26384f;
                border-radius: 14px;
                padding: 14px 16px;
                font-size: 14px;
                font-weight: 600;
            }

            QLineEdit:focus {
                border: 1px solid #38bdf8;
                background-color: #0b1628;
            }

            QLineEdit::placeholder {
                color: #64748b;
            }

            QTextEdit {
                background-color: #081120;
                color: #cbd5e1;
                border: 1px solid #26384f;
                border-radius: 18px;
                padding: 14px;
                font-family: Consolas;
                font-size: 12px;
            }

            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 14px;
                padding: 13px 16px;
                font-size: 14px;
                font-weight: 800;
            }

            QPushButton:hover {
                background-color: #1d4ed8;
            }

            QPushButton:pressed {
                background-color: #1e40af;
            }

            QPushButton#navButton {
                background-color: transparent;
                color: #94a3b8;
                text-align: left;
                padding: 14px 18px;
                border-radius: 14px;
                font-size: 14px;
                font-weight: 800;
            }

            QPushButton#navButton:hover {
                background-color: #111f35;
                color: #e5e7eb;
            }

            QPushButton#activeNav {
                background-color: #1d4ed8;
                color: white;
                text-align: left;
                padding: 14px 18px;
                border-radius: 14px;
                font-size: 14px;
                font-weight: 800;
            }

            QPushButton#secondary {
                background-color: #111f35;
                color: #cbd5e1;
                border: 1px solid #26384f;
            }

            QPushButton#secondary:hover {
                background-color: #1e293b;
            }

            QPushButton#success {
                background-color: #16a34a;
            }

            QPushButton#success:hover {
                background-color: #15803d;
            }
        """

    def arayuzu_hazirla(self):
        ana = QHBoxLayout()
        ana.setContentsMargins(0, 0, 0, 0)
        ana.setSpacing(0)

        sidebar = self.sidebar_olustur()

        self.stack.addWidget(self.dashboard_sayfasi())
        self.stack.addWidget(self.kayit_sayfasi())
        self.stack.addWidget(self.giris_sayfasi())

        ana.addWidget(sidebar)
        ana.addWidget(self.stack, 1)

        self.setLayout(ana)
        self.sayfa_degistir(0)

    def sidebar_olustur(self):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(280)

        duzen = QVBoxLayout()
        duzen.setContentsMargins(22, 28, 22, 28)
        duzen.setSpacing(12)

        title = QLabel("IrisGuard")
        title.setObjectName("appTitle")

        subtitle = QLabel("Biometric Access Panel")
        subtitle.setObjectName("appSubTitle")

        duzen.addWidget(title)
        duzen.addWidget(subtitle)
        duzen.addSpacing(30)

        self.menu_btn["dashboard"] = self.nav_buton("Dashboard", lambda: self.sayfa_degistir(0))
        self.menu_btn["kayit"] = self.nav_buton("Kullanıcı Kaydı", lambda: self.sayfa_degistir(1))
        self.menu_btn["giris"] = self.nav_buton("Giriş Doğrulama", lambda: self.sayfa_degistir(2))

        duzen.addWidget(self.menu_btn["dashboard"])
        duzen.addWidget(self.menu_btn["kayit"])
        duzen.addWidget(self.menu_btn["giris"])

        duzen.addStretch()

        info = QLabel("Model tabanlı sağ-sol göz kontrolü\nve çift iris doğrulama sistemi.")
        info.setObjectName("hintText")
        info.setWordWrap(True)

        duzen.addWidget(info)

        sidebar.setLayout(duzen)
        return sidebar

    def nav_buton(self, metin, fonksiyon):
        btn = QPushButton(metin)
        btn.setObjectName("navButton")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setMinimumHeight(48)
        btn.clicked.connect(fonksiyon)
        return btn

    def sayfa_degistir(self, index):
        self.stack.setCurrentIndex(index)

        keys = ["dashboard", "kayit", "giris"]
        for i, key in enumerate(keys):
            self.menu_btn[key].setObjectName("activeNav" if i == index else "navButton")
            self.menu_btn[key].style().unpolish(self.menu_btn[key])
            self.menu_btn[key].style().polish(self.menu_btn[key])

    def sayfa_baslik(self, baslik, aciklama):
        alan = QVBoxLayout()
        alan.setSpacing(6)

        title = QLabel(baslik)
        title.setObjectName("pageTitle")

        desc = QLabel(aciklama)
        desc.setObjectName("pageDesc")

        alan.addWidget(title)
        alan.addWidget(desc)

        return alan

    def kart(self, object_name="pageCard"):
        frame = QFrame()
        frame.setObjectName(object_name)
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return frame

    def buton(self, metin, fonksiyon, tip="primary"):
        btn = QPushButton(metin)
        btn.clicked.connect(fonksiyon)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setMinimumHeight(48)

        if tip == "secondary":
            btn.setObjectName("secondary")
        elif tip == "success":
            btn.setObjectName("success")

        return btn

    def dashboard_sayfasi(self):
        sayfa = QWidget()
        ana = QVBoxLayout()
        ana.setContentsMargins(36, 34, 36, 34)
        ana.setSpacing(26)

        ana.addLayout(self.sayfa_baslik(
            "Dashboard",
            "Segmentation, polar normalization, ResNet18 embedding ve sağ-sol göz kontrollü doğrulama paneli."
        ))

        grid = QGridLayout()
        grid.setSpacing(20)

        kart1 = self.dashboard_karti(
            "Kullanıcı Kaydı",
            "Sağ/sol göz yönü kontrol edilir; iris segmentasyonu sonrası ResNet18 embedding profili oluşturulur.",
            "Kayda Git",
            lambda: self.sayfa_degistir(1)
        )

        kart2 = self.dashboard_karti(
            "Giriş Doğrulama",
            "Kayıtlı kullanıcı ResNet18 embedding, cosine similarity ve çapraz göz kontrolüyle test edilir.",
            "Doğrulamaya Git",
            lambda: self.sayfa_degistir(2)
        )

        kart3 = self.dashboard_bilgi_karti()

        grid.addWidget(kart1, 0, 0)
        grid.addWidget(kart2, 0, 1)
        grid.addWidget(kart3, 1, 0, 1, 2)

        ana.addLayout(grid)
        ana.addStretch()

        sayfa.setLayout(ana)
        return sayfa

    def dashboard_karti(self, baslik, aciklama, buton_metni, fonksiyon):
        frame = self.kart("softCard")
        duzen = QVBoxLayout()
        duzen.setContentsMargins(28, 28, 28, 28)
        duzen.setSpacing(14)

        title = QLabel(baslik)
        title.setObjectName("sectionTitle")

        desc = QLabel(aciklama)
        desc.setObjectName("pageDesc")
        desc.setWordWrap(True)

        duzen.addWidget(title)
        duzen.addWidget(desc)
        duzen.addStretch()
        duzen.addWidget(self.buton(buton_metni, fonksiyon, "success"))

        frame.setLayout(duzen)
        return frame

    def dashboard_bilgi_karti(self):
        frame = self.kart("softCard")
        duzen = QVBoxLayout()
        duzen.setContentsMargins(28, 26, 28, 26)
        duzen.setSpacing(10)

        title = QLabel("Sistem Akışı")
        title.setObjectName("sectionTitle")

        desc = QLabel(
            "1. Fotoğraf seçildiğinde model görüntüden sağ/sol göz tahmini yapar.\n"
            "2. Yanlış alana yüklenen göz fotoğrafı kayıt veya girişe alınmaz.\n"
            "3. Girişte sağ-sağ ve sol-sol iris eşleşmesi yapılır.\n"
            "4. Ek olarak çapraz kontrol ile sağ-sol karışıklığı engellenir."
        )
        desc.setStyleSheet("color: #cbd5e1; font-size: 14px; line-height: 1.4;")

        duzen.addWidget(title)
        duzen.addWidget(desc)

        frame.setLayout(duzen)
        return frame

    def kayit_sayfasi(self):
        sayfa = QWidget()
        ana = QVBoxLayout()
        ana.setContentsMargins(36, 34, 36, 34)
        ana.setSpacing(24)

        ana.addLayout(self.sayfa_baslik(
            "Kullanıcı Kaydı",
            "Sağ ve sol göz görsellerini seçerek kullanıcı profili oluştur."
        ))

        govde = QHBoxLayout()
        govde.setSpacing(22)

        form_card = self.kart("pageCard")
        form = QVBoxLayout()
        form.setContentsMargins(28, 28, 28, 28)
        form.setSpacing(15)

        form.addWidget(self.label("Kullanıcı Adı"))
        self.kayit_kullanici = QLineEdit()
        self.kayit_kullanici.setPlaceholderText("Örn: emir")
        form.addWidget(self.kayit_kullanici)

        self.kayit_sag_goz_etiketi = self.resim_alani("Sağ göz görseli bekleniyor")
        self.kayit_sol_goz_etiketi = self.resim_alani("Sol göz görseli bekleniyor")

        form.addWidget(self.kayit_sag_goz_etiketi)
        form.addWidget(self.buton("Sağ Göz Görseli Seç", self.kayit_sag_goz_sec, "secondary"))

        form.addWidget(self.kayit_sol_goz_etiketi)
        form.addWidget(self.buton("Sol Göz Görseli Seç", self.kayit_sol_goz_sec, "secondary"))

        form.addStretch()
        form.addWidget(self.buton("Profili Oluştur ve Kaydet", self.kullanici_kaydet, "success"))

        form_card.setLayout(form)

        log_card = self.log_karti("Kayıt Günlüğü")
        self.kayit_log = log_card["log"]

        govde.addWidget(form_card, 1)
        govde.addWidget(log_card["card"], 1)

        ana.addLayout(govde, 1)
        sayfa.setLayout(ana)
        return sayfa

    def giris_sayfasi(self):
        sayfa = QWidget()
        ana = QVBoxLayout()
        ana.setContentsMargins(36, 34, 36, 34)
        ana.setSpacing(24)

        ana.addLayout(self.sayfa_baslik(
            "Giriş Doğrulama",
            "Kullanıcı adı ve iki göz görseliyle doğrulama işlemini başlat."
        ))

        govde = QHBoxLayout()
        govde.setSpacing(22)

        form_card = self.kart("pageCard")
        form = QVBoxLayout()
        form.setContentsMargins(28, 28, 28, 28)
        form.setSpacing(15)

        form.addWidget(self.label("Kullanıcı Adı"))
        self.giris_kullanici = QLineEdit()
        self.giris_kullanici.setPlaceholderText("Kayıtlı kullanıcı adı")
        form.addWidget(self.giris_kullanici)

        self.giris_sag_goz_etiketi = self.resim_alani("Giriş sağ göz görseli bekleniyor")
        self.giris_sol_goz_etiketi = self.resim_alani("Giriş sol göz görseli bekleniyor")

        form.addWidget(self.giris_sag_goz_etiketi)
        form.addWidget(self.buton("Sağ Göz Görseli Seç", self.giris_sag_goz_sec, "secondary"))

        form.addWidget(self.giris_sol_goz_etiketi)
        form.addWidget(self.buton("Sol Göz Görseli Seç", self.giris_sol_goz_sec, "secondary"))

        form.addStretch()
        form.addWidget(self.buton("Doğrulamayı Başlat", self.giris_dogrula, "success"))

        form_card.setLayout(form)

        sag_panel = QVBoxLayout()
        sag_panel.setSpacing(18)

        self.sonuc_kutusu = QLabel("SONUÇ BEKLENİYOR")
        self.sonuc_kutusu.setObjectName("statusBox")
        self.sonuc_kutusu.setAlignment(Qt.AlignCenter)
        self.sonuc_kutusu.setMinimumHeight(95)

        metric_card = self.kart("pageCard")
        metric_layout = QGridLayout()
        metric_layout.setContentsMargins(22, 22, 22, 22)
        metric_layout.setSpacing(14)

        metrik_adlari = [
            ("Ortalama skor", "0.0000"),
            ("Sağ skor", "0.0000"),
            ("Sol skor", "0.0000"),
            ("Çapraz skor", "0.0000"),
            ("Skor farkı", "0.0000"),
            ("Kalite", "0.00"),
            ("Ortalama mesafe", "0.0000"),
            ("Karar", "-")
        ]

        for i, (ad, deger) in enumerate(metrik_adlari):
            self.metrikler[ad] = self.metrik_karti(ad, deger)
            metric_layout.addWidget(self.metrikler[ad]["card"], i // 3, i % 3)

        metric_card.setLayout(metric_layout)

        log_card = self.log_karti("Doğrulama Günlüğü")
        self.giris_log = log_card["log"]

        sag_panel.addWidget(self.sonuc_kutusu)
        sag_panel.addWidget(metric_card)
        sag_panel.addWidget(log_card["card"], 1)

        govde.addWidget(form_card, 1)
        govde.addLayout(sag_panel, 1)

        ana.addLayout(govde, 1)
        sayfa.setLayout(ana)
        return sayfa

    def label(self, metin):
        lbl = QLabel(metin)
        lbl.setObjectName("fieldLabel")
        return lbl

    def resim_alani(self, metin):
        lbl = QLabel(metin)
        lbl.setObjectName("imageBox")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setMinimumHeight(150)
        lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        return lbl

    def metrik_karti(self, baslik, deger):
        frame = QFrame()
        frame.setObjectName("metricCard")

        duzen = QVBoxLayout()
        duzen.setContentsMargins(16, 14, 16, 14)
        duzen.setSpacing(4)

        title = QLabel(baslik)
        title.setObjectName("metricTitle")

        value = QLabel(deger)
        value.setObjectName("metricValue")

        duzen.addWidget(title)
        duzen.addWidget(value)

        frame.setLayout(duzen)
        return {"card": frame, "value": value}

    def log_karti(self, baslik):
        frame = self.kart("pageCard")

        duzen = QVBoxLayout()
        duzen.setContentsMargins(24, 24, 24, 24)
        duzen.setSpacing(12)

        title = QLabel(baslik)
        title.setObjectName("sectionTitle")

        log = QTextEdit()
        log.setReadOnly(True)

        duzen.addWidget(title)
        duzen.addWidget(log, 1)

        frame.setLayout(duzen)
        return {"card": frame, "log": log}

    def resim_sec(self, baslik, hedef_attr, etiket, log_fonksiyonu, beklenen_yon=None):
        dosya_yolu, _ = QFileDialog.getOpenFileName(
            self,
            baslik,
            "",
            "Görüntüler (*.png *.jpg *.jpeg *.bmp)"
        )

        if not dosya_yolu:
            return

        if beklenen_yon is not None:
            tahmin = self.iris_isleyici.goz_yonu_tahmin_et(dosya_yolu)
            yon = tahmin["yon"]
            guven = tahmin["guven"]

            log_fonksiyonu(f"Göz yönü tahmini: {yon.upper()} | güven: {guven:.2f}")

            if yon == "bilinmiyor":
                log_fonksiyonu("Hata: Göz yönü modeli bulunamadı. Önce modeli eğitmelisin.")
                return

            if guven < 0.35:
                log_fonksiyonu("Hata: Göz yönü tahmini düşük güvenli. Görsel kabul edilmedi.")
                return

            if yon != beklenen_yon:
                log_fonksiyonu(
                    f"Hata: Bu görsel {yon.upper()} göz gibi algılandı. "
                    f"{beklenen_yon.upper()} göz alanına yüklenemez."
                )
                return

        setattr(self, hedef_attr, dosya_yolu)
        self.resim_goster(etiket, dosya_yolu)
        log_fonksiyonu(f"Görsel seçildi: {dosya_yolu}")

    def resim_goster(self, etiket, resim_yolu):
        resim = cv2.imread(resim_yolu)
        if resim is None:
            return

        resim = cv2.cvtColor(resim, cv2.COLOR_BGR2RGB)
        h, w, c = resim.shape

        q_resim = QImage(resim.data, w, h, c * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_resim)

        etiket.setPixmap(
            pixmap.scaled(etiket.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

    def log_yaz(self, alan, mesaj):
        alan.append(mesaj)
        alan.moveCursor(QTextCursor.End)
        alan.ensureCursorVisible()

    def kayit_log_yaz(self, mesaj):
        self.log_yaz(self.kayit_log, mesaj)

    def giris_log_yaz(self, mesaj):
        self.log_yaz(self.giris_log, mesaj)

    def kayit_sag_goz_sec(self):
        self.resim_sec(
            "Kayıt sağ göz görselini seç",
            "kayit_sag_goz_yolu",
            self.kayit_sag_goz_etiketi,
            self.kayit_log_yaz,
            beklenen_yon="sag"
        )

    def kayit_sol_goz_sec(self):
        self.resim_sec(
            "Kayıt sol göz görselini seç",
            "kayit_sol_goz_yolu",
            self.kayit_sol_goz_etiketi,
            self.kayit_log_yaz,
            beklenen_yon="sol"
        )

    def giris_sag_goz_sec(self):
        self.resim_sec(
            "Giriş sağ göz görselini seç",
            "giris_sag_goz_yolu",
            self.giris_sag_goz_etiketi,
            self.giris_log_yaz,
            beklenen_yon="sag"
        )
        self.sonuc_sifirla()

    def giris_sol_goz_sec(self):
        self.resim_sec(
            "Giriş sol göz görselini seç",
            "giris_sol_goz_yolu",
            self.giris_sol_goz_etiketi,
            self.giris_log_yaz,
            beklenen_yon="sol"
        )
        self.sonuc_sifirla()

    def sonuc_sifirla(self):
        self.sonuc_kutusu.setText("SONUÇ BEKLENİYOR")
        self.sonuc_kutusu.setStyleSheet("")

        varsayilan = {
            "Ortalama skor": "0.0000",
            "Sağ skor": "0.0000",
            "Sol skor": "0.0000",
            "Çapraz skor": "0.0000",
            "Skor farkı": "0.0000",
            "Kalite": "0.00",
            "Ortalama mesafe": "0.0000",
            "Karar": "-"
        }

        for key, value in varsayilan.items():
            if key in self.metrikler:
                self.metrikler[key]["value"].setText(value)

    def sonuc_guncelle(self, basarili, metrikler):
        if basarili:
            self.sonuc_kutusu.setText("✅ GİRİŞ BAŞARILI")
            self.sonuc_kutusu.setStyleSheet("""
                QLabel#statusBox {
                    background-color: #052e16;
                    color: #dcfce7;
                    border: 1px solid #22c55e;
                    border-radius: 22px;
                    font-size: 24px;
                    font-weight: 900;
                    padding: 22px;
                }
            """)
        else:
            self.sonuc_kutusu.setText("❌ GİRİŞ REDDEDİLDİ")
            self.sonuc_kutusu.setStyleSheet("""
                QLabel#statusBox {
                    background-color: #450a0a;
                    color: #fee2e2;
                    border: 1px solid #ef4444;
                    border-radius: 22px;
                    font-size: 24px;
                    font-weight: 900;
                    padding: 22px;
                }
            """)

        for key, value in metrikler.items():
            if key in self.metrikler:
                self.metrikler[key]["value"].setText(value)

    def iris_analiz_et(self, resim_yolu, log_fonksiyonu, ad):
        log_fonksiyonu(f"{ad}: segmentation → polar normalize → ResNet18 embedding çıkarılıyor...")
        return self.iris_isleyici.iris_profili_cikar(resim_yolu)

    def analiz_kaydet(self, sonuc, klasor, on_ek):
        return self.iris_isleyici.profil_kaydet(sonuc, klasor, on_ek)

    def kalite_puani(self, sonuc):
        iris_x, iris_y, iris_r = sonuc["iris"]
        pupil_x, pupil_y, pupil_r = sonuc["gozbebegi"]

        merkez_kayma = np.sqrt((iris_x - pupil_x) ** 2 + (iris_y - pupil_y) ** 2)
        merkez_orani = merkez_kayma / max(iris_r, 1)
        oran = pupil_r / max(iris_r, 1)

        puan = 100.0

        if merkez_orani > 0.20:
            puan -= 35
        elif merkez_orani > 0.14:
            puan -= 20
        elif merkez_orani > 0.10:
            puan -= 10

        if oran < 0.22 or oran > 0.60:
            puan -= 25
        elif oran < 0.26 or oran > 0.54:
            puan -= 12

        return max(0.0, min(100.0, puan))

    def kullanici_kaydet(self):
        kullanici_adi = self.kayit_kullanici.text().strip()

        if not kullanici_adi:
            self.kayit_log_yaz("Hata: Kullanıcı adı giriniz.")
            return

        if not self.kayit_sag_goz_yolu or not self.kayit_sol_goz_yolu:
            self.kayit_log_yaz("Hata: Sağ ve sol göz görsellerini seçiniz.")
            return

        try:
            sag_sonuc = self.iris_analiz_et(
                self.kayit_sag_goz_yolu,
                self.kayit_log_yaz,
                "Sağ göz"
            )

            sol_sonuc = self.iris_analiz_et(
                self.kayit_sol_goz_yolu,
                self.kayit_log_yaz,
                "Sol göz"
            )

            kayit_klasoru = "veriler/kayitlar"
            analiz_klasoru = os.path.join("veriler", "analizler", kullanici_adi)

            os.makedirs(kayit_klasoru, exist_ok=True)
            os.makedirs(analiz_klasoru, exist_ok=True)

            sag_hedef = os.path.join(kayit_klasoru, f"{kullanici_adi}_sag_goz.png")
            sol_hedef = os.path.join(kayit_klasoru, f"{kullanici_adi}_sol_goz.png")

            shutil.copy(self.kayit_sag_goz_yolu, sag_hedef)
            shutil.copy(self.kayit_sol_goz_yolu, sol_hedef)

            self.veritabani.kullanici_kaydet(
                kullanici_adi,
                sag_sonuc["profil"],
                sol_sonuc["profil"],
                sag_hedef,
                sol_hedef
            )

            sag_dosyalar = self.analiz_kaydet(sag_sonuc, analiz_klasoru, "kayit_sag_goz")
            sol_dosyalar = self.analiz_kaydet(sol_sonuc, analiz_klasoru, "kayit_sol_goz")

            np.save(os.path.join(analiz_klasoru, "sag_goz_profil.npy"), sag_sonuc["profil"])
            np.save(os.path.join(analiz_klasoru, "sol_goz_profil.npy"), sol_sonuc["profil"])

            self.kayit_log_yaz("Kayıt tamamlandı.")
            self.kayit_log_yaz(f"Sağ iris çıktısı: {sag_dosyalar['iris_yolu']}")
            self.kayit_log_yaz(f"Sol iris çıktısı: {sol_dosyalar['iris_yolu']}")
            self.kayit_log_yaz(f"Analiz klasörü: {analiz_klasoru}")

        except Exception as hata:
            self.kayit_log_yaz(f"Kayıt hatası: {str(hata)}")

    def goz_karsilastir(self, kayit_yolu, giris_yolu, goz_adi):
        kayit_sonuc = self.iris_analiz_et(
            kayit_yolu,
            self.giris_log_yaz,
            f"Kayıt {goz_adi}"
        )

        giris_sonuc = self.iris_analiz_et(
            giris_yolu,
            self.giris_log_yaz,
            f"Giriş {goz_adi}"
        )

        karsilastirma = self.iris_isleyici.kaydirmali_karsilastir(
            kayit_sonuc["polar"],
            giris_sonuc["polar"]
        )

        return {
            "kayit_sonuc": kayit_sonuc,
            "giris_sonuc": giris_sonuc,
            "skor": karsilastirma["genel_skor"],
            "mesafe": karsilastirma["mesafe"],
            "kosinus": karsilastirma["kosinus"],
            "korelasyon": karsilastirma["korelasyon"],
            "kaydirma": karsilastirma["en_iyi_kaydirma"],
            "kalite": self.kalite_puani(giris_sonuc)
        }

    def karar_ver(self, sag, sol, capraz_sag, capraz_sol):
        ortalama_skor = (sag["skor"] + sol["skor"]) / 2.0
        ortalama_mesafe = (sag["mesafe"] + sol["mesafe"]) / 2.0
        skor_farki = abs(sag["skor"] - sol["skor"])

        capraz_sag_skor = capraz_sag["genel_skor"]
        capraz_sol_skor = capraz_sol["genel_skor"]
        capraz_en_yuksek = max(capraz_sag_skor, capraz_sol_skor)

        sag_kalite = sag["kalite"]
        sol_kalite = sol["kalite"]
        ortalama_kalite = (sag_kalite + sol_kalite) / 2.0

        capraz_margin = 0.04
        capraz_supheli = (
            capraz_sag_skor > sag["skor"] + capraz_margin and
            capraz_sol_skor > sol["skor"] + capraz_margin
        )

        kalite_cok_kotu = (
            sag_kalite < 45 or
            sol_kalite < 45 or
            ortalama_kalite < 50
        )

        orta_kalite = (
            not kalite_cok_kotu and
            (
                sag_kalite < 65 or
                sol_kalite < 65 or
                ortalama_kalite < 65
            )
        )

        if orta_kalite:
            min_goz_skoru = 0.84
            min_ortalama_skor = 0.86
            max_goz_mesafe = 0.50
            max_ortalama_mesafe = 0.46
            max_skor_farki = 0.14
        else:
            min_goz_skoru = 0.80
            min_ortalama_skor = 0.81
            max_goz_mesafe = 0.55
            max_ortalama_mesafe = 0.52
            max_skor_farki = 0.16

        karar = (
            sag["skor"] >= min_goz_skoru and
            sol["skor"] >= min_goz_skoru and
            ortalama_skor >= min_ortalama_skor and
            sag["mesafe"] <= max_goz_mesafe and
            sol["mesafe"] <= max_goz_mesafe and
            ortalama_mesafe <= max_ortalama_mesafe and
            skor_farki <= max_skor_farki and
            not capraz_supheli and
            not kalite_cok_kotu
        )

        red_nedenleri = []

        if sag["skor"] < min_goz_skoru:
            red_nedenleri.append(
                f"Sağ göz skoru düşük: {sag['skor']:.4f} < {min_goz_skoru:.2f}"
            )

        if sol["skor"] < min_goz_skoru:
            red_nedenleri.append(
                f"Sol göz skoru düşük: {sol['skor']:.4f} < {min_goz_skoru:.2f}"
            )

        if ortalama_skor < min_ortalama_skor:
            red_nedenleri.append(
                f"Ortalama skor düşük: {ortalama_skor:.4f} < {min_ortalama_skor:.2f}"
            )

        if sag["mesafe"] > max_goz_mesafe:
            red_nedenleri.append(
                f"Sağ göz mesafesi yüksek: {sag['mesafe']:.4f} > {max_goz_mesafe:.2f}"
            )

        if sol["mesafe"] > max_goz_mesafe:
            red_nedenleri.append(
                f"Sol göz mesafesi yüksek: {sol['mesafe']:.4f} > {max_goz_mesafe:.2f}"
            )

        if ortalama_mesafe > max_ortalama_mesafe:
            red_nedenleri.append(
                f"Ortalama mesafe yüksek: {ortalama_mesafe:.4f} > {max_ortalama_mesafe:.2f}"
            )

        if skor_farki > max_skor_farki:
            red_nedenleri.append(
                f"Sağ-sol skor farkı yüksek: {skor_farki:.4f} > {max_skor_farki:.2f}"
            )

        if capraz_supheli:
            red_nedenleri.append("Çapraz kontrol şüpheli: sağ-sol göz karışmış olabilir.")

        if kalite_cok_kotu:
            red_nedenleri.append("Görüntü kalitesi çok düşük.")

        return karar, {
            "ortalama_skor": ortalama_skor,
            "ortalama_mesafe": ortalama_mesafe,
            "skor_farki": skor_farki,
            "capraz_sag_skor": capraz_sag_skor,
            "capraz_sol_skor": capraz_sol_skor,
            "capraz_en_yuksek": capraz_en_yuksek,
            "capraz_supheli": capraz_supheli,
            "sag_kalite": sag_kalite,
            "sol_kalite": sol_kalite,
            "ortalama_kalite": ortalama_kalite,
            "kalite_cok_kotu": kalite_cok_kotu,
            "orta_kalite": orta_kalite,
            "red_nedenleri": red_nedenleri
        }

    def rapor_yaz(self, klasor, kullanici_adi, sag, sol, karar, metrikler):
        rapor_yolu = os.path.join(klasor, "sag_sol_giris_karsilastirma_raporu.txt")

        with open(rapor_yolu, "w", encoding="utf-8") as dosya:
            dosya.write("SAĞ-SOL GİRİŞ KARŞILAŞTIRMA RAPORU\n")
            dosya.write("=" * 60 + "\n")
            dosya.write(f"Kullanıcı: {kullanici_adi}\n\n")

            for ad, veri in [("SAĞ GÖZ", sag), ("SOL GÖZ", sol)]:
                dosya.write(f"{ad}\n")
                dosya.write("-" * 30 + "\n")
                dosya.write(f"Skor: {veri['skor']:.4f}\n")
                dosya.write(f"Mesafe: {veri['mesafe']:.4f}\n")
                dosya.write(f"Kosinüs: {veri['kosinus']:.4f}\n")
                dosya.write(f"Korelasyon: {veri['korelasyon']:.4f}\n")
                dosya.write(f"Kalite: {veri['kalite']:.2f}\n\n")

            dosya.write("ÇAPRAZ KONTROL\n")
            dosya.write("-" * 30 + "\n")
            dosya.write(f"Çapraz sağ skor: {metrikler['capraz_sag_skor']:.4f}\n")
            dosya.write(f"Çapraz sol skor: {metrikler['capraz_sol_skor']:.4f}\n")
            dosya.write(f"Çapraz en yüksek: {metrikler['capraz_en_yuksek']:.4f}\n")
            dosya.write(f"Çapraz şüpheli: {metrikler['capraz_supheli']}\n\n")

            dosya.write("GENEL KARAR\n")
            dosya.write("-" * 30 + "\n")
            dosya.write(f"Ortalama skor: {metrikler['ortalama_skor']:.4f}\n")
            dosya.write(f"Ortalama mesafe: {metrikler['ortalama_mesafe']:.4f}\n")
            dosya.write(f"Skor farkı: {metrikler['skor_farki']:.4f}\n")
            dosya.write(f"Sağ kalite: {metrikler.get('sag_kalite', 0):.2f}\n")
            dosya.write(f"Sol kalite: {metrikler.get('sol_kalite', 0):.2f}\n")
            dosya.write(f"Ortalama kalite: {metrikler.get('ortalama_kalite', 0):.2f}\n")
            dosya.write(f"Orta kalite modu: {metrikler.get('orta_kalite', False)}\n")
            dosya.write(f"Kalite çok kötü: {metrikler.get('kalite_cok_kotu', False)}\n")
            dosya.write(f"Karar: {'KABUL' if karar else 'RED'}\n")

            if metrikler.get("red_nedenleri"):
                dosya.write("\nRED NEDENLERİ\n")
                dosya.write("-" * 30 + "\n")
                for neden in metrikler["red_nedenleri"]:
                    dosya.write(f"- {neden}\n")

        return rapor_yolu

    def giris_dogrula(self):
        kullanici_adi = self.giris_kullanici.text().strip()

        if not kullanici_adi:
            self.giris_log_yaz("Hata: Kullanıcı adı giriniz.")
            return

        if not self.giris_sag_goz_yolu or not self.giris_sol_goz_yolu:
            self.giris_log_yaz("Hata: Sağ ve sol giriş görsellerini seçiniz.")
            return

        kayit = self.veritabani.kullanici_getir(kullanici_adi)

        if kayit is None:
            self.sonuc_kutusu.setText("❌ KULLANICI BULUNAMADI")
            return

        try:
            self.giris_log.clear()
            self.giris_log_yaz("Doğrulama başlatıldı...")

            sag = self.goz_karsilastir(
                kayit["sag_gorsel"],
                self.giris_sag_goz_yolu,
                "sağ göz"
            )

            sol = self.goz_karsilastir(
                kayit["sol_gorsel"],
                self.giris_sol_goz_yolu,
                "sol göz"
            )

            capraz_sag = self.iris_isleyici.kaydirmali_karsilastir(
                sol["kayit_sonuc"]["polar"],
                sag["giris_sonuc"]["polar"]
            )

            capraz_sol = self.iris_isleyici.kaydirmali_karsilastir(
                sag["kayit_sonuc"]["polar"],
                sol["giris_sonuc"]["polar"]
            )

            karar, metrikler = self.karar_ver(sag, sol, capraz_sag, capraz_sol)

            analiz_klasoru = os.path.join(
                "veriler",
                "analizler",
                kullanici_adi,
                "son_giris_sag_sol"
            )
            os.makedirs(analiz_klasoru, exist_ok=True)

            self.analiz_kaydet(sag["giris_sonuc"], analiz_klasoru, "giris_sag_goz")
            self.analiz_kaydet(sol["giris_sonuc"], analiz_klasoru, "giris_sol_goz")
            self.analiz_kaydet(sag["kayit_sonuc"], analiz_klasoru, "kayit_sag_goz")
            self.analiz_kaydet(sol["kayit_sonuc"], analiz_klasoru, "kayit_sol_goz")

            rapor_yolu = self.rapor_yaz(
                analiz_klasoru,
                kullanici_adi,
                sag,
                sol,
                karar,
                metrikler
            )

            self.sonuc_guncelle(
                karar,
                {
                    "Ortalama skor": f"{metrikler['ortalama_skor']:.4f}",
                    "Sağ skor": f"{sag['skor']:.4f}",
                    "Sol skor": f"{sol['skor']:.4f}",
                    "Çapraz skor": f"{metrikler['capraz_en_yuksek']:.4f}",
                    "Skor farkı": f"{metrikler['skor_farki']:.4f}",
                    "Kalite": f"{metrikler['ortalama_kalite']:.2f}",
                    "Ortalama mesafe": f"{metrikler['ortalama_mesafe']:.4f}",
                    "Karar": "KABUL" if karar else "RED"
                }
            )

            self.giris_log_yaz(f"Sağ skor: {sag['skor']:.4f}")
            self.giris_log_yaz(f"Sol skor: {sol['skor']:.4f}")
            self.giris_log_yaz(f"Ortalama skor: {metrikler['ortalama_skor']:.4f}")
            self.giris_log_yaz(f"Çapraz sağ skor: {metrikler['capraz_sag_skor']:.4f}")
            self.giris_log_yaz(f"Çapraz sol skor: {metrikler['capraz_sol_skor']:.4f}")

            self.giris_log_yaz(f"Sağ kalite: {metrikler['sag_kalite']:.2f}")
            self.giris_log_yaz(f"Sol kalite: {metrikler['sol_kalite']:.2f}")
            self.giris_log_yaz(f"Ortalama kalite: {metrikler['ortalama_kalite']:.2f}")

            if metrikler["kalite_cok_kotu"]:
                self.giris_log_yaz("Uyarı: Görüntü kalitesi çok düşük. İris bölgesi güvenilir değil.")

            if metrikler["orta_kalite"]:
                self.giris_log_yaz("Bilgi: Görüntü orta kalite. Eşikler biraz sıkılaştırıldı.")

            if metrikler["capraz_supheli"]:
                self.giris_log_yaz("Uyarı: Sağ-sol göz karışmış olabilir. Çapraz eşleşme şüpheli.")

            if not karar:
                for neden in metrikler["red_nedenleri"]:
                    self.giris_log_yaz(f"Red nedeni: {neden}")

            self.giris_log_yaz(f"Rapor: {rapor_yolu}")

        except Exception as hata:
            self.giris_log_yaz(f"Doğrulama hatası: {str(hata)}")