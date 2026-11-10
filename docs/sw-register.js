/* Çevrimdışı kopya: yalnızca http(s) üzerinden açıldığında. */
if ('serviceWorker' in navigator && /^https?:$/.test(location.protocol)) {
  window.addEventListener('load', () => navigator.serviceWorker.register('sw.js').catch(() => {}));
}
