import { flushPromises, mount } from "@vue/test-utils";
import { beforeEach, describe, expect, test, vi } from "vitest";
import RecipeImageUploadBtn from "./RecipeImageUploadBtn.vue";

const mocks = vi.hoisted(() => ({ readImage: vi.fn() }));

vi.mock("~/composables/api", () => ({ useUserApi: () => ({ recipes: {} }) }));
vi.mock("~/composables/use-paste-image", () => ({ useClipboardImage: () => ({ readImage: mocks.readImage }) }));

function mountButton() {
  return mount(RecipeImageUploadBtn, {
    props: { slug: "pancakes" },
    global: {
      mocks: { $globals: { icons: { fileImage: "mdi-file-image", contentPaste: "mdi-content-paste", alertCircle: "mdi-alert" } } },
      stubs: {
        "BaseDialog": true,
        "BaseButton": true,
        "AppButtonUpload": true,
        "v-menu": { template: "<div><slot /></div>" },
        "v-card": { template: "<div><slot /></div>" },
        "v-card-title": { template: "<div><slot /></div>" },
        "v-card-text": { template: "<div><slot /></div>" },
        "v-text-field": true,
        "v-icon": true,
        "v-btn": { props: ["loading"], template: "<button><slot /></button>" },
      },
    },
  });
}

describe("RecipeImageUploadBtn paste button", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test("hands the clipboard image to the page", async () => {
    const image = new File(["x"], "pasted-image.png", { type: "image/png" });
    mocks.readImage.mockResolvedValue(image);
    const wrapper = mountButton();

    await wrapper.findAll("button").find(b => b.text() === "Paste")!.trigger("click");
    await flushPromises();

    expect(wrapper.emitted("clipboard")).toEqual([[image]]);
  });

  test("emits nothing when the clipboard has no image", async () => {
    mocks.readImage.mockResolvedValue(null);
    const wrapper = mountButton();

    await wrapper.findAll("button").find(b => b.text() === "Paste")!.trigger("click");
    await flushPromises();

    expect(wrapper.emitted("clipboard")).toBeUndefined();
  });
});
