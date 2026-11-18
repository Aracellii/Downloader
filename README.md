# Base64 to PDF Downloader

Script Python untuk menggabungkan gambar halaman `data:image/...;base64` dari situs dokumen menjadi satu PDF. Mendukung Windows, Linux, dan macOS.

## Cara pakai

Pastikan Python sudah terinstal. Tersedia dua cara:

### 1. Otomatis (`downloads.py`)

Dependensi dan Chromium Playwright akan dipasang otomatis jika belum tersedia.

**Windows:**

```powershell
py downloads.py "https://contoh.com/dokumen" -o hasil.pdf
```

**Linux / macOS:**

```bash
python3 downloads.py 'https://contoh.com/dokumen' -o hasil.pdf
```

Untuk situs yang membutuhkan login, tambahkan `--login`.

### 2. Manual (`downloadmanual.py`)

Instal dependensi terlebih dahulu:

```bash
python -m pip install pillow playwright
python -m playwright install chromium
```

Jalankan:

**Windows:**

```powershell
py downloadmanual.py "https://contoh.com/dokumen" -o hasil.pdf
```

**Linux / macOS:**

```bash
python3 downloadmanual.py 'https://contoh.com/dokumen' -o hasil.pdf
```

Browser akan terbuka. Login atau buka dokumen jika diperlukan, lalu tekan **Enter di terminal** untuk mulai mengambil halaman.

Untuk data Base64 yang sudah disimpan di file TXT (satu URI per baris):

```bash
python3 downloadmanual.py --input halaman.txt -o hasil.pdf
```

> **Catatan:** Hanya mendukung gambar Base64 (`data:image/...;base64`), bukan semua viewer PDF, canvas, atau blob. Gunakan hanya pada dokumen yang berhak kamu akses.
