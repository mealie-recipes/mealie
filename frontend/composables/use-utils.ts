import { useDark, useToggle } from "@vueuse/core";
import type { FilterFunction } from "vuetify";

export const useToggleDarkMode = () => {
  const isDark = useDark();
  const toggleDark = useToggle(isDark);

  return () => toggleDark();
};

export const useAsyncKey = function () {
  return `${Date.now()}-${Math.random().toString(36).slice(2)}`;
};

export const titleCase = function (str: string) {
  return str
    .split(" ")
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
};

const replaceAllBuilder = (map: Map<string, string>): ((str: string) => string) => {
  const re = new RegExp(Array.from(map.keys()).join("|"), "gi");
  return str => str.replace(re, matched => map.get(matched)!);
};

const normalizeLigatures = replaceAllBuilder(new Map([
  ["œ", "oe"],
  ["æ", "ae"],
  ["ĳ", "ij"],
  ["ﬀ", "ff"],
  ["ﬁ", "fi"],
  ["ﬂ", "fl"],
  ["ﬆ", "st"],
]));

export const normalize = (str: string) => {
  if (!str) {
    return "";
  }

  let normalized = str.normalize("NFKD").toLowerCase();
  normalized = normalized.replace(/\p{Diacritic}/gu, "");
  normalized = normalizeLigatures(normalized);
  return normalized;
};

export const normalizeFilter: FilterFunction = (value: string, query: string) => {
  const normalizedValue = normalize(value);
  const normalizeQuery = normalize(query);
  return normalizedValue.includes(normalizeQuery);
};

export function uuid4() {
  return "10000000-1000-4000-8000-100000000000".replace(/[018]/g, c =>
    (parseInt(c) ^ (crypto.getRandomValues(new Uint8Array(1))[0] & (15 >> (parseInt(c) / 4)))).toString(16),
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
      }
      else {
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

export function downloadAsJson(data: any, filename: string) {
  const content = JSON.stringify(data);
  const blob = new Blob([content], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.download = filename;
  a.href = url;
  a.click();
  URL.revokeObjectURL(url);
}
