"""把各分類的 csv 嵌進 template.html，產生網站首頁 index.html。
用法：python _工具/build.py            → 產生 index.html（含截圖連結）
      python _工具/build.py --artifact → 另外產生 claude.ai 發布用版本（不含截圖連結、不含外框）
"""
import csv, json, os, sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)

SETS = [
    ('lodging', '國內住宿', '01_國內住宿', '國內住宿優惠.csv'),
    ('dining', '餐飲', '02_餐飲', '餐飲優惠.csv'),
    ('flight', '國外機票', '03_國外機票', '國外機票優惠.csv'),
    ('tour', '跟團', '04_跟團', '跟團優惠.csv'),
    ('flash', '限時搶購', '00_官方總覽', '限時搶購時程表.csv'),
    ('card', '刷卡回饋', '00_官方總覽', '刷卡回饋.csv'),
    ('booth', '參展商攤位', '00_官方總覽', '參展商名單.csv'),
]

MDS = {
    'flash': ('00_官方總覽', '官方總覽.md'),
    'lodging': ('01_國內住宿', '國內住宿分析.md'),
    'dining': ('02_餐飲', '餐飲分析.md'),
    'flight': ('03_國外機票', '國外機票分析.md'),
    'tour': ('04_跟團', '跟團分析.md'),
}

data = {}
for key, name, folder, fn in SETS:
    with open(os.path.join(ROOT, folder, fn), encoding='utf-8-sig') as f:
        rows = list(csv.reader(f))
    head = [h.strip() for h in rows[0]]
    body = [r + [''] * (len(head) - len(r)) for r in rows[1:] if any(c.strip() for c in r)]
    item = {'name': name, 'folder': folder, 'csv': fn, 'csv_path': f'{folder}\\{fn}', 'headers': head, 'rows': body}
    if key in MDS:
        mf, mfn = MDS[key]
        mp = os.path.join(ROOT, mf, mfn)
        if os.path.exists(mp):
            item['md_path'] = f'{mf}\\{mfn}'
            item['md'] = open(mp, encoding='utf-8').read()
    data[key] = item

sum_p = os.path.join(ROOT, '_先看這裡_總表.md')
if os.path.exists(sum_p):
    data['flash']['summary_path'] = '_先看這裡_總表.md'
    data['flash']['summary_md'] = open(sum_p, encoding='utf-8').read()

blob = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
tpl = open(os.path.join(TOOLS, 'template.html'), encoding='utf-8').read().replace('__DATA__', blob)

page = tpl.replace('__SHOTS__', 'true')
index = ('<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">'
         '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
         '<meta name="theme-color" content="#f4eee3">'
         '<link rel="icon" type="image/png" sizes="32x32" href="icons/favicon-32.png">'
         '<link rel="icon" type="image/png" sizes="16x16" href="icons/icon-16.png">'
         '<link rel="apple-touch-icon" sizes="180x180" href="icons/apple-touch-icon.png">'
         '<meta name="description" content="整理 2026 台灣國際旅展（11/6–11/9 南港）住宿、餐飲、機票、跟團與展場優惠，可搜尋、收藏、離線查詢。">'
         '<meta property="og:type" content="website">'
         '<meta property="og:site_name" content="ITF 旅展優惠 2026">'
         '<meta property="og:locale" content="zh_TW">'
         '<meta property="og:url" content="https://fullmodel-star.github.io/itf-2026-deals/%E7%A8%9C%E7%B7%9A/%E6%97%85%E9%81%8A%E7%B3%BB%E5%88%97/ITF%E6%97%85%E5%B1%95%E5%84%AA%E6%83%A02026/">'
         '<meta property="og:title" content="ITF 旅展優惠 2026｜南港旅展優惠一次查">'
         '<meta property="og:description" content="2026 台灣國際旅展 11/6–11/9 南港，住宿、餐飲、機票、跟團優惠一頁整理。">'
         '<meta property="og:image" content="https://fullmodel-star.github.io/itf-2026-deals/%E7%A8%9C%E7%B7%9A/%E6%97%85%E9%81%8A%E7%B3%BB%E5%88%97/ITF%E6%97%85%E5%B1%95%E5%84%AA%E6%83%A02026/og.png?v=1">'
         '<meta property="og:image:type" content="image/png">'
         '<meta property="og:image:width" content="1200">'
         '<meta property="og:image:height" content="630">'
         '<meta property="og:image:alt" content="ITF 旅展優惠 2026 — 南港旅展優惠一次查">'
         '<meta name="twitter:card" content="summary_large_image">'
         '<meta name="twitter:title" content="ITF 旅展優惠 2026｜南港旅展優惠一次查">'
         '<meta name="twitter:description" content="2026 台灣國際旅展 11/6–11/9 南港，住宿、餐飲、機票、跟團優惠一頁整理。">'
         '<meta name="twitter:image" content="https://fullmodel-star.github.io/itf-2026-deals/%E7%A8%9C%E7%B7%9A/%E6%97%85%E9%81%8A%E7%B3%BB%E5%88%97/ITF%E6%97%85%E5%B1%95%E5%84%AA%E6%83%A02026/og.png?v=1">'
         '<meta name="apple-mobile-web-app-capable" content="yes">'
         '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">'
         '<meta name="apple-mobile-web-app-title" content="稜線旅展">'
         '<link rel="manifest" href="manifest.json">'
         '</head><body>' + page + '</body></html>')
open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(index)
print('index.html', os.path.getsize(os.path.join(ROOT, 'index.html')) // 1024, 'KB',
      {k: len(v['rows']) for k, v in data.items()})

if '--artifact' in sys.argv:
    out = os.path.join(TOOLS, '_artifact.html')
    open(out, 'w', encoding='utf-8').write(tpl.replace('__SHOTS__', 'false'))
    print('artifact 版本：', out)
