import os
import cv2
import joblib
import numpy as np
from skimage.feature import local_binary_pattern, hog


class IrisIsleyici:
    def __init__(self):
        pass

    def resmi_yukle(self, resim_yolu):
        gri = cv2.imread(resim_yolu, cv2.IMREAD_GRAYSCALE)
        if gri is None:
            raise ValueError("Görüntü okunamadı.")
        return gri

    def on_isle(self, gri):
        gri = cv2.resize(gri, (640, 480))
        gri = cv2.bilateralFilter(gri, 7, 35, 35)

        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gri = clahe.apply(gri)

        gri = cv2.GaussianBlur(gri, (5, 5), 0)
        return gri

    def goz_yonu_ozellik_cikar(self, resim_yolu):
        gri = cv2.imread(resim_yolu, cv2.IMREAD_GRAYSCALE)

        if gri is None:
            raise ValueError("Görüntü okunamadı.")

        gri = cv2.resize(gri, (160, 80))

        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gri = clahe.apply(gri)
        gri = cv2.GaussianBlur(gri, (3, 3), 0)

        hog_ozellik = hog(
            gri,
            orientations=9,
            pixels_per_cell=(8, 8),
            cells_per_block=(2, 2),
            block_norm="L2-Hys",
            feature_vector=True
        )

        sol_yari = gri[:, :80]
        sag_yari = gri[:, 80:]

        kenar = cv2.Canny(gri, 60, 140)
        sol_kenar = kenar[:, :80]
        sag_kenar = kenar[:, 80:]

        ekstra = np.array([
            np.mean(sol_yari),
            np.mean(sag_yari),
            np.std(sol_yari),
            np.std(sag_yari),
            np.mean(sol_kenar),
            np.mean(sag_kenar),
            np.std(sol_kenar),
            np.std(sag_kenar),
        ], dtype=np.float32)

        return np.concatenate([hog_ozellik, ekstra]).astype(np.float32)

    def goz_yonu_tahmin_et(self, resim_yolu, model_yolu="veriler/goz_yonu_model.pkl"):
        if not os.path.exists(model_yolu):
            return {
                "yon": "bilinmiyor",
                "guven": 0.0,
                "mesaj": "Göz yönü modeli bulunamadı."
            }

        model = joblib.load(model_yolu)
        ozellik = self.goz_yonu_ozellik_cikar(resim_yolu).reshape(1, -1)

        tahmin = model.predict(ozellik)[0]

        guven = 1.0
        try:
            skor = model.decision_function(ozellik)
            skor_degeri = float(np.max(np.abs(skor)))
            guven = min(1.0, skor_degeri / 2.5)
        except Exception:
            guven = 1.0

        return {
            "yon": tahmin,
            "guven": guven,
            "mesaj": "Tahmin başarılı."
        }

    def gozbebegi_bul(self, gri):
        h, w = gri.shape

        x1 = int(w * 0.18)
        x2 = int(w * 0.82)
        y1 = int(h * 0.18)
        y2 = int(h * 0.82)

        roi = gri[y1:y2, x1:x2].copy()
        roi = cv2.medianBlur(roi, 5)

        daireler = cv2.HoughCircles(
            roi,
            cv2.HOUGH_GRADIENT,
            dp=1.2,
            minDist=70,
            param1=80,
            param2=18,
            minRadius=18,
            maxRadius=58
        )

        if daireler is None:
            raise ValueError("Göz bebeği bulunamadı.")

        daireler = np.round(daireler[0]).astype(int)

        roi_h, roi_w = roi.shape
        roi_merkez_x = roi_w // 2
        roi_merkez_y = roi_h // 2

        en_iyi = None
        en_iyi_skor = float("inf")

        for x, y, r in daireler:
            tam_x = x + x1
            tam_y = y + y1

            if tam_x - r < 0 or tam_y - r < 0 or tam_x + r >= w or tam_y + r >= h:
                continue

            maske = np.zeros_like(gri, dtype=np.uint8)
            cv2.circle(maske, (tam_x, tam_y), r, 255, -1)

            ortalama = cv2.mean(gri, mask=maske)[0]
            if ortalama > 110:
                continue

            merkez_uzaklik = np.sqrt((x - roi_merkez_x) ** 2 + (y - roi_merkez_y) ** 2)
            yaricap_cezasi = abs(r - 30)

            skor = ortalama * 2.4 + merkez_uzaklik * 0.35 + yaricap_cezasi * 2.8

            if skor < en_iyi_skor:
                en_iyi_skor = skor
                en_iyi = (tam_x, tam_y, r)

        if en_iyi is None:
            raise ValueError("Geçerli göz bebeği bulunamadı.")

        return en_iyi

    def dairesel_kenar_skoru(self, gri, merkez_x, merkez_y, yaricap):
        gx = cv2.Sobel(gri, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(gri, cv2.CV_32F, 0, 1, ksize=3)
        gradyan = cv2.magnitude(gx, gy)

        acilar = np.linspace(0, 2 * np.pi, 240, endpoint=False)
        skorlar = []

        for aci in acilar:
            sin_deger = abs(np.sin(aci))
            aci_agirligi = 1.0 - 0.65 * sin_deger

            x = int(merkez_x + yaricap * np.cos(aci))
            y = int(merkez_y + yaricap * np.sin(aci))

            if 0 <= x < gri.shape[1] and 0 <= y < gri.shape[0]:
                skorlar.append(gradyan[y, x] * aci_agirligi)

        if not skorlar:
            return 0.0

        return float(np.mean(skorlar))

    def halka_kontrast_skoru(self, gri, merkez_x, merkez_y, yaricap):
        ic_maske = np.zeros_like(gri, dtype=np.uint8)
        dis_maske = np.zeros_like(gri, dtype=np.uint8)

        cv2.circle(ic_maske, (merkez_x, merkez_y), max(yaricap - 5, 1), 255, 2)
        cv2.circle(dis_maske, (merkez_x, merkez_y), yaricap + 5, 255, 2)

        ic_ortalama = cv2.mean(gri, mask=ic_maske)[0]
        dis_ortalama = cv2.mean(gri, mask=dis_maske)[0]

        return float(abs(dis_ortalama - ic_ortalama))

    def iris_bul(self, gri, gozbebegi):
        gx, gy, gr = gozbebegi

        min_r = int(gr * 2.0)
        max_r = int(gr * 3.8)

        max_izinli = min(
            gx - 8,
            gy - 8,
            gri.shape[1] - gx - 8,
            gri.shape[0] - gy - 8
        )
        max_izinli = max(20, max_izinli)
        max_r = min(max_r, max_izinli)

        if min_r >= max_r:
            varsayilan_r = int(gr * 2.6)
            varsayilan_r = min(varsayilan_r, max_izinli)

            if varsayilan_r <= gr + 8:
                raise ValueError("İris sınırı bulunamadı.")

            return gx, gy, varsayilan_r

        en_iyi_r = None
        en_iyi_skor = -1.0

        for r in range(min_r, max_r + 1):
            kenar_skor = self.dairesel_kenar_skoru(gri, gx, gy, r)
            kontrast_skor = self.halka_kontrast_skoru(gri, gx, gy, r)

            kucuk_ceza = 0.0
            if r < gr * 2.3:
                kucuk_ceza = (gr * 2.3 - r) * 1.8

            toplam_skor = 0.82 * kenar_skor + 0.18 * kontrast_skor - kucuk_ceza

            if toplam_skor > en_iyi_skor:
                en_iyi_skor = toplam_skor
                en_iyi_r = r

        if en_iyi_r is None:
            raise ValueError("İris sınırı bulunamadı.")

        return gx, gy, en_iyi_r

    def iris_halkasi_cikar(self, gri, iris, gozbebegi):
        ix, iy, ir = iris
        px, py, pr = gozbebegi

        x1 = max(ix - ir, 0)
        y1 = max(iy - ir, 0)
        x2 = min(ix + ir, gri.shape[1])
        y2 = min(iy + ir, gri.shape[0])

        kirpilmis_gri = gri[y1:y2, x1:x2]

        if kirpilmis_gri.size == 0:
            raise ValueError("İris bölgesi kırpılamadı.")

        yeni_ix = ix - x1
        yeni_iy = iy - y1
        yeni_px = px - x1
        yeni_py = py - y1

        maske = np.zeros_like(kirpilmis_gri, dtype=np.uint8)
        cv2.circle(maske, (yeni_ix, yeni_iy), ir, 255, -1)
        cv2.circle(maske, (yeni_px, yeni_py), pr, 0, -1)

        iris_halkasi = cv2.bitwise_and(kirpilmis_gri, kirpilmis_gri, mask=maske)

        hedef_boyut = 240
        eski_h, eski_w = kirpilmis_gri.shape[:2]

        iris_halkasi = cv2.resize(iris_halkasi, (hedef_boyut, hedef_boyut))
        maske = cv2.resize(maske, (hedef_boyut, hedef_boyut), interpolation=cv2.INTER_NEAREST)

        olcek_x = hedef_boyut / eski_w
        olcek_y = hedef_boyut / eski_h

        yeni_ix = int(yeni_ix * olcek_x)
        yeni_iy = int(yeni_iy * olcek_y)
        yeni_px = int(yeni_px * olcek_x)
        yeni_py = int(yeni_py * olcek_y)

        yeni_ir = int(ir * ((olcek_x + olcek_y) / 2))
        yeni_pr = int(pr * ((olcek_x + olcek_y) / 2))

        yeni_ir = min(yeni_ir, hedef_boyut // 2 - 6)
        yeni_pr = min(yeni_pr, max(8, yeni_ir - 12))

        konum_bilgisi = {
            "iris_merkez": (yeni_ix, yeni_iy),
            "iris_yaricap": yeni_ir,
            "pupil_merkez": (yeni_px, yeni_py),
            "pupil_yaricap": yeni_pr
        }

        return iris_halkasi, maske, konum_bilgisi

    def polar_normallestir(self, goruntu, maske, konum_bilgisi, aci_adim=512, yaricap_adim=64):
        iris_merkez_x, iris_merkez_y = konum_bilgisi["iris_merkez"]
        pupil_merkez_x, pupil_merkez_y = konum_bilgisi["pupil_merkez"]
        iris_r = konum_bilgisi["iris_yaricap"]
        pupil_r = konum_bilgisi["pupil_yaricap"]

        h, w = goruntu.shape
        polar = np.zeros((yaricap_adim, aci_adim), dtype=np.uint8)

        for t in range(aci_adim):
            aci = 2 * np.pi * t / aci_adim

            x_ic = pupil_merkez_x + pupil_r * np.cos(aci)
            y_ic = pupil_merkez_y + pupil_r * np.sin(aci)

            x_dis = iris_merkez_x + iris_r * np.cos(aci)
            y_dis = iris_merkez_y + iris_r * np.sin(aci)

            for r in range(yaricap_adim):
                oran = r / max(yaricap_adim - 1, 1)

                x = int((1 - oran) * x_ic + oran * x_dis)
                y = int((1 - oran) * y_ic + oran * y_dis)

                if 0 <= x < w and 0 <= y < h and maske[y, x] > 0:
                    polar[r, t] = goruntu[y, x]

        polar = cv2.equalizeHist(polar)
        polar = cv2.GaussianBlur(polar, (3, 3), 0)
        return polar

    def lbp_ozellikleri(self, goruntu):
        yaricap = 2
        nokta_sayisi = 8 * yaricap

        lbp = local_binary_pattern(goruntu, nokta_sayisi, yaricap, method="uniform")

        histogram, _ = np.histogram(
            lbp.ravel(),
            bins=np.arange(0, nokta_sayisi + 3),
            range=(0, nokta_sayisi + 2)
        )

        histogram = histogram.astype(np.float32)
        toplam = histogram.sum()

        if toplam > 0:
            histogram /= toplam

        return histogram

    def gradyan_ozellikleri(self, goruntu):
        gx = cv2.Sobel(goruntu, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(goruntu, cv2.CV_32F, 0, 1, ksize=3)
        buyukluk = cv2.magnitude(gx, gy)

        satir_ort = np.mean(buyukluk, axis=1)
        sutun_ort = np.mean(buyukluk, axis=0)

        ozellik = np.concatenate([satir_ort, sutun_ort]).astype(np.float32)
        norm = np.linalg.norm(ozellik)

        if norm > 1e-8:
            ozellik /= norm

        return ozellik

    def polar_parlama_temizle(self, polar):
        temiz = polar.copy()

        parlak_maske = temiz > 235
        bulanmis = cv2.GaussianBlur(temiz, (7, 7), 0)
        temiz[parlak_maske] = bulanmis[parlak_maske]

        return temiz

    def profil_gorseli_olustur(self, profil):
        min_deger = np.min(profil)
        max_deger = np.max(profil)

        if max_deger - min_deger < 1e-8:
            normlu = np.zeros_like(profil, dtype=np.uint8)
        else:
            normlu = ((profil - min_deger) / (max_deger - min_deger) * 255).astype(np.uint8)

        goruntu = np.tile(normlu, (120, 1))
        goruntu = cv2.resize(goruntu, (1000, 180), interpolation=cv2.INTER_NEAREST)
        return goruntu

    def cember_cizimli_gorsel(self, gri, iris, gozbebegi):
        renkli = cv2.cvtColor(gri, cv2.COLOR_GRAY2BGR)

        ix, iy, ir = iris
        px, py, pr = gozbebegi

        cv2.circle(renkli, (ix, iy), ir, (0, 255, 0), 2)
        cv2.circle(renkli, (px, py), pr, (0, 0, 255), 2)
        cv2.circle(renkli, (ix, iy), 2, (255, 0, 0), -1)

        return renkli

    def normalize_vektor(self, v):
        v = v.astype(np.float32)
        norm = np.linalg.norm(v)
        if norm <= 1e-8:
            return v
        return v / norm

    def gabor_ozellik_cikar(self, polar):
        ozellikler = []

        frekanslar = [0.1, 0.2, 0.3]
        acilar = [0, np.pi / 4, np.pi / 2, 3 * np.pi / 4]

        for frek in frekanslar:
            for aci in acilar:
                cekirdek = cv2.getGaborKernel(
                    (15, 15),
                    sigma=3.0,
                    theta=aci,
                    lambd=1.0 / frek,
                    gamma=0.5,
                    psi=0
                )

                filtrelenmis = cv2.filter2D(
                    polar.astype(np.float32),
                    cv2.CV_32F,
                    cekirdek
                )

                isaretler = np.sign(filtrelenmis).flatten()
                ozellikler.append(isaretler)

        return np.concatenate(ozellikler).astype(np.float32)

    def profil_vektoru_olustur(self, polar):
        lbp = self.lbp_ozellikleri(polar)
        gradyan = self.gradyan_ozellikleri(polar)
        gabor = self.gabor_ozellik_cikar(polar)

        gabor_norm = gabor / (np.linalg.norm(gabor) + 1e-8)
        lbp_norm = lbp / (np.linalg.norm(lbp) + 1e-8)
        gradyan_norm = gradyan / (np.linalg.norm(gradyan) + 1e-8)

        profil = np.concatenate([
            gabor_norm * 0.65,
            lbp_norm * 0.25,
            gradyan_norm * 0.10
        ]).astype(np.float32)

        return self.normalize_vektor(profil)

    def iris_profili_cikar(self, resim_yolu):
        gri = self.resmi_yukle(resim_yolu)
        onislenmis = self.on_isle(gri)

        gozbebegi = self.gozbebegi_bul(onislenmis)
        iris = self.iris_bul(onislenmis, gozbebegi)

        iris_halkasi, maske, konum_bilgisi = self.iris_halkasi_cikar(
            onislenmis,
            iris,
            gozbebegi
        )

        polar = self.polar_normallestir(iris_halkasi, maske, konum_bilgisi)
        polar = self.polar_parlama_temizle(polar)

        profil = self.profil_vektoru_olustur(polar)

        if np.linalg.norm(profil) <= 1e-8:
            raise ValueError("İris profili üretilemedi.")

        cizimli = self.cember_cizimli_gorsel(onislenmis, iris, gozbebegi)

        return {
            "profil": profil,
            "polar": polar,
            "iris_bolgesi": iris_halkasi,
            "onislenmis": onislenmis,
            "maske": maske,
            "cizimli": cizimli,
            "iris": iris,
            "gozbebegi": gozbebegi,
            "konum_bilgisi": konum_bilgisi
        }

    def profil_kaydet(self, sonuc, hedef_klasor, dosya_adi_on_eki):
        os.makedirs(hedef_klasor, exist_ok=True)

        iris_yolu = os.path.join(hedef_klasor, f"{dosya_adi_on_eki}_iris_bolgesi.png")
        polar_yolu = os.path.join(hedef_klasor, f"{dosya_adi_on_eki}_polar.png")
        maske_yolu = os.path.join(hedef_klasor, f"{dosya_adi_on_eki}_maske.png")
        cizimli_yolu = os.path.join(hedef_klasor, f"{dosya_adi_on_eki}_cemberler.png")
        profil_npy_yolu = os.path.join(hedef_klasor, f"{dosya_adi_on_eki}_profil.npy")
        profil_png_yolu = os.path.join(hedef_klasor, f"{dosya_adi_on_eki}_profil_gorsel.png")

        cv2.imwrite(iris_yolu, sonuc["iris_bolgesi"])
        cv2.imwrite(polar_yolu, sonuc["polar"])
        cv2.imwrite(maske_yolu, sonuc["maske"])
        cv2.imwrite(cizimli_yolu, sonuc["cizimli"])
        np.save(profil_npy_yolu, sonuc["profil"])

        profil_gorseli = self.profil_gorseli_olustur(sonuc["profil"])
        cv2.imwrite(profil_png_yolu, profil_gorseli)

        return {
            "iris_yolu": iris_yolu,
            "polar_yolu": polar_yolu,
            "maske_yolu": maske_yolu,
            "cizimli_yolu": cizimli_yolu,
            "profil_npy_yolu": profil_npy_yolu,
            "profil_png_yolu": profil_png_yolu
        }

    def polar_korelasyon(self, polar1, polar2):
        a = polar1.astype(np.float32).flatten()
        b = polar2.astype(np.float32).flatten()

        a = a - np.mean(a)
        b = b - np.mean(b)

        payda = np.linalg.norm(a) * np.linalg.norm(b)
        if payda <= 1e-8:
            return 0.0

        skor = float(np.dot(a, b) / payda)
        skor = (skor + 1.0) / 2.0

        return max(0.0, min(1.0, skor))

    def kaydirmali_karsilastir(self, kayit_polar, giris_polar, kaydirma_araligi=20):
        kayit_polar = kayit_polar.astype(np.uint8)
        giris_polar = giris_polar.astype(np.uint8)

        en_iyi_korelasyon = -1.0
        en_iyi_kaydirma = 0

        for kaydirma in range(-kaydirma_araligi, kaydirma_araligi + 1):
            kaymis = np.roll(giris_polar, shift=kaydirma, axis=1)
            korelasyon = self.polar_korelasyon(kayit_polar, kaymis)

            if korelasyon > en_iyi_korelasyon:
                en_iyi_korelasyon = korelasyon
                en_iyi_kaydirma = kaydirma

        en_iyi_kaymis = np.roll(giris_polar, shift=en_iyi_kaydirma, axis=1)

        profil1 = self.profil_vektoru_olustur(kayit_polar)
        profil2 = self.profil_vektoru_olustur(en_iyi_kaymis)

        kosinus = float(np.dot(profil1, profil2))
        kosinus = max(0.0, min(1.0, kosinus))

        genel_skor = 0.60 * kosinus + 0.40 * en_iyi_korelasyon
        mesafe = float(np.linalg.norm(profil1 - profil2))

        return {
            "genel_skor": float(genel_skor),
            "kosinus": float(kosinus),
            "korelasyon": float(en_iyi_korelasyon),
            "mesafe": mesafe,
            "en_iyi_kaydirma": int(en_iyi_kaydirma)
        }