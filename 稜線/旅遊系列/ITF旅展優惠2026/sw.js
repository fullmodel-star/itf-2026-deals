const CACHE_NAME = 'ridgeline-travel-itf-2026-v2';
const PRECACHE_URLS = [
  './',
  './index.html',
  './manifest.json',
  './00_%E5%AE%98%E6%96%B9%E7%B8%BD%E8%A6%BD/2026_ITF%E5%B1%95%E5%A0%B4%E5%B9%B3%E9%9D%A2%E5%9C%96.pdf'
];

self.addEventListener('install', event => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return Promise.allSettled(PRECACHE_URLS.map(u => cache.add(u)));
    })
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k.startsWith('ridgeline-travel-itf-2026-') && k !== CACHE_NAME).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  // HTML / Root navigation: Network-First with Offline Cache Fallback
  if (req.mode === 'navigate' || url.pathname.endsWith('.html') || url.pathname.endsWith('/')) {
    event.respondWith(
      fetch(req).then(res => {
        if (res && res.ok) {
          const copy = res.clone();
          caches.open(CACHE_NAME).then(c => c.put(req, copy));
        }
        return res;
      }).catch(() =>
        caches.match(req).then(r => r || caches.match('./index.html') || caches.match('./'))
      )
    );
    return;
  }

  // Static assets, screenshots (截圖_jpg), PDFs: Cache-First with Network Fallback
  event.respondWith(
    caches.match(req).then(cached => {
      if (cached) return cached;
      return fetch(req).then(res => {
        if (res && res.ok) {
          const copy = res.clone();
          caches.open(CACHE_NAME).then(c => c.put(req, copy));
        }
        return res;
      });
    })
  );
});
