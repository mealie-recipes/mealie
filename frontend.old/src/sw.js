/* eslint-disable no-undef, no-underscore-dangle, no-restricted-globals */

self.addEventListener("install", event => {
  event.waitUntil(preLoad());
});

var preLoad = async () => {
  console.log("Installing web app");
  const cache = await caches.open("offline");
  console.log("caching index and important routes");
  return await cache.addAll(["/", "/recipes/all"]);
};

self.addEventListener("fetch", event => {
  event.respondWith(
    checkResponse(event.request).catch(() => {
      return returnFromCache(event.request);
    })
  );
  event.waitUntil(addToCache(event.request));
});

var checkResponse = request => {
  return new Promise(function(fulfill, reject) {
    fetch(request).then(function(response) {
      if (response.status !== 404) {
        fulfill(response);
      } else {
        reject();
      }
    }, reject);
  });
};

var addToCache = async request => {
  const cache = await caches.open("offline");
  const response = await fetch(request);
  console.log(response.url + " was cached");
  return await cache.put(request, response);
};

var returnFromCache = async request => {
  const cache = await caches.open("offline");
  const matching = await cache.match(request);
  if (!matching || matching.status == 404) {
    return cache.match("offline.html");
  } else {
    return matching;
  }
};

// This is the code piece that GenerateSW mode can't provide for us.
// This code listens for the user's confirmation to update the app.
self.addEventListener("message", e => {
  if (!e.data) {
    return;
  }

  switch (e.data) {
    case "skipWaiting":
      self.skipWaiting();
      break;
    default:
      // NOOP
      break;
  }
});

workbox.core.clientsClaim(); // Vue CLI 4 and Workbox v4, else
// workbox.clientsClaim(); // Vue CLI 3 and Workbox v3.

// The precaching code provided by Workbox.
self.__precacheManifest = [].concat(self.__precacheManifest || []);
// workbox.precaching.suppressWarnings(); // Only used with Vue CLI 3 and Workbox v3.
workbox.precaching.precacheAndRoute(self.__precacheManifest, {});
