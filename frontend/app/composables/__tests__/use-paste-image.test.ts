import { mount, type VueWrapper } from "@vue/test-utils";
import { afterEach, describe, expect, test, vi } from "vitest";
import { defineComponent, h, ref } from "vue";
import { useClipboardImage, usePasteImage } from "../use-paste-image";
import { toastAlert } from "../use-toast";

/** jsdom has no ClipboardEvent or DataTransfer, so build a paste that carries just what the composable reads. */
function pasteEvent(files: File[] = [], text?: string, textType = "text/plain") {
  const event = new Event("paste", { bubbles: true, cancelable: true });
  Object.defineProperty(event, "clipboardData", {
    value: {
      items: [
        ...files.map(file => ({ kind: "file", type: file.type, getAsFile: () => file })),
        ...(text ? [{ kind: "string", type: textType, getAsFile: () => null }] : []),
      ],
    },
  });
  return event;
}

// Every mounted instance keeps listening on the document, so each case must unmount its own
const mounted: VueWrapper[] = [];

function setup(enabled = true) {
  const onImage = vi.fn();
  const isEnabled = ref(enabled);
  const wrapper = mount(
    defineComponent({
      setup() {
        usePasteImage({ onImage, enabled: isEnabled });
        return () => h("div", [h("input"), h("textarea")]);
      },
    }),
    { attachTo: document.body },
  );
  mounted.push(wrapper);
  return { onImage, isEnabled, wrapper };
}

describe("usePasteImage", () => {
  afterEach(() => {
    mounted.splice(0).forEach(wrapper => wrapper.unmount());
    toastAlert.open = false;
    document.body.replaceChildren();
  });

  test("hands over a pasted image under a usable file name", () => {
    const { onImage } = setup();
    const event = pasteEvent([new File(["x"], "", { type: "image/jpeg" })]);

    document.dispatchEvent(event);

    expect(onImage).toHaveBeenCalledTimes(1);
    const file: File = onImage.mock.calls[0][0];
    expect(file.name).toBe("pasted-image.jpeg");
    expect(file.type).toBe("image/jpeg");
    expect(event.defaultPrevented).toBe(true);
  });

  test.each([
    ["image/x-ms-bmp", "", "pasted-image.bmp"],
    ["image/pjpeg", "", "pasted-image.jpeg"],
    ["image/svg+xml", "", "pasted-image.svg"],
    ["image/webp", "", "pasted-image.webp"],
    ["image/png", "Screenshot 2026-11-20.JPG", "pasted-image.JPG"],
  ])("names a %s image called %j as %s", (type, name, expected) => {
    const { onImage } = setup();

    document.dispatchEvent(pasteEvent([new File(["x"], name, { type })]));

    expect(onImage.mock.calls[0][0].name).toBe(expected);
  });

  test("leaves an image copied together with html alone inside a text field", () => {
    const { onImage, wrapper } = setup();
    const event = pasteEvent([new File(["x"], "shot.png", { type: "image/png" })], "<b>caption</b>", "text/html");

    wrapper.find("textarea").element.dispatchEvent(event);

    expect(onImage).not.toHaveBeenCalled();
    expect(event.defaultPrevented).toBe(false);
  });

  test("picks the image when the clipboard also holds other files", () => {
    const { onImage } = setup();

    document.dispatchEvent(pasteEvent([
      new File(["x"], "notes.txt", { type: "text/plain" }),
      new File(["x"], "shot.png", { type: "image/png" }),
    ]));

    expect(onImage.mock.calls[0][0].name).toBe("pasted-image.png");
  });

  test("an image pasted while a text field has focus is still taken", () => {
    const { onImage, wrapper } = setup();
    const textarea = wrapper.find("textarea").element;
    textarea.focus();

    textarea.dispatchEvent(pasteEvent([new File(["x"], "shot.png", { type: "image/png" })]));

    expect(onImage).toHaveBeenCalledTimes(1);
  });

  test("leaves an image copied together with text alone inside a text field", () => {
    const { onImage, wrapper } = setup();
    const event = pasteEvent([new File(["x"], "shot.png", { type: "image/png" })], "caption");

    wrapper.find("textarea").element.dispatchEvent(event);

    expect(onImage).not.toHaveBeenCalled();
    expect(event.defaultPrevented).toBe(false);
  });

  test("still takes an image copied together with text when no field has focus", () => {
    const { onImage } = setup();

    document.body.dispatchEvent(pasteEvent([new File(["x"], "shot.png", { type: "image/png" })], "caption"));

    expect(onImage).toHaveBeenCalledTimes(1);
  });

  test("ignores pastes made inside a dialog", () => {
    const { onImage } = setup();
    const overlay = document.createElement("div");
    overlay.className = "v-overlay";
    const button = document.createElement("button");
    overlay.append(button);
    document.body.append(overlay);

    button.dispatchEvent(pasteEvent([new File(["x"], "shot.png", { type: "image/png" })]));
    button.dispatchEvent(pasteEvent());

    expect(onImage).not.toHaveBeenCalled();
    expect(toastAlert.open).toBe(false);
  });

  test("tells the user when the clipboard has no image", () => {
    const { onImage } = setup();

    document.body.dispatchEvent(pasteEvent());

    expect(onImage).not.toHaveBeenCalled();
    expect(toastAlert.open).toBe(true);
    expect(toastAlert.color).toBe("warning");
  });

  test("leaves text pasted into a field alone, without a message", () => {
    const { onImage, wrapper } = setup();
    const event = pasteEvent();

    wrapper.find("input").element.dispatchEvent(event);

    expect(onImage).not.toHaveBeenCalled();
    expect(toastAlert.open).toBe(false);
    expect(event.defaultPrevented).toBe(false);
  });

  test("ignores pastes while disabled", () => {
    const { onImage, isEnabled } = setup(false);

    document.dispatchEvent(pasteEvent([new File(["x"], "shot.png", { type: "image/png" })]));
    expect(onImage).not.toHaveBeenCalled();
    expect(toastAlert.open).toBe(false);

    isEnabled.value = true;
    document.dispatchEvent(pasteEvent([new File(["x"], "shot.png", { type: "image/png" })]));
    expect(onImage).toHaveBeenCalledTimes(1);
  });
});

describe("useClipboardImage", () => {
  function readImage() {
    let read: () => Promise<File | null> = async () => null;
    mounted.push(mount(defineComponent({
      setup() {
        read = useClipboardImage().readImage;
        return () => h("div");
      },
    })));
    return read();
  }

  function clipboardWith(read: () => Promise<unknown>) {
    Object.defineProperty(navigator, "clipboard", { value: { read }, configurable: true });
  }

  function clipboardItem(types: Record<string, Blob>) {
    return { types: Object.keys(types), getType: async (type: string) => types[type] };
  }

  afterEach(() => {
    Reflect.deleteProperty(navigator, "clipboard");
    mounted.splice(0).forEach(wrapper => wrapper.unmount());
    toastAlert.open = false;
  });

  test("returns the image on the clipboard under a usable file name", async () => {
    clipboardWith(async () => [clipboardItem({
      "text/plain": new Blob(["x"], { type: "text/plain" }),
      "image/png": new Blob(["x"], { type: "image/png" }),
    })]);

    const file = await readImage();

    expect(file?.name).toBe("pasted-image.png");
    expect(file?.type).toBe("image/png");
    expect(toastAlert.open).toBe(false);
  });

  test("tells the user when the clipboard has no image", async () => {
    clipboardWith(async () => [clipboardItem({ "text/plain": new Blob(["x"], { type: "text/plain" }) })]);

    expect(await readImage()).toBeNull();
    expect(toastAlert.open).toBe(true);
    expect(toastAlert.text).toContain("No image found");
  });

  test("tells the user when the browser refuses clipboard access", async () => {
    clipboardWith(async () => {
      throw new DOMException("denied", "NotAllowedError");
    });

    expect(await readImage()).toBeNull();
    expect(toastAlert.open).toBe(true);
    expect(toastAlert.text).toContain("clipboard access");
  });

  test("tells the user when the browser cannot read the clipboard at all", async () => {
    expect(await readImage()).toBeNull();
    expect(toastAlert.open).toBe(true);
    expect(toastAlert.text).toContain("clipboard access");
  });
});
