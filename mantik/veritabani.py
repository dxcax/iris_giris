import json
import os
import base64
import numpy as np


class VeriTabani:
    def __init__(self, dosya_yolu="veriler/kayitlar/kullanicilar.json"):
        self.dosya_yolu = dosya_yolu
        os.makedirs(os.path.dirname(self.dosya_yolu), exist_ok=True)

        if not os.path.exists(self.dosya_yolu):
            with open(self.dosya_yolu, "w", encoding="utf-8") as dosya:
                json.dump({}, dosya, ensure_ascii=False, indent=4)

    def _oku(self):
        with open(self.dosya_yolu, "r", encoding="utf-8") as dosya:
            return json.load(dosya)

    def _yaz(self, veri):
        with open(self.dosya_yolu, "w", encoding="utf-8") as dosya:
            json.dump(veri, dosya, ensure_ascii=False, indent=4)

    def vektoru_metne_cevir(self, vektor: np.ndarray) -> str:
        return base64.b64encode(vektor.astype(np.float32).tobytes()).decode("utf-8")

    def metni_vektore_cevir(self, metin: str) -> np.ndarray:
        ham = base64.b64decode(metin.encode("utf-8"))
        return np.frombuffer(ham, dtype=np.float32)

    def kullanici_kaydet(self, kullanici_adi, iris_profili, gorsel1, gorsel2):
        veriler = self._oku()
        veriler[kullanici_adi] = {
            "iris_profili": self.vektoru_metne_cevir(iris_profili),
            "gorsel1": gorsel1,
            "gorsel2": gorsel2
        }
        self._yaz(veriler)

    def kullanici_getir(self, kullanici_adi):
        veriler = self._oku()
        if kullanici_adi not in veriler:
            return None

        kayit = veriler[kullanici_adi]
        return {
            "iris_profili": self.metni_vektore_cevir(kayit["iris_profili"]),
            "gorsel1": kayit["gorsel1"],
            "gorsel2": kayit["gorsel2"]
        }

    def kullanici_var_mi(self, kullanici_adi):
        veriler = self._oku()
        return kullanici_adi in veriler