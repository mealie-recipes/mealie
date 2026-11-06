import { mount } from "@vue/test-utils";
import { afterEach, describe, expect, test, vi } from "vitest";
import { nextTick } from "vue";
import AppButtonUpload from "./AppButtonUpload.vue";

vi.mock("~/composables/api", () => ({
  useUserApi: () => ({
    upload: {
      file: vi.fn(),
    },
  }),
}));

function mountUpload() {
  return mount(AppButtonUpload, {
    props: {
      url: "none",
      post: false,
    },
    global: {
      stubs: {
        VForm: {
          template: "<form><slot /></form>",
        },
        VBtn: {
          props: ["loading"],
          emits: ["click"],
          template: `
            <button
              class="upload-button"
              type="button"
              :data-loading="loading ? 'true' : 'false'"
              @click="$emit('click')"
            >
              <slot />
            </button>
          `,
        },
        VIcon: {
          template: "<span><slot /></span>",
        },
      },
    },
  });
}

describe("AppButtonUpload", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test("stops loading when the file picker closes without selecting a file", async () => {
    vi.stubGlobal("useNuxtApp", () => ({
      $globals: {
        icons: {
          upload: "upload",
        },
      },
    }));

    const wrapper = mountUpload();

    const input = wrapper.find("input[type=\"file\"]");
    const clickSpy = vi.spyOn(input.element as HTMLInputElement, "click")
      .mockImplementation(() => {});

    await wrapper.find(".upload-button").trigger("click");
    await nextTick();

    expect(clickSpy).toHaveBeenCalledOnce();
    expect(wrapper.find(".upload-button").attributes("data-loading")).toBe("true");

    document.dispatchEvent(new Event("visibilitychange"));
    await nextTick();

    expect(wrapper.find(".upload-button").attributes("data-loading")).toBe("false");

    wrapper.unmount();
  });

  test("stops loading when the window regains focus", async () => {
    vi.stubGlobal("useNuxtApp", () => ({
      $globals: {
        icons: {
          upload: "upload",
        },
      },
    }));

    const wrapper = mountUpload();

    const input = wrapper.find("input[type=\"file\"]");
    vi.spyOn(input.element as HTMLInputElement, "click")
      .mockImplementation(() => {});

    await wrapper.find(".upload-button").trigger("click");
    await nextTick();

    expect(wrapper.find(".upload-button").attributes("data-loading")).toBe("true");

    window.dispatchEvent(new Event("focus"));
    await nextTick();

    expect(wrapper.find(".upload-button").attributes("data-loading")).toBe("false");

    wrapper.unmount();
  });
});
