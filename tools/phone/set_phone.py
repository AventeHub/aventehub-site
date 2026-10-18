"""Drop the new public company phone number into the whole site in one go.

Usage (from the repo root):
    python3 tools/phone/set_phone.py "+1 (647) 555-0123"

Replaces the tokens {{PHONE_DISPLAY}} / {{PHONE_DASH}} / {{PHONE_E164}} in every text file
and re-stamps the phone in the catalogue PDF (email/Avente-product-packs.pdf, page 2 footer).
813 stays WhatsApp-only (Max, Oct 17 15:18); this script never touches it.
Needs: pip install pymupdf
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOKENS = ('{{PHONE_DISPLAY}}', '{{PHONE_DASH}}', '{{PHONE_E164}}')
PDF = os.path.join(ROOT, 'email', 'Avente-product-packs.pdf')
# where the number sits in the PDF (page index 1): right after "Phone", Jost SemiBold 9 pt, cream
PDF_PAGE, PDF_RECT, PDF_ORIGIN = 1, (204.0, 688.5, 310.0, 699.0), (204.785, 696.3)
CREAM = (0xF1 / 255, 0xE7 / 255, 0xD6 / 255)
BG = (0x1B / 255, 0x15 / 255, 0x12 / 255)


def formats(raw):
    digits = re.sub(r'\D', '', raw)
    if len(digits) == 10:
        digits = '1' + digits
    if len(digits) != 11 or digits[0] != '1':
        sys.exit('Need a North American number, e.g. "+1 (647) 555-0123"')
    a, b, c = digits[1:4], digits[4:7], digits[7:]
    return {'{{PHONE_DISPLAY}}': f'+1 ({a}) {b}-{c}', '{{PHONE_DASH}}': f'+1-{a}-{b}-{c}', '{{PHONE_E164}}': f'+1{a}{b}{c}'}


def text_files():
    n = 0
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in ('.git', 'node_modules')]
        for f in files:
            if f.endswith(('.html', '.js', '.gs', '.json', '.md', '.txt', '.xml', '.css')):
                yield os.path.join(root, f)


def stamp_pdf(display):
    import pymupdf
    doc = pymupdf.open(PDF)
    page = doc[PDF_PAGE]
    r = pymupdf.Rect(*PDF_RECT)
    page.add_redact_annot(r, fill=BG)
    page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE)
    font = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Jost-600.ttf')
    page.insert_font(fontname='JostSB', fontfile=font)
    page.insert_text(PDF_ORIGIN, display, fontname='JostSB', fontsize=9, color=CREAM)
    tmp = PDF + '.tmp'
    doc.save(tmp, garbage=3, deflate=True)
    doc.close()
    os.replace(tmp, PDF)


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    fm = formats(sys.argv[1]) if sys.argv[1] != '--placeholder' else {'{{PHONE_DISPLAY}}': 'NEW NUMBER (coming)'}
    if sys.argv[1] != '--placeholder':
        changed = 0
        for p in text_files():
            s = open(p, encoding='utf-8').read()
            if any(t in s for t in TOKENS):
                for t, v in fm.items():
                    s = s.replace(t, v)
                open(p, 'w', encoding='utf-8').write(s)
                changed += 1
        print(f'text files updated: {changed}')
    stamp_pdf(fm['{{PHONE_DISPLAY}}'])
    print('catalogue PDF stamped:', fm['{{PHONE_DISPLAY}}'])


if __name__ == '__main__':
    main()
