import os
import shutil
import cv2
import numpy as np

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage, QFont, QTextCursor
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QLineEdit, QFileDialog,
    QVBoxLayout, QHBoxLayout, QFrame, QTextEdit, QSizePolicy,
    QScrollArea
)

from mantik.iris_isleme import IrisIsleyici
from mantik.veritabani import VeriTabani


class AnaPencere(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("İris Profili ile Giriş Sistemi")
        self.setMinimumSize(1400, 900)
        self.showMaximized()

        self.iris_isleyici = IrisIsleyici()
        self.veritabani = VeriTabani()

        self.kayit_resim1_yolu = ""
        self.kayit_resim2_yolu = ""
        self.giris_resim_yolu = ""

        self.arayuzu_hazirla()
        self.setStyleSheet("background-color: #0f172a;")
        self.setAutoFillBackground(True)

    def arayuzu_hazirla(self):
        ana_duzen = QHBoxLayout()
        ana_duzen.setContentsMargins(18, 18, 18, 18)
        ana_duzen.setSpacing(18)

        sol_panel = self.kayit_paneli_olustur()
        sag_panel = self.giris_paneli_olustur()

        sol_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sag_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        ana_duzen.addWidget(sol_panel, 1)
        ana_duzen.addWidget(sag_panel, 1)

        self.setLayout(ana_duzen)

    def ortak_stil(self):
        return """
            QWidget {
                background-color: #0f172a;
            }
            QFrame {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 18px;
            }
            QLabel {
                color: #e2e8f0;
                font-size: 14px;
                background-color: transparent;
            }
            QLineEdit, QTextEdit {
                background-color: #020617;
                color: #e2e8f0;
                border: 1px solid #475569;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
                selection-background-color: #6366f1;
                selection-color: white;
            }
            QLineEdit::placeholder {
                color: #94a3b8;
            }
            QPushButton {
                background-color: #6366f1;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4f46e5;
            }
            QScrollBar:vertical {
                background: #020617;
                width: 10px;
                margin: 2px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #6366f1;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #4f46e5;
            }
        """

    def durum_kutusu_stili(self, durum):
        if durum == "basarili":
            return """
                QLabel {
                    background-color: #052e16;
                    color: #bbf7d0;
                    border: 3px solid #22c55e;
                    border-radius: 16px;
                    font-size: 24px;
                    font-weight: bold;
                    padding: 18px;
                }
            """
        if durum == "basarisiz":
            return """
                QLabel {
                    background-color: #450a0a;
                    color: #fecaca;
                    border: 3px solid #ef4444;
                    border-radius: 16px;
                    font-size: 24px;
                    font-weight: bold;
                    padding: 18px;
                }
            """
        if durum == "bilgi":
            return """
                QLabel {
                    background-color: #172554;
                    color: #bfdbfe;
                    border: 3px solid #3b82f6;
                    border-radius: 16px;
                    font-size: 22px;
                    font-weight: bold;
                    padding: 18px;
                }
            """
        return """
            QLabel {
                background-color: #1e293b;
                color: #e2e8f0;
                border: 2px solid #475569;
                border-radius: 16px;
                font-size: 22px;
                font-weight: bold;
                padding: 18px;
            }
        """

    def sonuc_alani_sifirla(self):
        self.sonuc_kutusu.setText("SONUÇ BEKLENİYOR")
        self.sonuc_kutusu.setStyleSheet(self.durum_kutusu_stili("bos"))

        self.detay_baslik.setText("Detaylar")
        self.detay_benzerlik.setText("Benzerlik: -")
        self.detay_mesafe.setText("Mesafe: -")
        self.detay_esik.setText("Eşik: -")
        self.detay_yorum.setText("Durum: Henüz doğrulama yapılmadı.")
        self.detay_dosya1.setText("İris bölgesi: -")
        self.detay_dosya2.setText("Polar görüntü: -")
        self.detay_dosya3.setText("Profil görseli: -")
        self.detay_en_iyi_skor.setText("En iyi skor: -")
        self.detay_agirlikli_skor.setText("Ağırlıklı skor: -")
        self.detay_en_kotu_skor.setText("En kötü skor: -")
        self.detay_agirlikli_mesafe.setText("Ağırlıklı mesafe: -")
        self.detay_en_kotu_mesafe.setText("En kötü mesafe: -")
        self.detay_skor_farki.setText("Skor farkı: -")

    def sonuc_alani_guncelle(
        self,
        durum,
        baslik,
        benzerlik=None,
        mesafe=None,
        esik_yazisi="-",
        yorum="-",
        iris_yolu="-",
        polar_yolu="-",
        profil_yolu="-",
        en_iyi_skor=None,
        agirlikli_skor=None,
        en_kotu_skor=None,
        agirlikli_mesafe=None,
        en_kotu_mesafe=None,
        skor_farki=None
    ):
        ikon = "✅" if durum == "basarili" else "❌" if durum == "basarisiz" else "ℹ️"
        self.sonuc_kutusu.setText(f"{ikon} {baslik}")
        self.sonuc_kutusu.setStyleSheet(self.durum_kutusu_stili(durum))

        self.detay_baslik.setText("Detaylar ve Oranlar")

        self.detay_benzerlik.setText("Benzerlik: -" if benzerlik is None else f"Benzerlik: {benzerlik:.4f}")
        self.detay_mesafe.setText("Mesafe: -" if mesafe is None else f"Mesafe: {mesafe:.4f}")
        self.detay_esik.setText(f"Eşik: {esik_yazisi}")
        self.detay_yorum.setText(f"Durum: {yorum}")
        self.detay_dosya1.setText(f"İris bölgesi: {iris_yolu}")
        self.detay_dosya2.setText(f"Polar görüntü: {polar_yolu}")
        self.detay_dosya3.setText(f"Profil görseli: {profil_yolu}")
        self.detay_en_iyi_skor.setText(
            "En iyi skor: -" if en_iyi_skor is None else f"En iyi skor: {en_iyi_skor:.4f}"
        )
        self.detay_agirlikli_skor.setText(
            "Ağırlıklı skor: -" if agirlikli_skor is None else f"Ağırlıklı skor: {agirlikli_skor:.4f}"
        )
        self.detay_en_kotu_skor.setText(
            "En kötü skor: -" if en_kotu_skor is None else f"En kötü skor: {en_kotu_skor:.4f}"
        )
        self.detay_agirlikli_mesafe.setText(
            "Ağırlıklı mesafe: -" if agirlikli_mesafe is None else f"Ağırlıklı mesafe: {agirlikli_mesafe:.4f}"
        )
        self.detay_en_kotu_mesafe.setText(
            "En kötü mesafe: -" if en_kotu_mesafe is None else f"En kötü mesafe: {en_kotu_mesafe:.4f}"
        )
        self.detay_skor_farki.setText(
            "Skor farkı: -" if skor_farki is None else f"Skor farkı: {skor_farki:.4f}"
        )

    def resim_alani_olustur(self, metin):
        etiket = QLabel(metin)
        etiket.setAlignment(Qt.AlignCenter)
        etiket.setMinimumHeight(170)
        etiket.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        etiket.setStyleSheet(
            "background-color: #020617; border: 1px dashed #475569; border-radius: 12px; color: #94a3b8;"
        )
        return etiket

    def bilgi_satiri_olustur(self, metin):
        etiket = QLabel(metin)
        etiket.setWordWrap(True)
        etiket.setMinimumHeight(34)
        etiket.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        etiket.setStyleSheet("""
            QLabel {
                background-color: #020617;
                border: 1px solid #334155;
                border-radius: 10px;
                padding: 6px 8px;
                font-size: 11px;
                color: #cbd5e1;
            }
        """)
        return etiket

    def kayit_log_yaz(self, mesaj):
        self.kayit_log.append(mesaj)
        self.kayit_log.moveCursor(QTextCursor.End)
        self.kayit_log.ensureCursorVisible()

    def log_yaz(self, mesaj):
        self.giris_log.append(mesaj)
        self.giris_log.moveCursor(QTextCursor.End)
        self.giris_log.ensureCursorVisible()

    def kalite_puani_hesapla(self, sonuc):
        iris_x, iris_y, iris_r = sonuc["iris"]
        pupil_x, pupil_y, pupil_r = sonuc["gozbebegi"]
        maske = sonuc["maske"]
        polar = sonuc["polar"]

        merkez_mesafe = np.sqrt((iris_x - pupil_x) ** 2 + (iris_y - pupil_y) ** 2)
        merkez_orani = float(merkez_mesafe / max(iris_r, 1))
        pupil_iris_orani = float(pupil_r / max(iris_r, 1))
        maske_doluluk = float(np.count_nonzero(maske)) / float(max(maske.size, 1))
        cok_parlak = float(np.mean(polar > 240))
        cok_karanlik = float(np.mean(polar < 15))
        polar_ortalama = float(np.mean(polar))
        polar_std = float(np.std(polar))

        puan = 100.0

        if merkez_orani > 0.18:
            puan -= 20
        elif merkez_orani > 0.12:
            puan -= 10

        if pupil_iris_orani < 0.22 or pupil_iris_orani > 0.58:
            puan -= 20
        elif pupil_iris_orani < 0.26 or pupil_iris_orani > 0.52:
            puan -= 10

        if maske_doluluk < 0.30:
            puan -= 20
        elif maske_doluluk < 0.38:
            puan -= 10

        if cok_parlak > 0.08:
            puan -= 10
        if cok_karanlik > 0.18:
            puan -= 10

        if polar_std < 22:
            puan -= 15
        elif polar_std < 28:
            puan -= 8

        if polar_ortalama < 45 or polar_ortalama > 210:
            puan -= 10

        puan = max(0.0, min(100.0, puan))

        return {
            "puan": puan,
            "merkez_orani": merkez_orani,
            "pupil_iris_orani": pupil_iris_orani,
            "maske_doluluk": maske_doluluk,
            "cok_parlak_orani": cok_parlak,
            "cok_karanlik_orani": cok_karanlik,
            "polar_ortalama": polar_ortalama,
            "polar_std": polar_std
        }

    def kayit_paneli_olustur(self):
        panel = QFrame()
        panel.setStyleSheet(self.ortak_stil())

        duzen = QVBoxLayout()
        duzen.setContentsMargins(20, 20, 20, 20)
        duzen.setSpacing(12)

        baslik = QLabel("Kayıt İşlemi")
        baslik.setFont(QFont("Arial", 16, QFont.Bold))
        baslik.setAlignment(Qt.AlignCenter)

        self.kayit_kullanici = QLineEdit()
        self.kayit_kullanici.setPlaceholderText("Kullanıcı adı giriniz")

        self.kayit_resim1_etiketi = self.resim_alani_olustur("Kayıt fotoğrafı 1 seçilmedi")
        self.kayit_resim2_etiketi = self.resim_alani_olustur("Kayıt fotoğrafı 2 seçilmedi")

        btn1 = QPushButton("Kayıt İçin 1. İris Fotoğrafını Seç")
        btn1.clicked.connect(self.kayit_resim1_sec)

        btn2 = QPushButton("Kayıt İçin 2. İris Fotoğrafını Seç")
        btn2.clicked.connect(self.kayit_resim2_sec)

        btn_kaydet = QPushButton("İris Profilini Oluştur ve Kaydet")
        btn_kaydet.clicked.connect(self.kullanici_kaydet)

        self.kayit_log = QTextEdit()
        self.kayit_log.setReadOnly(True)
        self.kayit_log.setMinimumHeight(300)
        self.kayit_log.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        duzen.addWidget(baslik)
        duzen.addWidget(QLabel("Kullanıcı Adı"))
        duzen.addWidget(self.kayit_kullanici)
        duzen.addWidget(self.kayit_resim1_etiketi)
        duzen.addWidget(btn1)
        duzen.addWidget(self.kayit_resim2_etiketi)
        duzen.addWidget(btn2)
        duzen.addWidget(btn_kaydet)
        duzen.addWidget(QLabel("Kayıt Günlüğü"))
        duzen.addWidget(self.kayit_log, 1)

        panel.setLayout(duzen)
        return panel

    def giris_paneli_olustur(self):
        panel = QFrame()
        panel.setStyleSheet(self.ortak_stil())

        duzen = QVBoxLayout()
        duzen.setContentsMargins(20, 20, 20, 20)
        duzen.setSpacing(8)

        baslik = QLabel("Giriş Doğrulama")
        baslik.setFont(QFont("Arial", 16, QFont.Bold))
        baslik.setAlignment(Qt.AlignCenter)

        self.giris_kullanici = QLineEdit()
        self.giris_kullanici.setPlaceholderText("Kullanıcı adı giriniz")

        self.giris_resim_etiketi = self.resim_alani_olustur("Giriş fotoğrafı seçilmedi")

        btn_sec = QPushButton("Giriş İçin İris Fotoğrafı Seç")
        btn_sec.clicked.connect(self.giris_resmi_sec)

        btn_dogrula = QPushButton("Giriş Doğrulamasını Yap")
        btn_dogrula.clicked.connect(self.giris_dogrula)

        self.sonuc_kutusu = QLabel()
        self.sonuc_kutusu.setAlignment(Qt.AlignCenter)
        self.sonuc_kutusu.setMinimumHeight(76)
        self.sonuc_kutusu.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.detay_baslik = QLabel("Detaylar")
        self.detay_baslik.setFont(QFont("Arial", 11, QFont.Bold))
        self.detay_baslik.setStyleSheet("color: #cbd5e1; padding: 4px 2px 2px 2px; background: transparent;")

        self.detay_benzerlik = self.bilgi_satiri_olustur("Benzerlik: -")
        self.detay_mesafe = self.bilgi_satiri_olustur("Mesafe: -")
        self.detay_en_iyi_skor = self.bilgi_satiri_olustur("En iyi skor: -")
        self.detay_agirlikli_skor = self.bilgi_satiri_olustur("Ağırlıklı skor: -")
        self.detay_en_kotu_skor = self.bilgi_satiri_olustur("En kötü skor: -")
        self.detay_agirlikli_mesafe = self.bilgi_satiri_olustur("Ağırlıklı mesafe: -")
        self.detay_en_kotu_mesafe = self.bilgi_satiri_olustur("En kötü mesafe: -")
        self.detay_skor_farki = self.bilgi_satiri_olustur("Skor farkı: -")
        self.detay_esik = self.bilgi_satiri_olustur("Eşik: -")
        self.detay_yorum = self.bilgi_satiri_olustur("Durum: Henüz doğrulama yapılmadı.")
        self.detay_dosya1 = self.bilgi_satiri_olustur("İris bölgesi: -")
        self.detay_dosya2 = self.bilgi_satiri_olustur("Polar görüntü: -")
        self.detay_dosya3 = self.bilgi_satiri_olustur("Profil görseli: -")

        self.giris_log = QTextEdit()
        self.giris_log.setReadOnly(True)
        self.giris_log.setMinimumHeight(120)
        self.giris_log.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.giris_log.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.sonuc_alani_sifirla()

        detay_icerik = QWidget()
        detay_duzen = QVBoxLayout()
        detay_duzen.setContentsMargins(0, 0, 0, 0)
        detay_duzen.setSpacing(6)
        detay_duzen.addWidget(self.detay_baslik)
        detay_duzen.addWidget(self.detay_benzerlik)
        detay_duzen.addWidget(self.detay_mesafe)
        detay_duzen.addWidget(self.detay_en_iyi_skor)
        detay_duzen.addWidget(self.detay_agirlikli_skor)
        detay_duzen.addWidget(self.detay_en_kotu_skor)
        detay_duzen.addWidget(self.detay_agirlikli_mesafe)
        detay_duzen.addWidget(self.detay_en_kotu_mesafe)
        detay_duzen.addWidget(self.detay_skor_farki)
        detay_duzen.addWidget(self.detay_esik)
        detay_duzen.addWidget(self.detay_yorum)
        detay_duzen.addWidget(self.detay_dosya1)
        detay_duzen.addWidget(self.detay_dosya2)
        detay_duzen.addWidget(self.detay_dosya3)
        detay_icerik.setLayout(detay_duzen)

        detay_scroll = QScrollArea()
        detay_scroll.setWidgetResizable(True)
        detay_scroll.setFrameShape(QFrame.NoFrame)
        detay_scroll.setWidget(detay_icerik)
        detay_scroll.setMinimumHeight(300)
        detay_scroll.setStyleSheet("background: transparent;")

        dogrulama_baslik = QLabel("Doğrulama Günlüğü")
        dogrulama_baslik.setStyleSheet("color: #cbd5e1; padding-top: 4px; background: transparent;")

        duzen.addWidget(baslik)
        duzen.addWidget(QLabel("Kullanıcı Adı"))
        duzen.addWidget(self.giris_kullanici)
        duzen.addWidget(self.giris_resim_etiketi)
        duzen.addWidget(btn_sec)
        duzen.addWidget(btn_dogrula)
        duzen.addWidget(self.sonuc_kutusu)
        duzen.addWidget(detay_scroll, 1)
        duzen.addWidget(dogrulama_baslik)
        duzen.addWidget(self.giris_log, 1)

        panel.setLayout(duzen)
        return panel
    def sonuc_kalite_puani(self, sonuc):
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


    def agirlikli_karar_metrikleri(self, skor1, skor2, mesafe1, mesafe2, kalite1, kalite2):
        agirlik1 = max(0.20, kalite1 / 100.0)
        agirlik2 = max(0.20, kalite2 / 100.0)

        toplam = agirlik1 + agirlik2
        agirlik1 /= toplam
        agirlik2 /= toplam

        agirlikli_skor = skor1 * agirlik1 + skor2 * agirlik2
        agirlikli_mesafe = mesafe1 * agirlik1 + mesafe2 * agirlik2

        return {
            "agirlik1": agirlik1,
            "agirlik2": agirlik2,
            "agirlikli_skor": agirlikli_skor,
            "agirlikli_mesafe": agirlikli_mesafe
        }

    def resim_goster(self, etiket, resim_yolu):
        resim = cv2.imread(resim_yolu)
        if resim is None:
            return

        resim = cv2.cvtColor(resim, cv2.COLOR_BGR2RGB)
        yukseklik, genislik, kanal = resim.shape
        satir_bayt = kanal * genislik

        q_resim = QImage(
            resim.data,
            genislik,
            yukseklik,
            satir_bayt,
            QImage.Format_RGB888
        )

        pixmap = QPixmap.fromImage(q_resim)
        etiket.setPixmap(
            pixmap.scaled(etiket.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

    def kayit_resim1_sec(self):
        dosya_yolu, _ = QFileDialog.getOpenFileName(
            self, "1. iris fotoğrafını seç", "", "Görüntüler (*.png *.jpg *.jpeg *.bmp)"
        )
        if dosya_yolu:
            self.kayit_resim1_yolu = dosya_yolu
            self.resim_goster(self.kayit_resim1_etiketi, dosya_yolu)
            self.kayit_log_yaz(f"1. kayıt fotoğrafı seçildi: {dosya_yolu}")

    def kayit_resim2_sec(self):
        dosya_yolu, _ = QFileDialog.getOpenFileName(
            self, "2. iris fotoğrafını seç", "", "Görüntüler (*.png *.jpg *.jpeg *.bmp)"
        )
        if dosya_yolu:
            self.kayit_resim2_yolu = dosya_yolu
            self.resim_goster(self.kayit_resim2_etiketi, dosya_yolu)
            self.kayit_log_yaz(f"2. kayıt fotoğrafı seçildi: {dosya_yolu}")

    def giris_resmi_sec(self):
        dosya_yolu, _ = QFileDialog.getOpenFileName(
            self, "Giriş iris fotoğrafını seç", "", "Görüntüler (*.png *.jpg *.jpeg *.bmp)"
        )
        if dosya_yolu:
            self.giris_resim_yolu = dosya_yolu
            self.resim_goster(self.giris_resim_etiketi, dosya_yolu)
            self.log_yaz(f"Giriş fotoğrafı seçildi: {dosya_yolu}")
            self.sonuc_alani_sifirla()

    def kullanici_kaydet(self):
        kullanici_adi = self.kayit_kullanici.text().strip()

        if not kullanici_adi:
            self.kayit_log_yaz("Hata: Lütfen kullanıcı adı giriniz.")
            return

        if not self.kayit_resim1_yolu or not self.kayit_resim2_yolu:
            self.kayit_log_yaz("Hata: Lütfen 2 kayıt fotoğrafını da seçiniz.")
            return

        try:
            birlesik_sonuc = self.iris_isleyici.birlesik_profil_olustur(
                self.kayit_resim1_yolu,
                self.kayit_resim2_yolu
            )

            profil = birlesik_sonuc["profil"]

            kayit_klasoru = "veriler/kayitlar"
            analiz_klasoru = os.path.join("veriler", "analizler", kullanici_adi)

            os.makedirs(kayit_klasoru, exist_ok=True)
            os.makedirs(analiz_klasoru, exist_ok=True)

            hedef1 = os.path.join(kayit_klasoru, f"{kullanici_adi}_kayit_1.png")
            hedef2 = os.path.join(kayit_klasoru, f"{kullanici_adi}_kayit_2.png")

            shutil.copy(self.kayit_resim1_yolu, hedef1)
            shutil.copy(self.kayit_resim2_yolu, hedef2)

            self.veritabani.kullanici_kaydet(kullanici_adi, profil, hedef1, hedef2)

            kayit1_dosyalar = self.iris_isleyici.profil_kaydet(
                birlesik_sonuc["sonuc1"], analiz_klasoru, "kayit_1"
            )
            kayit2_dosyalar = self.iris_isleyici.profil_kaydet(
                birlesik_sonuc["sonuc2"], analiz_klasoru, "kayit_2"
            )

            np.save(os.path.join(analiz_klasoru, "birlesik_profil.npy"), profil)
            birlesik_gorsel = self.iris_isleyici.profil_gorseli_olustur(profil)
            cv2.imwrite(os.path.join(analiz_klasoru, "birlesik_profil_gorsel.png"), birlesik_gorsel)

            self.kayit_log_yaz("İris profili başarıyla oluşturuldu.")
            self.kayit_log_yaz(f"Profil boyutu: {len(profil)}")
            self.kayit_log_yaz(f"Kayıt 1 iris bölgesi: {kayit1_dosyalar['iris_yolu']}")
            self.kayit_log_yaz(f"Kayıt 1 polar: {kayit1_dosyalar['polar_yolu']}")
            self.kayit_log_yaz(f"Kayıt 2 iris bölgesi: {kayit2_dosyalar['iris_yolu']}")
            self.kayit_log_yaz(f"Kayıt 2 polar: {kayit2_dosyalar['polar_yolu']}")
            self.kayit_log_yaz(f"Birleşik profil klasörü: {analiz_klasoru}")
            self.kayit_log_yaz("Kullanıcı kaydedildi.")

            self.sonuc_alani_guncelle(
                durum="bilgi",
                baslik="KAYIT TAMAMLANDI",
                esik_yazisi="-",
                yorum="Kayıt başarılı. Şimdi giriş testine geçebilirsin."
            )

        except Exception as hata:
            self.kayit_log_yaz(f"Kayıt hatası: {str(hata)}")
            self.sonuc_alani_guncelle(
                durum="basarisiz",
                baslik="KAYIT HATASI",
                esik_yazisi="-",
                yorum=str(hata)
            )

    def giris_dogrula(self):
        kullanici_adi = self.giris_kullanici.text().strip()

        if not kullanici_adi:
            self.giris_log.append("Hata: Lütfen kullanıcı adı giriniz.")
            return

        if not self.giris_resim_yolu:
            self.giris_log.append("Hata: Lütfen giriş fotoğrafı seçiniz.")
            return

        kayit = self.veritabani.kullanici_getir(kullanici_adi)
        if kayit is None:
            self.giris_log.append("Hata: Bu kullanıcı adına ait kayıt yok.")
            self.sonuc_alani_guncelle(
                durum="basarisiz",
                baslik="KULLANICI BULUNAMADI",
                esik_yazisi="-",
                yorum="Girilen kullanıcı adına ait kayıt bulunamadı."
            )
            return

        try:
            self.giris_log.clear()
            self.giris_log.append("Giriş analizi başlatıldı...")

            giris_sonuc = self.iris_isleyici.iris_profili_cikar(self.giris_resim_yolu)

            kayit1_sonuc = self.iris_isleyici.iris_profili_cikar(kayit["gorsel1"])
            kayit2_sonuc = self.iris_isleyici.iris_profili_cikar(kayit["gorsel2"])

            skor1 = self.iris_isleyici.kaydirmali_karsilastir(
                kayit1_sonuc["polar"],
                giris_sonuc["polar"]
            )

            skor2 = self.iris_isleyici.kaydirmali_karsilastir(
                kayit2_sonuc["polar"],
                giris_sonuc["polar"]
            )

            skor1_deger = skor1["genel_skor"]
            skor2_deger = skor2["genel_skor"]

            mesafe1 = skor1["mesafe"]
            mesafe2 = skor2["mesafe"]

            en_iyi_skor = max(skor1_deger, skor2_deger)
            en_kotu_skor = min(skor1_deger, skor2_deger)

            en_iyi_mesafe = min(mesafe1, mesafe2)
            en_kotu_mesafe = max(mesafe1, mesafe2)

            skor_farki = abs(skor1_deger - skor2_deger)

            if skor1_deger >= skor2_deger:
                kaydirma = skor1["en_iyi_kaydirma"]
                en_iyi_kayit = "kayit_1"
            else:
                kaydirma = skor2["en_iyi_kaydirma"]
                en_iyi_kayit = "kayit_2"

            kalite1 = self.sonuc_kalite_puani(kayit1_sonuc)
            kalite2 = self.sonuc_kalite_puani(kayit2_sonuc)

            agirlikli = self.agirlikli_karar_metrikleri(
                skor1_deger, skor2_deger,
                mesafe1, mesafe2,
                kalite1, kalite2
            )

            agirlikli_skor = agirlikli["agirlikli_skor"]
            agirlikli_mesafe = agirlikli["agirlikli_mesafe"]

            # Aynı kişiyi daha stabil bulur ama başkasını da kolay geçirmez
            karar = (
                en_iyi_skor >= 0.87 and
                agirlikli_skor >= 0.84 and
                en_kotu_skor >= 0.76 and
                agirlikli_mesafe <= 0.47 and
                en_kotu_mesafe <= 0.55 and
                skor_farki <= 0.11
            )

            analiz_klasoru = os.path.join("veriler", "analizler", kullanici_adi, "son_giris")
            os.makedirs(analiz_klasoru, exist_ok=True)

            giris_dosyalar = self.iris_isleyici.profil_kaydet(
                giris_sonuc, analiz_klasoru, "giris"
            )

            kayit1_dosyalar = self.iris_isleyici.profil_kaydet(
                kayit1_sonuc, analiz_klasoru, "karsilastirma_kayit_1"
            )
            kayit2_dosyalar = self.iris_isleyici.profil_kaydet(
                kayit2_sonuc, analiz_klasoru, "karsilastirma_kayit_2"
            )

            en_iyi_kaymis_polar = np.roll(giris_sonuc["polar"], shift=kaydirma, axis=1)
            kaymis_polar_yolu = os.path.join(analiz_klasoru, "giris_en_iyi_kaydirilmis_polar.png")
            cv2.imwrite(kaymis_polar_yolu, en_iyi_kaymis_polar)

            rapor_yolu = os.path.join(analiz_klasoru, "giris_karsilastirma_raporu.txt")
            with open(rapor_yolu, "w", encoding="utf-8") as dosya:
                dosya.write("GİRİŞ KARŞILAŞTIRMA RAPORU\n")
                dosya.write("=" * 55 + "\n")
                dosya.write(f"Kullanıcı: {kullanici_adi}\n")
                dosya.write(f"Giriş fotoğrafı: {self.giris_resim_yolu}\n")
                dosya.write(f"En iyi eşleşen kayıt: {en_iyi_kayit}\n")
                dosya.write(f"Kayıt 1 skor: {skor1_deger:.4f}\n")
                dosya.write(f"Kayıt 2 skor: {skor2_deger:.4f}\n")
                dosya.write(f"Kayıt 1 mesafe: {mesafe1:.4f}\n")
                dosya.write(f"Kayıt 2 mesafe: {mesafe2:.4f}\n")
                dosya.write(f"Kayıt 1 kalite: {kalite1:.2f}\n")
                dosya.write(f"Kayıt 2 kalite: {kalite2:.2f}\n")
                dosya.write(f"Ağırlık 1: {agirlikli['agirlik1']:.4f}\n")
                dosya.write(f"Ağırlık 2: {agirlikli['agirlik2']:.4f}\n")
                dosya.write(f"Ağırlıklı skor: {agirlikli_skor:.4f}\n")
                dosya.write(f"Ağırlıklı mesafe: {agirlikli_mesafe:.4f}\n")
                dosya.write(f"En iyi skor: {en_iyi_skor:.4f}\n")
                dosya.write(f"En kötü skor: {en_kotu_skor:.4f}\n")
                dosya.write(f"En kötü mesafe: {en_kotu_mesafe:.4f}\n")
                dosya.write(f"Skor farkı: {skor_farki:.4f}\n")
                dosya.write(f"En iyi kaydırma: {kaydirma}\n")
                dosya.write(f"Karar: {'KABUL' if karar else 'RED'}\n")

            self.giris_log.append(f"Kayıt 1 skor: {skor1_deger:.4f}")
            self.giris_log.append(f"Kayıt 2 skor: {skor2_deger:.4f}")
            self.giris_log.append(f"Kayıt 1 mesafe: {mesafe1:.4f}")
            self.giris_log.append(f"Kayıt 2 mesafe: {mesafe2:.4f}")
            self.giris_log.append(f"Kayıt 1 kalite: {kalite1:.2f}")
            self.giris_log.append(f"Kayıt 2 kalite: {kalite2:.2f}")
            self.giris_log.append(f"Ağırlık 1: {agirlikli['agirlik1']:.4f}")
            self.giris_log.append(f"Ağırlık 2: {agirlikli['agirlik2']:.4f}")
            self.giris_log.append(f"Ağırlıklı skor: {agirlikli_skor:.4f}")
            self.giris_log.append(f"Ağırlıklı mesafe: {agirlikli_mesafe:.4f}")
            self.giris_log.append(f"En iyi skor: {en_iyi_skor:.4f}")
            self.giris_log.append(f"En kötü skor: {en_kotu_skor:.4f}")
            self.giris_log.append(f"En kötü mesafe: {en_kotu_mesafe:.4f}")
            self.giris_log.append(f"Skor farkı: {skor_farki:.4f}")
            self.giris_log.append(f"En iyi kaydırma: {kaydirma}")
            self.giris_log.append(
                "Kural: en iyi >= 0.87 | ağırlıklı >= 0.84 | en kötü >= 0.76 | "
                "ağırlıklı mesafe <= 0.47 | en kötü mesafe <= 0.55 | fark <= 0.11"
            )
            self.giris_log.append(f"Giriş iris bölgesi: {giris_dosyalar['iris_yolu']}")
            self.giris_log.append(f"Giriş polar: {giris_dosyalar['polar_yolu']}")
            self.giris_log.append(f"Kayıt 1 iris bölgesi: {kayit1_dosyalar['iris_yolu']}")
            self.giris_log.append(f"Kayıt 2 iris bölgesi: {kayit2_dosyalar['iris_yolu']}")
            self.giris_log.append(f"Kaydırılmış polar: {kaymis_polar_yolu}")
            self.giris_log.append(f"Karşılaştırma raporu: {rapor_yolu}")

            if karar:
                yorum = (
                    f"Giriş kabul edildi. En iyi eşleşme {en_iyi_kayit}. "
                    f"Ağırlıklı değerlendirme aynı kişiyi yeterince tutarlı buldu."
                )
                self.giris_log.append("Sonuç: GİRİŞ BAŞARILI")

                self.sonuc_alani_guncelle(
                    durum="basarili",
                    baslik="GİRİŞ BAŞARILI",
                    benzerlik=agirlikli_skor,
                    mesafe=agirlikli_mesafe,
                    esik_yazisi="en iyi >= 0.87 | ağırlıklı >= 0.84 | en kötü >= 0.76 | ağırlıklı mesafe <= 0.47 | en kötü mesafe <= 0.55 | fark <= 0.11",
                    yorum=yorum,
                    iris_yolu=giris_dosyalar["iris_yolu"],
                    polar_yolu=giris_dosyalar["polar_yolu"],
                    profil_yolu=giris_dosyalar["profil_png_yolu"],
                    en_iyi_skor=en_iyi_skor,
                    agirlikli_skor=agirlikli_skor,
                    en_kotu_skor=en_kotu_skor,
                    agirlikli_mesafe=agirlikli_mesafe,
                    en_kotu_mesafe=en_kotu_mesafe,
                    skor_farki=skor_farki
                )
            else:
                yorum = (
                    "Doğrulama reddedildi. En iyi eşleşme tek başına yeterli olsa bile "
                    "iki kayıtla genel tutarlılık yeterli bulunmadı."
                )
                self.giris_log.append("Sonuç: GİRİŞ REDDEDİLDİ")

                self.sonuc_alani_guncelle(
                    durum="basarisiz",
                    baslik="GİRİŞ REDDEDİLDİ",
                    benzerlik=agirlikli_skor,
                    mesafe=agirlikli_mesafe,
                    esik_yazisi="en iyi >= 0.87 | ağırlıklı >= 0.84 | en kötü >= 0.76 | ağırlıklı mesafe <= 0.47 | en kötü mesafe <= 0.55 | fark <= 0.11",
                    yorum=yorum,
                    iris_yolu=giris_dosyalar["iris_yolu"],
                    polar_yolu=giris_dosyalar["polar_yolu"],
                    profil_yolu=giris_dosyalar["profil_png_yolu"],
                    en_iyi_skor=en_iyi_skor,
                    agirlikli_skor=agirlikli_skor,
                    en_kotu_skor=en_kotu_skor,
                    agirlikli_mesafe=agirlikli_mesafe,
                    en_kotu_mesafe=en_kotu_mesafe,
                    skor_farki=skor_farki
                )

        except Exception as hata:
            self.giris_log.append(f"Doğrulama hatası: {str(hata)}")
            self.sonuc_alani_guncelle(
                durum="basarisiz",
                baslik="DOĞRULAMA HATASI",
                esik_yazisi="-",
                yorum=str(hata)
            )
