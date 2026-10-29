r"""把各分類 截圖\*.png 壓成 截圖_jpg\*.jpg（網站用）。已存在且較新的會跳過。
需要 Pillow。用法：python _工具/shrink_shots.py
"""
import glob, os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAX_W = 1000
QUALITY = 70

done = skipped = 0
before = after = 0
for png in glob.glob(os.path.join(ROOT, '*', '截圖', '*.png')):
    out_dir = os.path.join(os.path.dirname(os.path.dirname(png)), '截圖_jpg')
    os.makedirs(out_dir, exist_ok=True)
    jpg = os.path.join(out_dir, os.path.splitext(os.path.basename(png))[0] + '.jpg')
    before += os.path.getsize(png)
    if os.path.exists(jpg) and os.path.getmtime(jpg) >= os.path.getmtime(png):
        skipped += 1
        after += os.path.getsize(jpg)
        continue
    im = Image.open(png).convert('RGB')
    if im.width > MAX_W:
        im = im.resize((MAX_W, round(im.height * MAX_W / im.width)), Image.LANCZOS)
    im.save(jpg, 'JPEG', quality=QUALITY, optimize=True, progressive=True)
    after += os.path.getsize(jpg)
    done += 1

print(f'壓縮 {done} 張、跳過 {skipped} 張；{before // 2**20} MB → {after // 2**20} MB')
