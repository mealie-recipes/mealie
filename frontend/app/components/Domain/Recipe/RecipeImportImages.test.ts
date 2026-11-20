import { flushPromises, mount, type VueWrapper } from "@vue/test-utils";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import RecipeImportImages from "./RecipeImportImages.vue";

const mocks = vi.hoisted(() => ({ readImage: vi.fn() }));

vi.mock("~/composables/use-paste-image", async (importOriginal) => {
  const original = await importOriginal<typeof import("~/composables/use-paste-image")>();
  return { ...original, useClipboardImage: () => ({ readImage: mocks.readImage }) };
});

function pasteImage(name = "shot.png") {
  const file = new File(["x"], name, { type: "image/png" });
  const event = new Event("paste", { bubbles: true, cancelable: true });
  Object.defineProperty(event, "clipboardData", {
    value: { items: [{ kind: "file", type: file.type, getAsFile: () => file }] },
  });
  document.dispatchEvent(event);
}

describe("RecipeImportImages paste", () => {
  let wrapper: VueWrapper;
  let images: (Blob | File)[];

  function mountImages(disabled = false) {
    images = [];
    wrapper = mount(RecipeImportImages, {
      props: {
        "disabled": disabled,
        "modelValue": images,
        "onUpdate:modelValue": (value: (Blob | File)[]) => {
          images = value;
          wrapper.setProps({ modelValue: value });
        },
      },
      attachTo: document.body,
      global: {
        stubs: { "AppButtonUpload": true, "ImageCropper": true, "v-row": true, "v-col": true, "v-btn": { template: "<button><slot /></button>" }, "v-icon": true },
        mocks: { $globals: { icons: { check: "mdi-check", fileImage: "mdi-file-image", contentPaste: "mdi-content-paste" } } },
      },
    });
  }

  beforeEach(() => {
    let count = 0;
    URL.createObjectURL = vi.fn(() => `blob:preview-${count++}`);
    URL.revokeObjectURL = vi.fn();
  });

  afterEach(() => {
    wrapper.unmount();
  });

  test("adds a pasted screenshot to the images", async () => {
    mountImages();

    pasteImage();
    await flushPromises();

    expect(images).toHaveLength(1);
    expect((images[0] as File).name).toBe("pasted-image.png");
  });

  test("keeps adding with every paste", async () => {
    mountImages();

    pasteImage();
    await flushPromises();
    pasteImage();
    await flushPromises();

    expect(images).toHaveLength(2);
  });

  test("adds the clipboard image when the paste button is clicked", async () => {
    mocks.readImage.mockResolvedValue(new File(["x"], "pasted-image.png", { type: "image/png" }));
    mountImages();

    await wrapper.findAll("button").find(b => b.text() === "Paste")!.trigger("click");
    await flushPromises();

    expect(images).toHaveLength(1);
    expect((images[0] as File).name).toBe("pasted-image.png");
  });

  test("adds nothing when the clipboard has no image", async () => {
    mocks.readImage.mockResolvedValue(null);
    mountImages();

    await wrapper.findAll("button").find(b => b.text() === "Paste")!.trigger("click");
    await flushPromises();

    expect(images).toHaveLength(0);
  });

  test("ignores pastes while disabled", async () => {
    mountImages(true);

    pasteImage();
    await flushPromises();

    expect(images).toHaveLength(0);
  });
});
