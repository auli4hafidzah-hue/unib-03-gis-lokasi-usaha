"""Generator dataset untuk repo ini.

Data sintetis dengan seed tetap (reproducible), tidak memuat data pribadi.
Jalankan:  python src/generate_dataset.py
"""
from __future__ import annotations

import argparse
import os

import numpy as np
import pandas as pd

from common import seed_default

SEED = seed_default()


def gen_gis_market(seed: int = SEED) -> pd.DataFrame:
    """Kandidat lokasi usaha baru dengan atribut pasar (untuk analisis GIS).

    Setiap titik punya koordinat di wilayah Bengkulu/Sumatera selatan, atribut
    demografi, jarak ke pesaing, dan skor permintaan historis. Label
    `layak` diturunkan dari aturan skor gabungan supaya modul GIS bisa
    menguji hipotesis "jarak ke pesaing + kepadatan penduduk".
    """
    rng = np.random.default_rng(seed)
    n = 240
    lat = rng.uniform(-4.10, -3.60, n)          # sekitar Kota Bengkulu
    lon = rng.uniform(102.20, 102.60, n)
    kepadatan = rng.normal(4200, 1800, n).clip(300, 14000)
    income = rng.normal(3.4, 1.1, n).clip(1.2, 8.5)          # juta Rp/bulan
    competitor_dist_km = abs(rng.normal(1.6, 1.3, n)).clip(0.05, 8.0)
    pedestrian = rng.normal(180, 90, n).clip(10, 900)        # orang/jam
    sewa = rng.normal(18, 7, n).clip(3, 45)                  # juta Rp/tahun
    akses_jalan = rng.choice(["arteri", "kolektor", "lokal"], n, p=[0.2, 0.35, 0.45])

    skor = (
        0.35 * (kepadatan / 14000)
        + 0.25 * (income / 8.5)
        + 0.20 * np.clip(competitor_dist_km / 8, 0, 1)
        + 0.15 * (pedestrian / 900)
        + 0.05 * pd.Series(akses_jalan).map({"arteri": 1.0, "kolektor": 0.6, "lokal": 0.2}).to_numpy()
        - 0.10 * (sewa / 45)
    )
    prob = 1 / (1 + np.exp(-(skor - 0.5) * 6))
    layak = rng.binomial(1, prob)

    return pd.DataFrame(
        dict(
            lokasi_id=[f"L{i:03d}" for i in range(n)],
            lat=lat.round(6),
            lon=lon.round(6),
            kepadatan_penduduk=kepadatan.round(0).astype(int),
            income_juta_rp=income.round(2),
            competitor_dist_km=competitor_dist_km.round(3),
            pedestrian_per_jam=pedestrian.round(0).astype(int),
            sewa_juta_rp_tahun=sewa.round(2),
            akses_jalan=akses_jalan,
            skor_potensi=skor.round(4),
            layak=layak,
        )
    )


# ---------------------------------------------------------------- materi 5

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default="data")
    ap.add_argument("--seed", type=int, default=seed_default())
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    df = gen_gis_market(seed=a.seed)
    path = os.path.join(a.out, "materi3_gis_pasar.csv")
    df.to_csv(path, index=False)
    print(f"{path}  {len(df)} baris, {len(df.columns)} kolom")


if __name__ == "__main__":
    main()
