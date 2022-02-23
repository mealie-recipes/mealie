import { IncomingMessage } from "connect";
import { useDark } from "@vueuse/core";
import { useContext } from "@nuxtjs/composition-api";

export const useToggleDarkMode = () => {
  const isDark = useDark();
  const { $vuetify } = useContext();

  function toggleDark() {
    isDark.value = !$vuetify.theme.dark;
    $vuetify.theme.dark = !$vuetify.theme.dark;
  }

  return toggleDark;
};

export const useAsyncKey = function () {
  return String(Date.now());
};

export const titleCase = function (str: string) {
  return str
    .split(" ")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
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
    // @ts-ignore See above
    const protocol = req.socket.encrypted ? "https:" : "http:";
    return `${protocol}//${req.headers.host}`;
  } else if (req.socket.remoteAddress) {
    // @ts-ignore See above
    const protocol = req.socket.encrypted ? "https:" : "http:";
    return `${protocol}//${req.socket.localAddress || ""}:${req.socket.localPort || ""}`;
  }

  return "";
}

export function uuid4() {
  return "10000000-1000-4000-8000-100000000000".replace(/[018]/g, (c) =>
    (parseInt(c) ^ (crypto.getRandomValues(new Uint8Array(1))[0] & (15 >> (parseInt(c) / 4)))).toString(16)
  );
}

// https://stackoverflow.com/questions/28876300/deep-copying-array-of-nested-objects-in-javascript
export function deepCopy<T>(obj: T): T {
  let rv;

  switch (typeof obj) {
    case "object":
      if (obj === null) {
        // null => null
        rv = null;
      } else {
        switch (Object.prototype.toString.call(obj)) {
          case "[object Array]":
            // It's an array, create a new array with
            // deep copies of the entries
            rv = (obj as unknown as Array<unknown>).map(deepCopy);
            break;
          case "[object Date]":
            // Clone the date
            rv = new Date(obj as unknown as Date);
            break;
          case "[object RegExp]":
            // Clone the RegExp
            rv = new RegExp(obj as unknown as RegExp);
            break;
          // ...probably a few others
          default:
            // Some other kind of object, deep-copy its
            // properties into a new object
            rv = Object.keys(obj).reduce(function (prev, key) {
              // @ts-ignore This is hard to make type-safe
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
  return rv as T;
}
