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
    ["file:///etc/passwd"],
    ["not a url at all"],
  ])("never fetches or uploads %s", async (uri) => {
    const wrapper = await drop({ "text/uri-list": uri });

    expect(wrapper.emitted("drop-url")).toBeUndefined();
    expect(wrapper.emitted("drop")).toBeUndefined();
    expect(wrapper.emitted("drop-unsupported")).toHaveLength(1);
  });

  test("takes the image from the markup, not the link wrapping it", async () => {
    // Google Images (and any thumbnail grid) wraps the picture in a link, so text/uri-list is
    // the page URL and only the markup names the actual image.
    const wrapper = await drop({
      "text/html": "<a href=\"https://www.google.com/imgres?q=pancakes\">"
        + "<img src=\"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9Gc\"></a>",
      "text/uri-list": "https://www.google.com/imgres?q=pancakes",
    });

    expect(wrapper.emitted("drop-url")).toEqual([["https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9Gc"]]);
  });

  test("unescapes entities in the markup's url", async () => {
    const wrapper = await drop({
      "text/html": "<img src=\"https://example.test/i?q=tbn&amp;s=10&amp;w=20\">",
    });

    expect(wrapper.emitted("drop-url")).toEqual([["https://example.test/i?q=tbn&s=10&w=20"]]);
  });

  test("is not fooled by a data-src attribute", async () => {
    const wrapper = await drop({
      "text/html": "<img data-src=\"https://example.test/placeholder.gif\" src=\"https://example.test/real.png\">",
    });

    expect(wrapper.emitted("drop-url")).toEqual([["https://example.test/real.png"]]);
  });

  test("falls back to text/uri-list when the markup has no image", async () => {
    const wrapper = await drop({
      "text/html": "<a href=\"https://example.test/page\">a link</a>",
      "text/uri-list": "https://example.test/pancakes.png",
    });

    expect(wrapper.emitted("drop-url")).toEqual([["https://example.test/pancakes.png"]]);
  });

  test("converts a data: url into a file for the normal upload path", async () => {
    // A 1x1 gif. Nothing can fetch a data: url on our behalf, but the bytes are already here.
    const gif = "data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==";
    const wrapper = await drop({ "text/uri-list": gif });

    expect(wrapper.emitted("drop-url")).toBeUndefined();

    const dropped = wrapper.emitted("drop")?.[0]?.[0] as File[];
    expect(dropped).toHaveLength(1);
    expect(dropped[0].type).toBe("image/gif");
    expect(dropped[0].name).toBe("image.gif");
    expect(dropped[0].size).toBeGreaterThan(0);
  });

  test("reports a blob: url as unusable rather than doing nothing", async () => {
    // Blob urls resolve only inside the origin that created them, so there is nothing to read.
    const wrapper = await drop({ "text/uri-list": "blob:https://www.google.com/abc-123" });

    expect(wrapper.emitted("drop-unsupported")).toHaveLength(1);
    expect(wrapper.emitted("drop-url")).toBeUndefined();
    expect(wrapper.emitted("drop")).toBeUndefined();
  });

  test("stays quiet when the drop holds nothing image-like at all", async () => {
    const wrapper = await drop({ "text/plain": "just some text" });

    expect(wrapper.emitted("drop-unsupported")).toBeUndefined();
  });
});
