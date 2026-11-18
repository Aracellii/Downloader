#!/usr/bin/env python3
"""Simpan gambar halaman data:image/...;base64 dari halaman yang sudah dapat diakses.

Instal: pip install playwright pillow && python -m playwright install chromium
Pakai: python base64_halaman_ke_pdf.py 'https://alamat-dokumen' -o hasil.pdf
      python base64_halaman_ke_pdf.py --input pasted.txt -o hasil.pdf
"""
import argparse
import base64
import hashlib
import io
import re
from pathlib import Path
from PIL import Image, ImageOps

PATTERN = re.compile(r'^data:image/(?:png|jpeg|jpg|webp);base64,', re.I)


def decode_image(uri):
    uri = uri.strip()
    if not PATTERN.match(uri):
        return None
    try:
        raw = base64.b64decode(uri.split(',', 1)[1], validate=True)
        im = Image.open(io.BytesIO(raw))
        im.load()
        return im
    except Exception:
        return None


def to_pdf(images, path):
    if not images:
        raise SystemExit('Tidak ada gambar halaman yang ditemukan.')
    pages = []
    for im in images:
        im = ImageOps.exif_transpose(im)
        if im.mode == 'RGBA' or 'transparency' in im.info:
            bg = Image.new('RGB', im.size, 'white')
            bg.paste(im.convert('RGBA'), mask=im.convert('RGBA').getchannel('A'))
            im = bg
        else:
            im = im.convert('RGB')
        pages.append(im)
    pages[0].save(path, 'PDF', save_all=True, append_images=pages[1:], resolution=100.0)
    print(f'Selesai: {path} ({len(pages)} halaman)')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('url', nargs='?', help='URL halaman yang boleh Anda akses')
    parser.add_argument('--input', help='File TXT berisi satu atau beberapa data:image/...;base64 (satu per baris)')
    parser.add_argument('-o', '--output', default='hasil.pdf', help='Lokasi PDF keluaran')
    parser.add_argument('--min-width', type=int, default=500)
    parser.add_argument('--min-height', type=int, default=600)
    parser.add_argument('--scrolls', type=int, default=100, help='Maksimum putaran scroll')
    args = parser.parse_args()
    if not args.input and not args.url:
        parser.error('Berikan URL atau --input file.txt')

    images, seen = [], set()

    def add(uri):
        if not isinstance(uri, str) or not PATTERN.match(uri):
            return False
        digest = hashlib.sha256(uri.encode()).hexdigest()
        if digest in seen:
            return False
        seen.add(digest)
        im = decode_image(uri)
        if im is None or im.width < args.min_width or im.height < args.min_height:
            return False
        images.append(im)
        print(f'Halaman {len(images)}: {im.width}x{im.height}')
        return True

    if args.input:
        for line in Path(args.input).read_text(encoding='utf-8').splitlines():
            add(line)
    else:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            profile = str(Path.home() / '.cache' / 'pdf-page-capture-chromium')
            context = pw.chromium.launch_persistent_context(profile, headless=False)
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(args.url, wait_until='domcontentloaded', timeout=60000)
            print('Login/buka dokumen secara normal di browser jika perlu.')
            input('Setelah halaman dokumen terlihat, tekan ENTER di terminal...')
            stagnant = 0
            for i in range(args.scrolls):
                # Ambil hanya gambar base64 yang benar-benar ada di DOM.
                uris = page.locator('img').evaluate_all('''els => els.map(e => e.currentSrc || e.src).filter(s => s && s.startsWith('data:image/'))''')
                # Juga mendukung gambar yang diisikan melalui CSS background-image.
                uris += page.evaluate('''() => Array.from(document.querySelectorAll('*')).map(e => getComputedStyle(e).backgroundImage).filter(s => s.startsWith('url("data:image/')).map(s => s.slice(5, -2))''')
                before = len(images)
                for uri in uris:
                    add(uri)
                stagnant = stagnant + 1 if len(images) == before else 0
                if stagnant >= 12:
                    print('Tidak ada halaman baru setelah beberapa kali scroll.')
                    break
                page.evaluate('''() => {
                  window.scrollBy(0, Math.max(650, window.innerHeight * 0.85));
                  for (const el of document.querySelectorAll('*')) {
                    if (el.scrollHeight > el.clientHeight + 300 && el.clientHeight > 300 && getComputedStyle(el).overflowY !== 'hidden') {
                      el.scrollTop += Math.max(650, el.clientHeight * 0.85);
                    }
                  }
                }''')
                page.wait_for_timeout(900)
            context.close()
    to_pdf(images, args.output)


if __name__ == '__main__':
    main()
