# Studi Kasus 3 — Carrier and Competition in Industrial Era with GIS

Materi dari [Informatika UNIB Official](https://youtube.com/@informatikaunibofficial):
**"Carrier and Competition in Industrial Era with GIS"**.

Studi kasus analisis lokasi usaha dengan pendekatan GIS ringan: pengukuran jarak
geografis, pengklasteran pasar, dan skoring kelayakan lokasi.

> Data **sintetis dengan seed tetap** (reproducible). Koordinat disebar di wilayah
> sekitar Kota Bengkulu, tidak memuat data pribadi.

## Menjalankan

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

bash run.sh          # atau:
python src/generate_dataset.py
python src/materi3_gis_analisis.py
```

Hasil masuk ke `outputs/`.

## Dataset

`data/materi3_gis_pasar.csv` — 240 kandidat lokasi di sekitar Kota Bengkulu.

Kolom: `lokasi_id`, `lat`, `lon`, `kepadatan_penduduk`, `income_juta_rp`,
`competitor_dist_km`, `pedestrian_per_jam`, `sewa_juta_rp_tahun`, `akses_jalan`,
`skor_potensi`, `layak`.

## Metode

1. **Haversine distance** — menghitung jarak koordinat langsung dari numpy, tanpa
   GeoPandas, supaya dependency tetap ringan.
2. **Korelasi faktor** — menguji hipotesis mana yang benar-benar berkorelasi dengan
   kelayakan lokasi.
3. **K-means (3 klaster)** — diimplementasikan manual pada fitur terstandarisasi
   (kepadatan penduduk, jarak pesaing) untuk melihat profil pasar.
4. **Skoring** — memilih 10 kandidat terbaik berdasarkan `skor_potensi`.

## Hasil terakhir

Korelasi faktor terhadap kelayakan:

| Faktor | Korelasi |
|---|---|
| `income_juta_rp` | **+0,138** |
| `sewa_juta_rp_tahun` | **−0,114** |
| `kepadatan_penduduk` | +0,085 |
| `log_jarak` (jarak pesaing) | +0,036 |
| `pedestrian_per_jam` | −0,035 |

Profil klaster:

| Klaster | Kepadatan | Jarak pesaing | Sewa | Rasio layak |
|---|---|---|---|---|
| 0 | 3.715 | 3,08 km | 17,76 | 0,20 |
| 1 | 6.206 | 1,50 km | 17,64 | 0,20 |
| 2 | 3.192 | 0,96 km | 18,86 | 0,16 |

10 kandidat terbaik tersimpan di `outputs/materi3_kandidat_terbaik.csv`, dan
sebarannya divisualisasikan di `outputs/materi3_peta_lokasi.png`.

## Temuan penting

Hipotesis umum "semakin jauh dari pesaing semakin baik" **tidak didukung data** —
korelasi jarak ke pesaing hanya 0,036, jauh di bawah pendapatan (0,138) dan sewa (−0,114).

Klaster 1 (paling padat, paling dekat pesaing) punya rasio layak **sama tinggi** dengan
klaster 0 yang jaraknya 2× lebih jauh. Artinya pasar padat menyerap kompetisi:
yang menentukan kelayakan adalah **daya beli dan biaya sewa**, bukan sekadar
menghindari pesaing.

Caveat: sampel 240 titik dan korelasi keseluruhan lemah, jadi ini indikasi arah,
bukan kebenaran statistik yang kuat.

## Struktur

```
src/common.py              # helper path & direktori
src/generate_dataset.py    # generator kandidat lokasi sintetis
src/materi3_gis_analisis.py
data/    outputs/          # dibuat saat runtime, tidak di-commit
```

## Lisensi

MIT — lihat [LICENSE](LICENSE).
