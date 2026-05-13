import os
import re
import cv2
import joblib
import numpy as np

from skimage.feature import hog
from sklearn.svm import LinearSVC
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score


VERISETI_KLASORU = "C:/Users/Emir/Desktop/CASIA-Iris-Thousand"
MODEL_YOLU = "veriler/goz_yonu_model.pkl"


def etiket_bul(dosya_adi):
    ad = os.path.basename(dosya_adi).upper()

    if re.search(r"L\d+", ad):
        return "sol"

    if re.search(r"R\d+", ad):
        return "sag"

    return None


def ozellik_cikar(resim_yolu):
    gri = cv2.imread(resim_yolu, cv2.IMREAD_GRAYSCALE)

    if gri is None:
        raise ValueError(f"Görüntü okunamadı: {resim_yolu}")

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


def veri_yukle():
    X = []
    y = []

    for kok, _, dosyalar in os.walk(VERISETI_KLASORU):
        for dosya in dosyalar:
            if not dosya.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
                continue

            yol = os.path.join(kok, dosya)
            etiket = etiket_bul(dosya)

            if etiket is None:
                continue

            try:
                X.append(ozellik_cikar(yol))
                y.append(etiket)
            except Exception as hata:
                print("Atlandı:", yol, hata)

    return np.array(X), np.array(y)


def main():
    print("Veriler okunuyor...")
    X, y = veri_yukle()

    print("Toplam veri:", len(X))
    print("Sağ göz:", np.sum(y == "sag"))
    print("Sol göz:", np.sum(y == "sol"))

    if len(X) < 20:
        raise ValueError("Model eğitmek için yeterli veri yok.")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y
    )

    model = make_pipeline(
        StandardScaler(),
        LinearSVC(C=1.0, class_weight="balanced", max_iter=10000)
    )

    print("Model eğitiliyor...")
    model.fit(X_train, y_train)

    tahmin = model.predict(X_test)

    print("Doğruluk:", accuracy_score(y_test, tahmin))
    print(classification_report(y_test, tahmin))

    os.makedirs(os.path.dirname(MODEL_YOLU), exist_ok=True)
    joblib.dump(model, MODEL_YOLU)

    print("Model kaydedildi:", MODEL_YOLU)


if __name__ == "__main__":
    main()