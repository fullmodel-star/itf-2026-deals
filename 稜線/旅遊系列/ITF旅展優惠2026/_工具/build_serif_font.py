"""把 Noto Serif TC（思源宋體）裁成「只含本 App 介面文字」的小字型 → vendor/serif-ui/

    python _工具/build_serif_font.py [NotoSerifTC-VF.ttf 的路徑，預設 C:/Windows/Fonts/NotoSerifTC-VF.ttf]
    （需要 fonttools＋brotli：pip install fonttools brotli）

2026-11-01「旅展票根」改版建立（照 604 _tools/build_serif_font.py 改）。
- 來源：Noto Serif TC（Google／Adobe，SIL OFL-1.1；全文在 vendor/serif-ui/LICENSE.txt）。
  照 OFL 精神把字型內部名稱改成「ITF Serif」，版權（nameID 0）、商標（7）、授權（13、14）原樣保留；CSS 用 font-family ITFSerif。
- 輸出兩個靜態字重：
  · itf-serif-700.woff2：_工具/template.html 全部文字（標題、分頁、分類格、按鈕用）
  · itf-serif-900.woff2：只收封面大標（.cover-title）的字＋數字
- 優惠資料（飯店名、行程名）不收，那些仍用系統黑體。**改介面文字後要重跑**（缺字會退回系統字，不會變豆腐）。
"""
import re
import sys
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = Path(__file__).resolve().parent.parent
TPL = Path(__file__).resolve().parent / "template.html"
OUTDIR = ROOT / "vendor" / "serif-ui"
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("C:/Windows/Fonts/NotoSerifTC-VF.ttf")
FAMILY = "ITF Serif"


def wanted(ch: str) -> bool:
    cp = ord(ch)
    return (0x3000 <= cp <= 0x303F or 0x3400 <= cp <= 0x9FFF or 0xFF00 <= cp <= 0xFFEF
            or 0x2010 <= cp <= 0x2027 or ch in "·×→←↑↓…｜★☆●○✓")


def texts():
    ascii_ = {chr(c) for c in range(0x20, 0x7F)}
    html = TPL.read_text(encoding="utf-8")
    body = ascii_ | {ch for ch in html if wanted(ch)}
    heads = re.findall(r'class="cover-title"[^>]*>(.*?)</h1>', html, re.S)
    if not heads:
        print("[FAIL] template.html 找不到 .cover-title"); sys.exit(1)
    title = set("0123456789") | {ch for ch in "".join(heads) if wanted(ch)}
    return "".join(sorted(body)), "".join(sorted(title))


def build(text: str, weight: int, out: Path) -> None:
    font = TTFont(SRC)
    opts = subset.Options()
    opts.layout_features = ["*"]
    opts.name_IDs = ["*"]
    opts.notdef_outline = True
    sub = subset.Subsetter(options=opts)
    sub.populate(text=text)
    sub.subset(font)
    font = instancer.instantiateVariableFont(font, {"wght": weight})
    style = "Bold" if weight == 700 else "Black"
    ps = "ITFSerif-" + style
    for rec in list(font["name"].names):
        if rec.nameID in (1, 16, 21):
            rec.string = FAMILY
        elif rec.nameID in (2, 17, 22):
            rec.string = style
        elif rec.nameID == 4:
            rec.string = f"{FAMILY} {style}"
        elif rec.nameID == 6:
            rec.string = ps
        elif rec.nameID == 3:
            rec.string = ps + ";subset-itf2026"
    font.flavor = "woff2"
    out.parent.mkdir(parents=True, exist_ok=True)
    font.save(out)
    print(f"[OK] {out.relative_to(ROOT)}：{out.stat().st_size / 1024:.0f} KB，收 {sum(1 for c in text if ord(c) > 0x7F)} 個非 ASCII 字")


def main() -> None:
    if not SRC.exists():
        print(f"[FAIL] 找不到字型 {SRC}"); sys.exit(1)
    body, title = texts()
    build(body, 700, OUTDIR / "itf-serif-700.woff2")
    build(title, 900, OUTDIR / "itf-serif-900.woff2")
    lic = OUTDIR / "LICENSE.txt"
    if not lic.exists():
        name = TTFont(SRC)["name"]
        text = name.getDebugName(13) or ""
        cr = name.getDebugName(0) or ""
        lic.write_text(f"Noto Serif TC — {cr}\n\n{text}\n\nhttps://openfontlicense.org\n", encoding="utf-8")
        print(f"[OK] {lic.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
