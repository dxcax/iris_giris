import json
import os
import base64
import numpy as np


class VeriTabani:
    def __init__(self, dosya_yolu="veriler/kayitlar/kullanicilar.json"):
        self.dosya_yolu = dosya_yolu
        os.makedirs(os.path.dirname(self.dosya_yolu), exist_ok=True)

        if not os.path.exists(self.dosya_yolu):
            self._yaz({})

    def _oku(self):
        with open(self.dosya_yolu, "r", encoding="utf-8") as dosya:
            return json.load(dosya)

    def _yaz(self, veri):
        with open(self.dosya_yolu, "w", encoding="utf-8") as dosya:
            json.dump(veri, dosya, ensure_ascii=False, indent=4)

    def vektoru_metne_cevir(self, vektor: np.ndarray) -> str:
        return base64.b64encode(
            vektor.astype(np.float32).tobytes()
        ).decode("utf-8")

    def metni_vektore_cevir(self, metin: str) -> np.ndarray:
        ham = base64.b64decode(metin.encode("utf-8"))
        return np.frombuffer(ham, dtype=np.float32)

    def kullanici_kaydet(self, kullanici_adi, sag_profil, sol_profil, sag_gorsel, sol_gorsel):
        veriler = self._oku()

        veriler[kullanici_adi] = {
            "sag_iris_profili": self.vektoru_metne_cevir(sag_profil),
            "sol_iris_profili": self.vektoru_metne_cevir(sol_profil),
            "sag_gorsel": sag_gorsel,
            "sol_gorsel": sol_gorsel
        }

        self._yaz(veriler)

    def kullanici_getir(self, kullanici_adi):
        veriler = self._oku()

        if kullanici_adi not in veriler:
            return None

        kayit = veriler[kullanici_adi]

        return {
            "sag_iris_profili": self.metni_vektore_cevir(kayit["sag_iris_profili"]),
            "sol_iris_profili": self.metni_vektore_cevir(kayit["sol_iris_profili"]),
            "sag_gorsel": kayit["sag_gorsel"],
            "sol_gorsel": kayit["sol_gorsel"]
        }

    def kullanici_var_mi(self, kullanici_adi):
        return kullanici_adi in self._oku()