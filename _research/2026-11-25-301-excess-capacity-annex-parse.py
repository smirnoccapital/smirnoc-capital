import sys, pdfplumber, re, csv, pathlib
from multiprocessing import Pool
CODE = re.compile(r'^\d{4}\.\d{2}\.\d{2}$')
def parse(p):
    rows=[]; started=False; annex=''; part=''
    with pdfplumber.open(p) as pdf:
        for pn, pg in enumerate(pdf.pages, 1):
            txt = pg.extract_text() or ''
            if not started:
                if re.search(r'^\s*ANNEX\b|^\s*Annex\s*$', txt, re.M): started=True
                else: continue
            m = re.search(r'^\s*ANNEX\s*([AB])?\b', txt, re.M)
            if m: annex = m.group(1) or annex or ''
            m = re.search(r'–\s*Part\s+([IVX]+)', txt)
            if m: part = m.group(1)
            words = pg.extract_words()
            codes = [w for w in words if CODE.match(w['text']) and w['x0'] < 160]
            scopes = [w for w in words if w['text'] in ('Ex','Aircraft','Pharma') and w['x0'] > 430]
            for c in codes:
                sc = [s['text'] for s in scopes if abs(s['top']-c['top']) < 3]
                rows.append((p.stem.split('_')[0], annex, part, c['text'], sc[0] if sc else '', pn))
    return rows
if __name__ == '__main__':
    src = pathlib.Path(sys.argv[1]); out = sys.argv[2]
    with Pool(7) as pool: res = pool.map(parse, sorted(src.glob('*.pdf')))
    with open(out,'w',newline='') as f:
        w=csv.writer(f); w.writerow(['economy','annex','part','hts8','scope','page'])
        for r in res: w.writerows(r)
    for r in res: print(r[0][0] if r else '?', len(r))
