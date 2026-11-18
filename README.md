# Base64 Halaman ke PDF

Script Python untuk mengumpulkan gambar halaman berformat **`data:image/...;base64`** dari situs dokumen yang dapat diakses, kemudian menggabungkannya menjadi satu file PDF.

Mendukung **Windows, Linux (termasuk Fedora/Ubuntu), dan macOS**. Dependensi Python serta Chromium untuk Playwright disiapkan secara otomatis saat diperlukan, sehingga tidak perlu menjalankan `pip install` secara manual.

> [!IMPORTANT]
> Script ini **bukan pengunduh PDF universal**. Script hanya dapat memproses gambar Base64 yang tersedia di elemen gambar atau CSS halaman web. Viewer berbasis `canvas`, `blob:`, atau PDF asli tidak otomatis didukung. Gunakan hanya pada dokumen yang memang berhak Anda akses dan simpan.

## Fitur

- Mengonversi gambar PNG, JPEG/JPG, dan WebP berformat Base64 menjadi PDF multipage.
- Membaca gambar dari elemen `<img>` dan `background-image` CSS, termasuk iframe yang dapat diakses oleh Playwright.
- Scroll otomatis untuk memuat gambar tambahan.
- Menghindari gambar duplikat berdasarkan hash.
- Memfilter gambar kecil agar ikon dan thumbnail tidak ikut masuk.
- Mengubah gambar transparan menjadi halaman berlatar putih.
- Bisa membaca langsung dari file TXT berisi data URI Base64.
- Menginstal **Pillow**, **Playwright**, dan browser **Chromium** secara otomatis jika belum tersedia.
- Menyediakan mode browser terlihat untuk login manual menggunakan `--login`.

## Persyaratan

- **Python 3.9+** yang sudah tersedia di PATH, beserta dukungan `venv` dan `pip`.
- Koneksi internet saat pertama kali menginstal dependensi atau Chromium.
- Akses ke situs atau dokumen yang ingin diproses.
- Pada Linux, Chromium mungkin memerlukan pustaka sistem tambahan yang tidak otomatis diinstal oleh script.

## Instalasi

Unduh file [`base64_halaman_ke_pdf.py`](base64_halaman_ke_pdf.py) atau clone repository ini:

```bash
git clone https://github.com/USERNAME/REPOSITORY.git
cd REPOSITORY
```

Ganti `USERNAME/REPOSITORY` dengan alamat repository Anda. Tidak perlu menginstal paket Python secara manual.

## Penggunaan

### Windows (PowerShell atau Command Prompt)

```powershell
py base64_halaman_ke_pdf.py "https://contoh.com/dokumen" -o hasil.pdf
```

### Linux (Fedora / Ubuntu)

```bash
python3 base64_halaman_ke_pdf.py 'https://contoh.com/dokumen' -o hasil.pdf
```

### macOS

```bash
python3 base64_halaman_ke_pdf.py 'https://contoh.com/dokumen' -o hasil.pdf
```

Saat dijalankan pertama kali, script akan membuat virtual environment sendiri, menginstal dependensi yang dibutuhkan, dan mengunduh Chromium jika belum ada. Setelah itu script akan membuka halaman, scroll, mengumpulkan gambar Base64, dan menyimpannya ke PDF. Pada penggunaan berikutnya dependensi yang sudah tersedia akan digunakan kembali.

### Halaman yang membutuhkan login

```bash
python3 base64_halaman_ke_pdf.py 'https://contoh.com/dokumen' --login -o hasil.pdf
```

Di Windows, ganti `python3` dengan `py` jika perlu. Browser akan terlihat agar Anda dapat login dan membuka dokumen. **Tekan Enter pada terminal** setelah halaman dokumen sudah tampil untuk memulai pengambilan.

### Dari file TXT Base64

Siapkan `pasted.txt` dengan **satu data URI gambar per baris**, misalnya:

```text
data:image/png;base64,iVBORw0KGgoAAA...
data:image/jpeg;base64,/9j/4AAQSkZJRgABAQ...
```

Lalu jalankan:

```bash
python3 base64_halaman_ke_pdf.py --input pasted.txt -o hasil.pdf
```

Mode ini tidak memerlukan browser Chromium; hanya Pillow yang digunakan.

### Atur jumlah scroll dan jeda

```bash
python3 base64_halaman_ke_pdf.py 'https://contoh.com/dokumen' \
  --scrolls 250 --delay 1200 -o hasil.pdf
```

Contoh di atas untuk Linux/macOS. Di PowerShell, tulis perintah dalam satu baris atau gunakan karakter lanjutan baris PowerShell.

## Opsi command-line

| Opsi | Default | Keterangan |
| --- | --- | --- |
| `url` | Tidak ada | URL halaman dokumen |
| `--input` | Tidak ada | File TXT berisi data URI Base64, satu per baris |
| `-o`, `--output` | `hasil.pdf` | Path file PDF hasil |
| `--min-width` | `500` | Lebar minimum gambar (piksel) |
| `--min-height` | `600` | Tinggi minimum gambar (piksel) |
| `--scrolls` | `150` | Jumlah maksimum iterasi scroll |
| `--delay` | `900` | Jeda antara scroll dalam milidetik |
| `--login` | Mati | Tampilkan browser untuk login manual |
| `-h`, `--help` | | Tampilkan bantuan |

Contoh mengikutsertakan halaman berukuran lebih kecil:

```bash
python3 base64_halaman_ke_pdf.py 'https://contoh.com/dokumen' \
  --min-width 300 --min-height 400 -o hasil.pdf
```

## Lokasi dependensi dan data browser

Script menyimpan virtual environment dan profil Chromium di direktori cache lokal:

| OS | Lokasi cache |
| --- | --- |
| Windows | `%LOCALAPPDATA%\base64-halaman-ke-pdf` |
| Linux | `${XDG_CACHE_HOME:-~/.cache}/base64-halaman-ke-pdf` |
| macOS | `~/Library/Caches/base64-halaman-ke-pdf` |

**Catatan:** File browser Chromium Playwright sendiri mengikuti lokasi browser cache bawaan Playwright, yang dapat berbeda dari folder di atas. Profil browser dapat menyimpan data sesi login, jadi jangan mengunggah folder cache tersebut ke GitHub.

## Troubleshooting

**`Tidak ditemukan gambar halaman base64`**

- Pastikan dokumen sudah tampil. Jika perlu login, gunakan `--login`.
- Pastikan viewer memang menghasilkan `data:image/...;base64` dan bukan elemen `canvas`, URL `blob:`, atau tautan gambar biasa.
- Coba tambah `--scrolls` atau `--delay` untuk halaman yang memuat gambar secara lambat.
- Pastikan gambar halaman memenuhi batas `--min-width` dan `--min-height`.

**Gagal membuat virtual environment**

Pastikan instalasi Python menyediakan modul `venv` dan `pip`. Pada beberapa distribusi Linux, paket pendukung perlu dipasang lewat package manager sistem.

**Chromium gagal berjalan di Linux**

Sistem mungkin belum memiliki pustaka native yang diperlukan browser. Lihat dokumentasi [Playwright: Browsers](https://playwright.dev/python/docs/browsers) untuk dependensi sistem yang sesuai distribusi.

**Halaman PDF tidak lengkap atau urutannya keliru**

Script menyimpan gambar sesuai urutan saat pertama kali ditemukan selama proses scroll. Viewer yang memuat halaman tidak berurutan atau menggunakan virtualisasi DOM mungkin membutuhkan penyesuaian khusus. Periksa hasil PDF sebelum digunakan.

## Batasan

- Tidak mengunduh file PDF asli dari server; PDF dibentuk ulang dari gambar halaman.
- PDF hasil **berbasis gambar**, sehingga teksnya tidak otomatis dapat diseleksi atau dicari (tidak ada OCR).
- Kualitas bergantung pada resolusi gambar yang tersedia di viewer.
- Tidak menjamin semua halaman berhasil tertangkap atau urutannya selalu benar.
- Tidak melakukan bypass login, captcha, DRM, pembatasan akses, maupun mekanisme keamanan situs.

## Lisensi

Belum ada file lisensi yang ditetapkan. Tambahkan file `LICENSE` ke repository jika Anda ingin mengizinkan penggunaan atau distribusi ulang dengan ketentuan lisensi tertentu.
