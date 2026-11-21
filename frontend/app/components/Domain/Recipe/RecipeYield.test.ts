import { mount } from "@vue/test-utils";
import { describe, expect, test } from "vitest";
import { createVuetify } from "vuetify";
import * as vuetifyComponents from "vuetify/components";
import RecipeYield from "./RecipeYield.vue";

function render(yieldQuantity: number, yieldText: string, scale = 1) {
  return mount(RecipeYield, {
    props: { yieldQuantity, yieldText, scale },
    global: {
      plugins: [createVuetify({ components: vuetifyComponents })],
      mocks: { $globals: { icons: { bread: "" } } },
      stubs: {
        SafeInlineHtml: { props: ["html"], template: "<span>{{ html }}</span>" },
      },
    },
  });
}

function textOf(wrapper: ReturnType<typeof render>): string {
  return wrapper.text().replace(/\s+/g, " ").trim();
}

describe("RecipeYield", () => {
  test("strips a leading quantity that repeats the structured value", () => {
    const wrapper = render(60, "60 servings");
    expect(textOf(wrapper)).toContain("60 servings");
    expect(textOf(wrapper)).not.toContain("60 60 servings");
    wrapper.unmount();
  });

  test("renders the quantity alone when the text is only the quantity", () => {
    const wrapper = render(60, "60");
    expect(textOf(wrapper)).toContain("Yield60");
    expect(textOf(wrapper)).not.toContain("60 60");
    wrapper.unmount();
  });

  test("leaves a non-matching leading number alone", () => {
    const wrapper = render(20, "1 9x13-inch pan, 20 bars");
    expect(textOf(wrapper)).toContain("20 1 9x13-inch pan, 20 bars");
    wrapper.unmount();
  });

  test("keeps the text when there is no structured quantity", () => {
    const wrapper = render(0, "60 servings");
    expect(textOf(wrapper)).toContain("60 servings");
    expect(textOf(wrapper)).not.toContain("0 60 servings");
    wrapper.unmount();
  });

  test("strips the raw quantity before scaling", () => {
    const wrapper = render(60, "60 servings", 2);
    expect(textOf(wrapper)).toContain("120 servings");
    wrapper.unmount();
  });
});
