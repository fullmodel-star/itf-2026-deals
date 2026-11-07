"""把每一筆優惠連到 00_官方總覽/商家總表.csv 的「商家編號」。

    python _工具/link_merchants.py          # 補上或更新各表的「商家編號」欄
    python _工具/link_merchants.py --check  # 只檢查（build.py 會呼叫），有對不上的就 exit 1

2026-11-04 建立。原本同一家公司在各表的寫法不一（老爺有 12 種寫法），畫面只能靠名稱猜。
現在以商家總表為準：
- 總表兩層：「參展單位」＝逛展要去的那一攤（集團或單一飯店、航空、旅行社）；「旗下館」＝其下的個別飯店，上層編號指回參展單位。
- 「對應名稱」欄列出各表出現過的寫法（；分隔）。新資料用了新寫法，就把那個寫法加進對應名稱。
- 比對順序：名稱完全相同（去掉【2025參考】這類標註）→ 對不到時用攤位號找參展單位（會列出來請人確認）→ 都對不到就報錯。
- 機票：航空欄是具體航空公司就連航空；寫「—／依產品／多家／未公布」的連銷售者（旅行社或平台）。
"""
import csv
import re
import sys
from pathlib import Path

APP = Path(__file__).resolve().parent.parent
MASTER = APP / '00_官方總覽' / '商家總表.csv'
COL = '商家編號'
GENERIC_AIR = {'', '—', '依產品', '多家', '未公布'}
# 表、名稱欄（可多個，依序取第一個有意義的）、攤位欄
TABLES = [
    ('01_國內住宿/國內住宿優惠.csv', ['飯店名稱'], '攤位號碼'),
    ('02_餐飲/餐飲優惠.csv', ['飯店/品牌'], '攤位號碼'),
    ('03_國外機票/國外機票優惠.csv', ['航空', '銷售者'], '攤位號碼'),
    ('04_跟團/跟團優惠.csv', ['旅行社'], '攤位號碼'),
    ('05_溫泉票券/溫泉票券優惠.csv', ['業者'], '攤位號碼'),
    ('00_官方總覽/限時搶購時程表.csv', ['商家'], '攤位'),
    ('00_官方總覽/參展商名單.csv', ['參展單位'], '攤位號'),
]


def clean(v):
    return re.sub(r'【[^】]*】', '', v or '').strip()


def booth_code(v):
    m = re.match(r'^\s*([A-Z])-?(\d{2,4})', v or '')
    return m.group(1) + m.group(2) if m else ''


def load_master():
    rows = list(csv.DictReader(open(MASTER, encoding='utf-8-sig')))
    ids = {r[COL]: r for r in rows}
    alias, errs = {}, []
    for r in rows:
        for a in [r['商家名稱']] + r['對應名稱'].split('；'):
            a = clean(a)
            if not a:
                continue
            if a in alias and alias[a] != r[COL]:
                errs.append(f'對應名稱重複：「{a}」同時屬於 {alias[a]} 和 {r[COL]}')
            alias[a] = r[COL]
        if r['上層編號'] and r['上層編號'] not in ids:
            errs.append(f'{r[COL]} 的上層編號 {r["上層編號"]} 不存在')
    booth = {}
    for r in rows:
        c = booth_code(r['攤位'])
        if c and not r['上層編號']:
            booth.setdefault(c, r[COL])
    return rows, ids, alias, booth, errs


def raw_name(row, names):
    for n in names:
        v = clean(row.get(n, ''))
        if n == '航空' and v in GENERIC_AIR:
            continue
        if v:
            return v
    return ''


def main():
    check = '--check' in sys.argv
    rows, ids, alias, booth, errs = load_master()
    by_booth, total = [], 0
    for rel, names, bcol in TABLES:
        p = APP / rel
        text = p.read_bytes().decode('utf-8-sig')
        nl = '\r\n' if '\r\n' in text else '\n'
        data = list(csv.reader(text.splitlines()))
        head, body = data[0], data[1:]
        dicts = [dict(zip(head, r)) for r in body]
        new = []
        for i, d in enumerate(dicts, 2):
            name = raw_name(d, names)
            mid = alias.get(name)
            if not mid and booth_code(d.get(bcol, '')) in booth:
                mid = booth[booth_code(d.get(bcol, ''))]
                by_booth.append(f'{rel} 第{i}列「{name}」→ 以攤位 {d.get(bcol, "")} 對到 {mid} {ids[mid]["商家名稱"]}')
            if rel.endswith('參展商名單.csv') and mid:
                mid = ids[mid]['上層編號'] or mid   # 參展單位一律連到上層
            if not mid:
                errs.append(f'{rel} 第{i}列「{name}」對不到商家總表（請把這個寫法加進某家商家的「對應名稱」）')
                mid = ''
            if check and d.get(COL, '') != mid:
                errs.append(f'{rel} 第{i}列的商家編號是「{d.get(COL, "")}」，應為「{mid}」（請執行 python _工具/link_merchants.py）')
            new.append(mid)
        total += len(body)
        if check:
            continue
        if COL not in head:
            at = head.index(names[0]) + 1
            head.insert(at, COL)
            for r, m in zip(body, new):
                r.insert(at, m)
        else:
            at = head.index(COL)
            for r, m in zip(body, new):
                r[at] = m
        with open(p, 'w', encoding='utf-8-sig', newline='') as f:
            csv.writer(f, lineterminator=nl).writerows([head] + body)
    for m in by_booth:
        print('[確認]', m)
    if errs:
        for e in errs:
            print('[FAIL]', e)
        sys.exit(1)
    print(f'[OK] {total} 筆資料都已連到商家總表（{len(rows)} 家）')


if __name__ == '__main__':
    main()
