import { IncomingMessage } from "connect";

export const useAsyncKey = function () {
  return String(Date.now());
};

export function detectServerBaseUrl(req?: IncomingMessage | null) {
  if (!req || req === undefined) {
    return "";
  }
  if (req.headers.referer) {
    const url = new URL(req.headers.referer);
    return `${url.protocol}//${url.host}`;
  } else if (req.headers.host) {
    // TODO Socket.encrypted doesn't exist. What is needed here?
    // @ts-ignore
    const protocol = req.socket.encrypted ? "https:" : "http:";
    return `${protocol}//${req.headers.host}`;
  } else if (req.socket.remoteAddress) {
    // @ts-ignore
    const protocol = req.socket.encrypted ? "https:" : "http:";
    return `${protocol}//${req.socket.localAddress}:${req.socket.localPort}`;
  }

  return "";
}

export function uuid4() {
  // @ts-ignore
  return ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, (c) =>
    (c ^ (crypto.getRandomValues(new Uint8Array(1))[0] & (15 >> (c / 4)))).toString(16)
  );
}

// https://stackoverflow.com/questions/28876300/deep-copying-array-of-nested-objects-in-javascript
const toString = Object.prototype.toString;
export function deepCopy(obj: any) {
  let rv;

  switch (typeof obj) {
    case "object":
      if (obj === null) {
        // null => null
        rv = null;
      } else {
        switch (toString.call(obj)) {
          case "[object Array]":
            // It's an array, create a new array with
            // deep copies of the entries
            rv = obj.map(deepCopy);
            break;
          case "[object Date]":
            // Clone the date
            rv = new Date(obj);
            break;
          case "[object RegExp]":
            // Clone the RegExp
            rv = new RegExp(obj);
            break;
          // ...probably a few others
          default:
            // Some other kind of object, deep-copy its
            // properties into a new object
            rv = Object.keys(obj).reduce(function (prev, key) {
              // @ts-ignore
              prev[key] = deepCopy(obj[key]);
              return prev;
            }, {});
            break;
        }
      }
      break;
    default:
      // It's a primitive, copy via assignment
      rv = obj;
      break;
  }
  return rv;
}
