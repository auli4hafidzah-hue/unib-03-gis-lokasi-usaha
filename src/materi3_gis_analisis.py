"""Materi 3 - Carrier and Competition in Industrial Era with GIS.

Analisis lokasi usaha dengan pendekatan GIS ringan (tanpa GeoPandas supaya
dependency tetap kecil): buffer pesaing, kepadatan penduduk, dan skor kelayakan.

Jalankan:
    python src/materi3_gis_analisis.py
Output:
    outputs/materi3_peta_lokasi.png
    outputs/materi3_kandidat_terbaik.csv
    outputs/materi3_ringkasan.txt
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

DATA = os.path.join("data", "materi3_gis_pasar.csv")
OUT = "outputs"


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dp = p2 - p1
    dl = np.radians(lon2 - lon1)
    a = np.sin(dp / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * r * np.arcsin(np.sqrt(a))


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    df = pd.read_csv(DATA)

    # --- 1. Hitung ulang skor & uji faktor ------------------------------
    # hipotesis: jarak ke pesaing & kepadatan penduduk menentukan kelayakan
    df["log_jarak"] = np.log(df["competitor_dist_km"])
    num = ["kepadatan_penduduk", "income_juta_rp", "log_jarak",
           "pedestrian_per_jam", "sewa_juta_rp_tahun"]
    corr = df[num + ["layak"]].corr()["layak"].drop("layak").sort_values(key=abs, ascending=False)

    # --- 2. Klaster sederhana (k-means manual, 3 klaster) ---------------
    x = df[["kepadatan_penduduk", "competitor_dist_km"]].to_numpy()
    x = (x - x.mean(0)) / x.std(0)
    rng = np.random.default_rng(7)
    cent = x[rng.choice(len(x), 3, replace=False)]
    for _ in range(100):
        lab = ((x[:, None, :] - cent[None]) ** 2).sum(-1).argmin(1)
        for k in range(3):
            if (lab == k).any():
                cent[k] = x[lab == k].mean(0)
    df["klaster"] = lab

    # --- 3. 10 kandidat terbaik -----------------------------------------
    top = df.sort_values("skor_potensi", ascending=False).head(10)

    # --- 4. Peta ---------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 7))
    for k, name in enumerate(["A", "B", "C"]):
        sub = df[df["klaster"] == k]
        ax.scatter(sub["lon"], sub["lat"], s=14, alpha=0.45, label=f"Klaster {name}")
    ax.scatter(top["lon"], top["lat"], s=90, facecolors="none",
               edgecolors="red", linewidths=1.6, label="10 kandidat terbaik")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("Materi 3 - Sebaran kandidat lokasi & klaster pasar")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "materi3_peta_lokasi.png"), dpi=140)
    plt.close(fig)

    # --- 5. Ringkasan ----------------------------------------------------
    lines = ["=== MATERI 3: ANALISIS GIS LOKASI USAHA ===\n"]
    lines.append(f"Kandidat: {len(df)} | klaster: 3 | layak: {df['layak'].sum()} "
                 f"({df['layak'].mean():.1%})\n")
    lines.append("-- Korelasi faktor vs kelayakan --")
    lines.append(corr.to_string())
    lines.append("\n-- Profil klaster --")
    lines.append(df.groupby("klaster")[["kepadatan_penduduk", "competitor_dist_km",
                                        "sewa_juta_rp_tahun", "layak"]].mean().round(2).to_string())
    lines.append("\n-- 10 kandidat terbaik --")
    lines.append(top[["lokasi_id", "lat", "lon", "kepadatan_penduduk",
                      "competitor_dist_km", "skor_potensi"]].to_string(index=False))

    top.to_csv(os.path.join(OUT, "materi3_kandidat_terbaik.csv"), index=False)
    report = "\n".join(lines)
    with open(os.path.join(OUT, "materi3_ringkasan.txt"), "w") as f:
        f.write(report)
    print(report)


if __name__ == "__main__":
    main()
