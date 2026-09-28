import { describe, expect, test, vi } from "vitest";
import { useRecipeFilterFields } from "../use-recipe-filter-fields";
import { Organizer } from "~/lib/api/types/non-generated";

vi.mock("vue-i18n", async (importOriginal) => {
  const actual = await importOriginal<typeof import("vue-i18n")>();
  return {
    ...actual,
    useI18n: () => ({ t: (key: string) => key }),
  };
});

describe("useRecipeFilterFields", () => {
  test("offers every recipe filter field", () => {
    const names = useRecipeFilterFields().map(field => field.name);

    expect(names).toEqual([
      "recipe_category.id",
      "tags.id",
      "recipe_ingredient.food.id",
      "recipe_ingredient.food.label_id",
      "tools.id",
      "household_id",
      "user_id",
      "rating",
      "total_time_seconds",
      "last_made",
      "created_at",
      "updated_at",
    ]);
  });

  test("offers last made as a relative date", () => {
    const lastMade = useRecipeFilterFields().find(field => field.name === "last_made");

    expect(lastMade).toEqual({
      name: "last_made",
      label: "general.last-made",
      type: "relativeDate",
    });
  });

  test("uses the organizer type for organizer fields", () => {
    const types = Object.fromEntries(useRecipeFilterFields().map(field => [field.name, field.type]));

    expect(types["recipe_category.id"]).toBe(Organizer.Category);
    expect(types["tags.id"]).toBe(Organizer.Tag);
    expect(types["recipe_ingredient.food.id"]).toBe(Organizer.Food);
    expect(types["recipe_ingredient.food.label_id"]).toBe(Organizer.Label);
    expect(types["tools.id"]).toBe(Organizer.Tool);
    expect(types["household_id"]).toBe(Organizer.Household);
    expect(types["user_id"]).toBe(Organizer.User);
  });

  test("has no duplicate field names", () => {
    const names = useRecipeFilterFields().map(field => field.name);

    expect(new Set(names).size).toBe(names.length);
  });

  test("leaves out only the excluded fields", () => {
    const all = useRecipeFilterFields().map(field => field.name);
    const withoutTools = useRecipeFilterFields({ exclude: ["tools.id"] }).map(field => field.name);

    expect(withoutTools).toEqual(all.filter(name => name !== "tools.id"));
  });
});
