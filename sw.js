// 舊入口的過渡 worker，讓已安裝的舊版重新取得品牌入口。
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', event => event.waitUntil((async () => {
  await caches.delete('itf-2026-app-v1');
  await self.clients.claim();
  await self.registration.unregister();
})()));
