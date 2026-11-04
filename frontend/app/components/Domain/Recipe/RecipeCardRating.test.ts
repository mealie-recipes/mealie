import { mount } from "@vue/test-utils";
import { beforeEach, describe, expect, test, vi } from "vitest";
import { ref } from "vue";
import RecipeCardRating from "./RecipeCardRating.vue";

const userRatings = ref<{ recipeId: string; rating: number | null }[]>([]);

vi.mock("~/composables/use-users", () => ({
  useUserSelfRatings: () => ({ userRatings }),
}));

function mountRating(modelValue: number) {
  return mount(RecipeCardRating, { props: { modelValue, recipeId: "recipe-1" } });
}

describe("RecipeCardRating", () => {
  beforeEach(() => {
    userRatings.value = [];
  });

  test("announces the user's own rating", () => {
    userRatings.value = [{ recipeId: "recipe-1", rating: 4 }];

    const display = mountRating(2).get("[role='img']");

    expect(display.attributes("aria-label")).toBe("4 out of 5 stars");
  });

  test("falls back to the group average when the user has not rated", () => {
    const display = mountRating(3.5).get("[role='img']");

    expect(display.attributes("aria-label")).toBe("3.5 out of 5 stars");
  });

  test("announces an unrated recipe as zero stars", () => {
    const display = mountRating(0).get("[role='img']");

    expect(display.attributes("aria-label")).toBe("0 out of 5 stars");
  });

  test("hides the star glyphs from assistive technology", () => {
    const stars = mountRating(3).findAll(".star");

    expect(stars).toHaveLength(5);
    expect(stars.every(star => star.attributes("aria-hidden") === "true")).toBe(true);
  });
});
