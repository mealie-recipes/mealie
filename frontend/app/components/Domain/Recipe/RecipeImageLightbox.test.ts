import { mount } from "@vue/test-utils";
import { describe, expect, test, vi } from "vitest";
import { ref } from "vue";
import RecipeImageLightbox from "./RecipeImageLightbox.vue";

vi.mock("vuetify", () => ({ useTheme: () => ({ global: { current: ref({ dark: false }) } }) }));

function mountLightbox(navigation = true) {
  return mount(RecipeImageLightbox, {
    props: { modelValue: true, imageUrl: "/first.jpg", navigation },
    global: {
      mocks: { $globals: { icons: {} } },
      stubs: {
        VDialog: { template: "<div><slot /></div>" },
        VBtn: { template: "<button><slot /></button>" },
        VIcon: true,
      },
    },
  });
}

describe("RecipeImageLightbox navigation", () => {
  test("supports previous and next buttons and arrow keys", async () => {
    const wrapper = mountLightbox();
    await wrapper.get("button[aria-label='Next photo']").trigger("click");
    await wrapper.get("button[aria-label='Previous photo']").trigger("click");
    await wrapper.trigger("keydown", { key: "ArrowRight" });
    await wrapper.trigger("keydown", { key: "ArrowLeft" });
    expect(wrapper.emitted("next")).toHaveLength(2);
    expect(wrapper.emitted("previous")).toHaveLength(2);
    expect(wrapper.emitted("update:modelValue")).toBeUndefined();
    wrapper.unmount();
  });

  test("resets zoom when the photo changes", async () => {
    const wrapper = mountLightbox();
    await wrapper.get("img").trigger("click");
    expect(wrapper.get("img").attributes("style")).toContain("scale(2)");
    await wrapper.setProps({ imageUrl: "/second.jpg" });
    expect(wrapper.get("img").attributes("style")).toContain("scale(1)");
    wrapper.unmount();
  });

  test("supports swipe navigation without zooming the next photo", async () => {
    const wrapper = mountLightbox();
    wrapper.get("img").element.dispatchEvent(new MouseEvent("pointerdown", { clientX: 200, clientY: 100 }));
    wrapper.get("img").element.dispatchEvent(new MouseEvent("pointerup", { clientX: 80, clientY: 105 }));
    expect(wrapper.emitted("next")).toHaveLength(1);
    await wrapper.setProps({ imageUrl: "/second.jpg" });
    await wrapper.get("img").trigger("click");
    expect(wrapper.get("img").attributes("style")).toContain("scale(1)");
    wrapper.unmount();
  });

  test("keeps single-image viewers free of navigation buttons", () => {
    const wrapper = mountLightbox(false);
    expect(wrapper.find("button[aria-label='Next photo']").exists()).toBe(false);
    expect(wrapper.find("button[aria-label='Previous photo']").exists()).toBe(false);
    wrapper.unmount();
  });
});
