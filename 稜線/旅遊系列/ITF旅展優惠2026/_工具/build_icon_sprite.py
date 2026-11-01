"""把 _工具/template.html 用到的 Tabler 線條圖示（MIT）做成內嵌 <svg> sprite，寫進 template.html 的標記之間。

    npm pack @tabler/icons@3.49.0
    python _工具/build_icon_sprite.py [<解開後的 package 資料夾 或 .tgz 檔>]

2026-11-01「旅展票根」改版建立（照 605 的腳本改）：操作類圖示（搜尋、篩選、導航、收藏、分頁…）一律用同一套
線條圖示，取代原本混用的彩色 emoji；菜系仍用 Fluent Emoji 彩色食物圖（內容，不是操作）。
- 分三層系統管理：第一層（系統/頂層工具）、第二層（分類/搜尋/篩選/導覽）、第三層（卡片/標籤/狀態）。
- 授權全文複製到 vendor/tabler-icons/LICENSE.txt（部署白名單已列）。
- 寫進 template.html 的標記之間（重跑 build.py 後進 index.html）；二進位讀寫，其他位元組不動。
"""
import io
import json
import os
import re
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = Path(__file__).resolve().parent / "template.html"
START = b"<!-- TABLER_SPRITE_START"
END = b"<!-- TABLER_SPRITE_END -->"

# (sprite id, Tabler 檔名, 樣式)
ICONS = [
    # 第一層：品牌頂層導覽與系統控制
    ("device-mobile", "device-mobile", "outline"),
    ("wifi-off", "wifi-off", "outline"),
    ("sun", "sun", "outline"),
    ("moon", "moon", "outline"),
    ("sun-moon", "sun-moon", "outline"),
    ("x", "x", "outline"),

    # 第二層：分頁分類導航與互動操作控制
    ("home", "home", "outline"),
    ("flame", "flame", "outline"),
    ("bed", "bed", "outline"),
    ("tools-kitchen-2", "tools-kitchen-2", "outline"),
    ("plane", "plane", "outline"),
    ("bus", "bus", "outline"),
    ("star", "star", "outline"),
    ("star-filled", "star", "filled"),
    ("arrow", "arrow-right", "outline"),
    ("adjustments", "adjustments", "outline"),
    ("share", "share", "outline"),
    ("check", "check", "outline"),
    ("users", "users", "outline"),
    ("book", "book", "outline"),
    ("chevron-down", "chevron-down", "outline"),
    ("photo", "photo", "outline"),
    ("map", "map", "outline"),
    ("file-spreadsheet", "file-spreadsheet", "outline"),

    # 第三層：資料卡片細部層與內容屬性徽章
    ("map-pin", "map-pin", "outline"),
    ("copy", "copy", "outline"),
    ("tag", "tag", "outline"),
    ("coffee", "coffee", "outline"),
    ("luggage", "luggage", "outline"),
    ("alert-triangle", "alert-triangle", "outline"),
    ("award", "award", "outline"),
    ("refresh", "refresh", "outline"),
]


def load_from_dir(pkg: Path, sid: str, name: str, style: str) -> str:
    svg = (pkg / "icons" / style / f"{name}.svg").read_text(encoding="utf-8")
    return build_symbol(sid, style, svg)


def load_from_tar(tar: tarfile.TarFile, sid: str, name: str, style: str) -> str:
    f = tar.extractfile(f"package/icons/{style}/{name}.svg")
    if not f:
        raise SystemExit(f"[FAIL] tar 找不到 package/icons/{style}/{name}.svg")
    svg = f.read().decode("utf-8")
    return build_symbol(sid, style, svg)


def build_symbol(sid: str, style: str, svg: str) -> str:
    paths = re.findall(r"<path[^>]*/>", svg)
    paths = [p for p in paths if 'stroke="none"' not in p]
    if not paths:
        raise SystemExit(f"[FAIL] {sid} 沒有可用的 path")
    if style == "filled":
        attrs = 'fill="currentColor" stroke="none"'
    else:
        attrs = 'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
    body = "".join(p.replace(" />", "/>") for p in paths)
    return f'<symbol id="ti-{sid}" viewBox="0 0 24 24" {attrs}>{body}</symbol>'


def main() -> None:
    pkg_arg = sys.argv[1] if len(sys.argv) > 1 else None
    tar_obj = None
    pkg_path = None
    version = "3.49.0"
    license_bytes = None

    if pkg_arg and Path(pkg_arg).is_dir():
        pkg_path = Path(pkg_arg)
        pkg_json = json.loads((pkg_path / "package.json").read_text(encoding="utf-8"))
        version = pkg_json.get("version", "3.49.0")
        lic_file = pkg_path / "LICENSE"
        if lic_file.exists():
            license_bytes = lic_file.read_bytes()
    else:
        tgz_candidates = []
        if pkg_arg and Path(pkg_arg).is_file():
            tgz_candidates.append(Path(pkg_arg))
        tgz_candidates.append(Path(tempfile.gettempdir()) / "tabler-icons-3.49.0.tgz")
        tgz_candidates.append(ROOT / "tabler-icons-3.49.0.tgz")

        chosen_tgz = None
        for cand in tgz_candidates:
            if cand.exists():
                chosen_tgz = cand
                break
        if not chosen_tgz:
            raise SystemExit("[FAIL] 找不到 @tabler/icons 來源，請提供解開的資料夾或 .tgz 路徑")
        tar_obj = tarfile.open(chosen_tgz, "r:gz")
        try:
            pkg_json_file = tar_obj.extractfile("package/package.json")
            if pkg_json_file:
                version = json.loads(pkg_json_file.read().decode("utf-8")).get("version", "3.49.0")
            lic_tar = tar_obj.extractfile("package/LICENSE")
            if lic_tar:
                license_bytes = lic_tar.read()
        except Exception as e:
            print("讀取 tar 資訊警告：", e)

    if pkg_path:
        syms = "".join(load_from_dir(pkg_path, *i) for i in ICONS)
    else:
        syms = "".join(load_from_tar(tar_obj, *i) for i in ICONS)

    block = (f"<!-- TABLER_SPRITE_START Tabler Icons {version}（MIT，授權見 vendor/tabler-icons/LICENSE.txt）；"
             f"由 _工具/build_icon_sprite.py 產生，勿手改 -->\r\n"
             f'<svg xmlns="http://www.w3.org/2000/svg" style="position:absolute;width:0;height:0;overflow:hidden" aria-hidden="true" focusable="false">'
             f"{syms}</svg>\r\n").encode("utf-8")

    raw = HTML.read_bytes()
    a = raw.find(START)
    b = raw.find(END)
    if a < 0 or b < a:
        raise SystemExit("[FAIL] template.html 找不到 TABLER_SPRITE 標記")
    new = raw[:a] + block + raw[b:]
    HTML.write_bytes(new)

    if license_bytes:
        lic = ROOT / "vendor" / "tabler-icons" / "LICENSE.txt"
        lic.parent.mkdir(parents=True, exist_ok=True)
        lic.write_bytes(license_bytes)

    print(f"OK Tabler {version}：{len(ICONS)} 個圖示寫進 template.html（sprite {len(block)} bytes）")


if __name__ == "__main__":
    main()
