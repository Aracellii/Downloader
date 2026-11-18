#!/usr/bin/env python3
"""Gabungkan gambar halaman base64 dari dokumen web yang dapat diakses menjadi PDF.

Dependensi otomatis diinstal saat pertama kali dijalankan (perlu internet).
Mendukung Windows, Linux, dan macOS dengan Python 3.9+.

Penggunaan:
    Windows: py base64_halaman_ke_pdf.py "https://alamat-dokumen" -o hasil.pdf
    Linux:   python3 base64_halaman_ke_pdf.py 'https://alamat-dokumen' -o hasil.pdf
    python base64_halaman_ke_pdf.py --input pasted.txt -o hasil.pdf
    python base64_halaman_ke_pdf.py 'https://alamat-dokumen' --login -o hasil.pdf
"""
import argparse
import base64
import hashlib
import io
import re
import os
import sys
import subprocess
import importlib.util
import venv
from pathlib import Path


def cache_dir():
    """Folder cache sesuai platform, tanpa perlu paket tambahan."""
    if sys.platform == "win32":
        root = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
        return Path(root) / "base64-halaman-ke-pdf"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Caches" / "base64-halaman-ke-pdf"
    return Path(os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache"))) / "base64-halaman-ke-pdf"


def prepare_environment():
    """Siapkan venv mandiri dan paket yang dibutuhkan pada tiap OS."""
    if any(x in sys.argv for x in ("-h", "--help")):
        return
    env_dir = cache_dir() / "venv"
    env_python = env_dir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")

    if os.environ.get("PDF_SCRIPT_VENV") != "1":
        if not env_python.is_file():
            print("[Setup] Membuat virtual environment...", flush=True)
            try:
                venv.EnvBuilder(with_pip=True).create(env_dir)
            except Exception as exc:
                raise SystemExit(f"Gagal membuat venv: {exc}\nPastikan Python terpasang dengan pip dan venv.") from exc
        # subprocess + exit code portable untuk Windows (os.execve tidak ideal).
        env = os.environ.copy()
        env["PDF_SCRIPT_VENV"] = "1"
        result = subprocess.run(
            [str(env_python), str(Path(__file__).resolve()), *sys.argv[1:]],
            env=env,
            check=False,
        )
        raise SystemExit(result.returncode)

    needed = []
    if importlib.util.find_spec("PIL") is None:
        needed.append("pillow")
    if "--input" not in sys.argv and importlib.util.find_spec("playwright") is None:
        needed.append("playwright")
    if needed:
        print("[Setup] Menginstal: " + ", ".join(needed), flush=True)
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *needed])
        except subprocess.CalledProcessError as exc:
            raise SystemExit("Instalasi paket gagal. Periksa koneksi internet dan akses PyPI.") from exc

    if "--input" not in sys.argv and not any(x in sys.argv for x in ("-h", "--help")):
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            chromium_path = Path(pw.chromium.executable_path)
        if not chromium_path.is_file():
            print("[Setup] Mengunduh Chromium Playwright...", flush=True)
            try:
                subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
            except subprocess.CalledProcessError as exc:
                raise SystemExit("Unduhan Chromium gagal. Periksa koneksi internet atau dependensi sistem browser.") from exc


prepare_environment()

from PIL import Image, ImageOps

PATTERN = re.compile(r"^data:image/(?:png|jpeg|jpg|webp);base64,", re.I)


def decode_image(uri):
    if not isinstance(uri, str) or not PATTERN.match(uri.strip()):
        return None
    try:
        raw = base64.b64decode(uri.split(",", 1)[1], validate=True)
        with Image.open(io.BytesIO(raw)) as img:
            img.load()
            return img.copy()
    except Exception:
        return None


def to_pdf(images, path):
    if not images:
        raise SystemExit("Tidak ditemukan gambar halaman base64. Situs mungkin menggunakan canvas/blob atau dokumen belum dimuat.")
    pages = []
    for im in images:
        im = ImageOps.exif_transpose(im)
        if im.mode == "RGBA" or "transparency" in im.info:
            rgba = im.convert("RGBA")
            bg = Image.new("RGB", rgba.size, "white")
            bg.paste(rgba, mask=rgba.getchannel("A"))
            pages.append(bg)
        else:
            pages.append(im.convert("RGB"))
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    pages[0].save(str(path), "PDF", save_all=True, append_images=pages[1:], resolution=100.0)
    print(f"Selesai: {path.resolve()} ({len(pages)} halaman)")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("url", nargs="?", help="URL dokumen yang dapat diakses")
    p.add_argument("--input", help="TXT berisi data:image/...;base64, satu per baris")
    p.add_argument("-o", "--output", default="hasil.pdf")
    p.add_argument("--min-width", type=int, default=500)
    p.add_argument("--min-height", type=int, default=600)
    p.add_argument("--scrolls", type=int, default=150)
    p.add_argument("--delay", type=int, default=900, help="Jeda tiap scroll (milidetik)")
    p.add_argument("--login", action="store_true", help="Berhenti untuk login manual bila perlu")
    args = p.parse_args()
    if not args.url and not args.input:
        p.error("Masukkan URL atau --input")

    images, seen = [], set()

    def add(uri):
        if not isinstance(uri, str) or not PATTERN.match(uri.strip()):
            return False
        img = decode_image(uri.strip())
        if img is None or img.width < args.min_width or img.height < args.min_height:
            return False
        digest = hashlib.sha256(uri.encode()).hexdigest()
        if digest in seen:
            return False
        seen.add(digest)
        images.append(img)
        print(f"Halaman {len(images)}: {img.width}x{img.height}", flush=True)
        return True

    if args.input:
        for line in Path(args.input).read_text(encoding="utf-8").splitlines():
            add(line)
    else:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            profile_path = cache_dir() / "chromium-profile"
            profile_path.parent.mkdir(parents=True, exist_ok=True)
            profile = str(profile_path)
            context = pw.chromium.launch_persistent_context(profile, headless=not args.login)
            try:
                page = context.pages[0] if context.pages else context.new_page()
                page.goto(args.url, wait_until="domcontentloaded", timeout=60000)
                if args.login:
                    input("Login dan tampilkan dokumen, lalu tekan ENTER untuk lanjut...")
                page.wait_for_timeout(1800)
                stagnant = 0
                for _ in range(args.scrolls):
                    before = len(images)
                    # Ambil dari DOM pada halaman dan iframe yang bisa diakses.
                    for frame in page.frames:
                        try:
                            uris = frame.locator("img").evaluate_all(
                                "els => els.map(e => e.currentSrc || e.src).filter(s => s && s.startsWith('data:image/'))"
                            )
                            uris += frame.evaluate("""() => Array.from(document.querySelectorAll('*'))
                                .map(e => getComputedStyle(e).backgroundImage)
                                .filter(s => s.startsWith('url(') && s.includes('data:image/'))
                                .map(s => s.slice(4, -1).replace(/^['\"]|['\"]$/g, ''))""")
                            for uri in uris:
                                add(uri)
                        except Exception:
                            continue
                    stagnant = stagnant + 1 if len(images) == before else 0
                    if stagnant >= 12:
                        break
                    for frame in page.frames:
                        try:
                            frame.evaluate("""() => {
                                window.scrollBy(0, Math.max(650, window.innerHeight * 0.85));
                                for (const el of document.querySelectorAll('*')) {
                                    if (el.scrollHeight > el.clientHeight + 300 && el.clientHeight > 300 &&
                                        getComputedStyle(el).overflowY !== 'hidden') {
                                        el.scrollTop += Math.max(650, el.clientHeight * 0.85);
                                    }
                                }
                            }""")
                        except Exception:
                            continue
                    page.wait_for_timeout(args.delay)
            finally:
                context.close()
    to_pdf(images, args.output)


if __name__ == "__main__":
    main()
