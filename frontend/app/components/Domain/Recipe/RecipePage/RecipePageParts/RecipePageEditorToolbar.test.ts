import { flushPromises, mount, type VueWrapper } from "@vue/test-utils";
import { defineComponent, ref } from "vue";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import RecipePageEditorToolbar from "./RecipePageEditorToolbar.vue";
import type { RecipeOut } from "~/lib/api/types/recipe";

const mocks = vi.hoisted(() => ({ updateImage: vi.fn() }));

vi.mock("~/composables/api", () => ({
  useUserApi: () => ({ recipes: { updateImage: mocks.updateImage } }),
}));
vi.mock("~/composables/recipe-page/shared-state", () => ({
  usePageUser: () => ({ user: { id: "user-1", admin: true } }),
  usePageState: () => ({ imageKey: ref(0) }),
}));
vi.mock("~/composables/store/use-user-store", () => ({
  useUserStore: () => ({ store: ref([]) }),
}));
vi.mock("~/composables/store", () => ({
  useHouseholdStore: () => ({ store: ref([]) }),
}));
vi.mock("~/components/Domain/Recipe/RecipeImageUploadBtn.vue", () => ({ default: { render: () => null } }));
vi.mock("~/components/Domain/Recipe/RecipeSettingsMenu.vue", () => ({ default: { render: () => null } }));
vi.mock("~/components/Domain/User/UserAvatar.vue", () => ({ default: { render: () => null } }));

// Shows its content while open and exposes the confirm and close events a real dialog emits.
const BaseDialogStub = defineComponent({
  props: { modelValue: Boolean },
  emits: ["update:modelValue", "confirm", "close"],
  template: `
    <div v-if="modelValue" data-test="paste-dialog">
      <slot />
      <button data-test="confirm" @click="$emit('confirm'); $emit('update:modelValue', false); $emit('close')" />
      <button data-test="cancel" @click="$emit('update:modelValue', false); $emit('close')" />
    </div>
  `,
});

function pasteImage() {
  const file = new File(["x"], "shot.png", { type: "image/png" });
  const event = new Event("paste", { bubbles: true, cancelable: true });
  Object.defineProperty(event, "clipboardData", {
    value: { items: [{ kind: "file", type: file.type, getAsFile: () => file }] },
  });
  document.dispatchEvent(event);
  return event;
}

describe("RecipePageEditorToolbar paste", () => {
  let wrapper: VueWrapper;

  beforeEach(() => {
    vi.clearAllMocks();
    // jsdom has no object URLs
    URL.createObjectURL = vi.fn(() => "blob:preview");
    URL.revokeObjectURL = vi.fn();
    mocks.updateImage.mockResolvedValue({ data: { image: "new-image" }, error: null });

    const recipe = { slug: "pancakes", userId: "user-1", settings: {}, image: "old-image" } as unknown as RecipeOut;
    wrapper = mount(RecipePageEditorToolbar, {
      props: { modelValue: recipe },
      attachTo: document.body,
      global: {
        mocks: { $globals: { icons: { fileImage: "mdi-file-image" } } },
        stubs: {
          "BaseDialog": BaseDialogStub,
          "v-select": true,
          "v-spacer": true,
          "v-card-text": { template: "<div><slot /></div>" },
          "v-img": true,
        },
      },
    });
  });

  afterEach(() => {
    wrapper.unmount();
  });

  test("shows a preview instead of replacing the image right away", async () => {
    pasteImage();
    await flushPromises();

    expect(wrapper.find("[data-test=paste-dialog]").exists()).toBe(true);
    expect(mocks.updateImage).not.toHaveBeenCalled();
  });

  test("uploads the pasted image once the preview is confirmed", async () => {
    pasteImage();
    await flushPromises();

    await wrapper.find("[data-test=confirm]").trigger("click");
    await flushPromises();

    expect(mocks.updateImage).toHaveBeenCalledOnce();
    expect(mocks.updateImage).toHaveBeenCalledWith("pancakes", expect.objectContaining({ name: "pasted-image.png" }));
    expect((wrapper.props("modelValue") as RecipeOut).image).toBe("new-image");
  });

  test("keeps the current image when the preview is cancelled", async () => {
    pasteImage();
    await flushPromises();

    await wrapper.find("[data-test=cancel]").trigger("click");
    await flushPromises();

    expect(mocks.updateImage).not.toHaveBeenCalled();
    expect(wrapper.find("[data-test=paste-dialog]").exists()).toBe(false);
    expect(URL.revokeObjectURL).toHaveBeenCalled();
  });

  test("ignores a paste made while the previous image is still uploading", async () => {
    let finishUpload: (response: unknown) => void = () => {};
    mocks.updateImage.mockReturnValue(new Promise((resolve) => {
      finishUpload = resolve;
    }));
    pasteImage();
    await flushPromises();
    await wrapper.find("[data-test=confirm]").trigger("click");
    await flushPromises();

    const event = pasteImage();
    await flushPromises();

    expect(wrapper.find("[data-test=paste-dialog]").exists()).toBe(false);
    expect(event.defaultPrevented).toBe(false);

    finishUpload({ data: { image: "new-image" }, error: null });
    await flushPromises();
    pasteImage();
    await flushPromises();

    expect(wrapper.find("[data-test=paste-dialog]").exists()).toBe(true);
  });

  test("stops listening for pastes once the toolbar is gone", async () => {
    wrapper.unmount();
    vi.mocked(URL.createObjectURL).mockClear();

    const event = pasteImage();
    await flushPromises();

    expect(event.defaultPrevented).toBe(false);
    expect(URL.createObjectURL).not.toHaveBeenCalled();
  });
});
