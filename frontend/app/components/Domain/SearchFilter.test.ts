import { flushPromises, mount, type VueWrapper } from "@vue/test-utils";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { nextTick } from "vue";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
import SearchFilter from "./SearchFilter.vue";

let wrapper: VueWrapper;

async function settleMenu() {
  await flushPromises();
  // Overlay scroll listeners and positioning are installed after animation frames.
  await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
  await nextTick();
}

async function openFilter() {
  wrapper = mount(SearchFilter, {
    attachTo: document.body,
    props: {
      items: [{ id: "apple", name: "Apple" }, { id: "carrot", name: "Carrot" }],
      modelValue: [],
    },
    slots: { default: "Foods" },
    global: {
      plugins: [createVuetify({
        components,
        directives,
        defaults: {
          VOverlay: { scrollStrategy: "close" },
          VMenu: { scrollStrategy: "close" },
        },
      })],
    },
  });
  await wrapper.get("button").trigger("click");
  await settleMenu();
  return document.querySelector<HTMLElement>(".v-overlay--active")!;
}

describe("SearchFilter", () => {
  beforeEach(() => {
    vi.stubGlobal("visualViewport", Object.assign(new EventTarget(), {
      width: 1024,
      height: 768,
      offsetLeft: 0,
      offsetTop: 0,
      scale: 1,
    }));
    vi.stubGlobal("ResizeObserver", class {
      observe() {}
      unobserve() {}
      disconnect() {}
    });
  });

  afterEach(() => {
    wrapper?.unmount();
    document.body.innerHTML = "";
    vi.unstubAllGlobals();
  });

  test("keeps the search usable when focusing it scrolls the document", async () => {
    const overlay = await openFilter();
    const input = overlay.querySelector<HTMLInputElement>("input")!;
    input.focus();
    Object.assign(visualViewport, { height: 390 });
    visualViewport.dispatchEvent(new Event("resize"));
    document.dispatchEvent(new Event("scroll"));
    await settleMenu();

    expect(overlay.classList.contains("v-overlay--active")).toBe(true);
    input.value = "Apple";
    input.dispatchEvent(new Event("input", { bubbles: true }));
    await new Promise(resolve => setTimeout(resolve, 400));
    await nextTick();
    expect(overlay.textContent).toContain("Apple");
    expect(overlay.textContent).not.toContain("Carrot");
    const checkbox = overlay.querySelector<HTMLInputElement>("input[type=checkbox]")!;
    checkbox.click();
    await nextTick();
    expect(wrapper.emitted("update:modelValue")?.at(-1)).toEqual([[{ id: "apple", name: "Apple" }]]);
  });

  test("still closes with Escape", async () => {
    const overlay = await openFilter();
    window.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", bubbles: true }));
    await settleMenu();
    expect(overlay.classList.contains("v-overlay--active")).toBe(false);
  });

  test("still closes when clicking outside", async () => {
    const overlay = await openFilter();
    document.body.dispatchEvent(new MouseEvent("mousedown", { bubbles: true }));
    document.body.click();
    await new Promise(resolve => setTimeout(resolve, 0));
    await settleMenu();
    expect(overlay.classList.contains("v-overlay--active")).toBe(false);
  });
});
