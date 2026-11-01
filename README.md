# 稜線 App

## 旅遊系列

- [ITF 旅展優惠 2026](稜線/旅遊系列/ITF旅展優惠2026/README.md)：旅展優惠查詢、收藏與離線瀏覽。

網址：https://itf-2026-deals.pages.dev/ （Cloudflare Pages，專案 `itf-2026-deals`）。

App 完整原始檔、資料、截圖及建置工具均放在 `稜線/旅遊系列/ITF旅展優惠2026/`。根目錄 `index.html` 會把舊的 GitHub Pages 網址自動轉到 Cloudflare；`sw.js` 用於讓舊版快取退役。部署步驟見 App 資料夾的 README。

## 重新建置

```powershell
python "稜線/旅遊系列/ITF旅展優惠2026/_工具/build.py"
```

在專案根目錄啟動本機網頁伺服器即可預覽。
