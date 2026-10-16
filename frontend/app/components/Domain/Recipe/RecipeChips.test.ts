import { mount } from "@vue/test-utils";
import { describe, expect, test } from "vitest";
import RecipeChips from "./RecipeChips.vue";
import type { RecipeCategory, RecipeTag, RecipeTool } from "~/lib/api/types/recipe";

type ChipItem = RecipeCategory | RecipeTag | RecipeTool;

function mountChips(items: ChipItem[]) {
  return mount(RecipeChips, {
    props: { items },
    global: {
      stubs: {
        VChip: {
          props: ["color", "label", "variant", "size", "dark"],
          template: `<span class="chip" :data-color="color"><slot /></span>`,
        },
      },
    },
  });
}

describe("RecipeChips", () => {
  test("uses the theme accent color when no item color is set", () => {
    const wrapper = mountChips([{ id: "1", name: "dinner", slug: "dinner" } as RecipeCategory]);
    const chips = wrapper.findAll(".chip");
    expect(chips).toHaveLength(1);
    expect(chips[0].attributes("data-color")).toBe("accent");
  });

  test("uses the tag/category color when set", () => {
    const wrapper = mountChips([
      { id: "1", name: "dinner", slug: "dinner", color: "#ff0000" } as unknown as RecipeCategory,
      { id: "2", name: "vegan", slug: "vegan", color: "" } as unknown as RecipeTag,
    ]);
    const chips = wrapper.findAll(".chip");
    expect(chips).toHaveLength(2);
    expect(chips[0].attributes("data-color")).toBe("#ff0000");
    // an empty color falls back to the theme accent
    expect(chips[1].attributes("data-color")).toBe("accent");
  });

  test("tools without a color render with the accent default", () => {
    const wrapper = mountChips([{ id: "1", name: "knife", slug: "knife" } as unknown as RecipeTool]);
    expect(wrapper.find(".chip").attributes("data-color")).toBe("accent");
  });
});
