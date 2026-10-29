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

data = {}
for key, name, folder, fn in SETS:
    with open(os.path.join(ROOT, folder, fn), encoding='utf-8-sig') as f:
        rows = list(csv.reader(f))
    head = [h.strip() for h in rows[0]]
    body = [r + [''] * (len(head) - len(r)) for r in rows[1:] if any(c.strip() for c in r)]
    data[key] = {'name': name, 'folder': folder, 'headers': head, 'rows': body}

blob = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
tpl = open(os.path.join(TOOLS, 'template.html'), encoding='utf-8').read().replace('__DATA__', blob)

page = tpl.replace('__SHOTS__', 'true')
index = ('<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">'
         '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
         '</head><body>' + page + '</body></html>')
open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(index)
print('index.html', os.path.getsize(os.path.join(ROOT, 'index.html')) // 1024, 'KB',
      {k: len(v['rows']) for k, v in data.items()})

if '--artifact' in sys.argv:
    out = os.path.join(TOOLS, '_artifact.html')
    open(out, 'w', encoding='utf-8').write(tpl.replace('__SHOTS__', 'false'))
    print('artifact 版本：', out)
