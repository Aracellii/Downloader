# Base64 to PDF Downloader

Script Python untuk mengambil gambar halaman **Base64** dari situs dokumen dan menggabungkannya menjadi satu file PDF.

Mendukung **Windows, Linux, dan macOS**. Dependensi Python dan Chromium Playwright diinstal otomatis saat pertama kali dijalankan.

## Cara Pakai

Pastikan **Python 3.9+** sudah terpasang.

**Windows:**

```powershell
py base64_halaman_ke_pdf.py "https://contoh.com/dokumen" -o hasil.pdf
```

**Linux / macOS:**

```bash
python3 base64_halaman_ke_pdf.py 'https://contoh.com/dokumen' -o hasil.pdf
```

Jika perlu login, tambahkan `--login`:

```bash
python3 base64_halaman_ke_pdf.py 'https://contoh.com/dokumen' --login -o hasil.pdf
```

Untuk mengubah data Base64 dari file TXT:

```bash
python3 base64_halaman_ke_pdf.py --input halaman.txt -o hasil.pdf
```

> **Catatan:** Hanya mendukung gambar `data:image/...;base64`, bukan semua jenis PDF viewer. Gunakan pada dokumen yang berhak kamu akses dan simpan.
