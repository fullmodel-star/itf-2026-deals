"""Cloudflare Pages 部署白名單：只複製網站真的會用到的檔到乾淨的 staging 資料夾。

    python _工具/build_staging.py <staging 資料夾>
    npx wrangler pages deploy <staging 資料夾> --project-name=itf-2026-deals --branch=main

2026-11-01 搬到 Cloudflare（專案 itf-2026-deals）時建立。整包部署會取代整站，漏檔＝刪掉線上檔，所以清單寫死在這裡、進版控。
- 收：index.html、manifest.json、sw.js、favicon-32.png、og.png、icons/、vendor/（含授權檔）、
      各分類資料夾的 截圖_jpg/、00_官方總覽 的展場平面圖 PDF。
- 不收：CSV、.md、README、brand.config.json、_工具/、原始 截圖/（PNG 大檔）。
  CSV 與 .md 的內容在 build.py 時已經嵌進 index.html，網頁不會另外去抓。
- 新增網頁會用到的檔案類型時，要回來加進 INCLUDE。
"""
import shutil
import sys
from pathlib import Path

APP = Path(__file__).resolve().parent.parent
FILES = ["index.html", "manifest.json", "sw.js", "favicon-32.png", "og.png",
         "00_官方總覽/2026_ITF展場平面圖.pdf"]
DIRS = ["icons", "vendor"]
SHOT_DIRS = ["00_官方總覽", "01_國內住宿", "02_餐飲", "03_國外機票", "04_跟團"]


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    out = Path(sys.argv[1])
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    n = 0
    for f in FILES:
        src = APP / f
        if not src.exists():
            raise SystemExit(f"[FAIL] 缺檔：{f}")
        (out / f).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, out / f)
        n += 1
    for d in DIRS + [f"{s}/截圖_jpg" for s in SHOT_DIRS]:
        src = APP / d
        if not src.is_dir():
            raise SystemExit(f"[FAIL] 缺資料夾：{d}")
        for p in src.rglob("*"):
            if p.is_file():
                dst = out / p.relative_to(APP)
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, dst)
                n += 1
    size = sum(p.stat().st_size for p in out.rglob("*") if p.is_file())
    big = [p for p in out.rglob("*") if p.is_file() and p.stat().st_size > 25 * 1024 * 1024]
    if big:
        raise SystemExit(f"[FAIL] 超過 Cloudflare 單檔 25MB：{big}")
    print(f"[OK] {n} 個檔，{size / 1024 / 1024:.1f} MB → {out}")


if __name__ == "__main__":
    main()
