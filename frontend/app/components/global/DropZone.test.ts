import { mount } from "@vue/test-utils";
import { describe, expect, test } from "vitest";
import { nextTick } from "vue";
import DropZone from "./DropZone.vue";

/**
 * Builds a drop carrying the given drag-data types. `useDropZone` reads `items` to decide the
 * drop is valid and `files` to decide whether anything was actually attached, so a fake has to
 * provide both -- jsdom has no real DataTransfer.
 */
function dropEvent(types: Record<string, string>, files: File[] = []) {
  const event = new Event("drop", { bubbles: true, cancelable: true });

  Object.defineProperty(event, "dataTransfer", {
    value: {
      items: [
        ...files.map(file => ({ kind: "file", type: file.type })),
        ...Object.keys(types).map(type => ({ kind: "string", type })),
      ],
      files,
      dropEffect: "none",
      getData: (type: string) => types[type] ?? "",
    },
  });

  return event;
}

async function drop(types: Record<string, string>, files: File[] = []) {
  const wrapper = mount(DropZone);

  // Vue assigns the template ref in a post-render effect, and useDropZone's listener is only
  // attached on the flush after that. Dispatching any sooner hits an element with no listener.
  await nextTick();

  wrapper.element.dispatchEvent(dropEvent(types, files));
  return wrapper;
}

describe("DropZone", () => {
  test("emits the url of an image dragged out of another tab", async () => {
    const wrapper = await drop({ "text/uri-list": "https://example.test/pancakes.png" });

    expect(wrapper.emitted("drop-url")).toEqual([["https://example.test/pancakes.png"]]);
    expect(wrapper.emitted("drop")).toBeUndefined();
  });

  test("prefers an attached file over the url", async () => {
    const file = new File([""], "pancakes.png", { type: "image/png" });
    const wrapper = await drop({ "text/uri-list": "https://example.test/pancakes.png" }, [file]);

    expect(wrapper.emitted("drop")).toEqual([[[file]]]);
    expect(wrapper.emitted("drop-url")).toBeUndefined();
  });

  test("skips comment lines and takes the first usable url", async () => {
    const wrapper = await drop({
      "text/uri-list": "# a comment\nhttps://example.test/first.png\nhttps://example.test/second.png",
    });

    expect(wrapper.emitted("drop-url")).toEqual([["https://example.test/first.png"]]);
  });

  test("accepts plain http", async () => {
    const wrapper = await drop({ "text/uri-list": "http://example.test/pancakes.png" });

    expect(wrapper.emitted("drop-url")).toEqual([["http://example.test/pancakes.png"]]);
  });

  test.each([
    ["javascript:alert(1)"],
    ["data:image/png;base64,iVBORw0KGgo="],
    ["file:///etc/passwd"],
    ["not a url at all"],
  ])("ignores %s", async (uri) => {
    const wrapper = await drop({ "text/uri-list": uri });

    expect(wrapper.emitted("drop-url")).toBeUndefined();
    expect(wrapper.emitted("drop")).toBeUndefined();
  });

  test("ignores a drop carrying nothing usable", async () => {
    const wrapper = await drop({ "text/plain": "just some text" });

    expect(wrapper.emitted("drop-url")).toBeUndefined();
    expect(wrapper.emitted("drop")).toBeUndefined();
  });

  test("does not dig a url out of text/html markup", async () => {
    // Deliberate: parsing untrusted markup to find an <img> is not worth the sink it creates,
    // and every major browser fills in text/uri-list when an image is dragged.
    const wrapper = await drop({ "text/html": "<img src=\"https://example.test/pancakes.png\">" });

    expect(wrapper.emitted("drop-url")).toBeUndefined();
  });
});
