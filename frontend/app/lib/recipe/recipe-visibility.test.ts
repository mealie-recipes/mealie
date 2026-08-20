import { describe, expect, test } from "vitest";
import { isRecipeFullyPublic } from "./recipe-visibility";
import type { Recipe } from "~/lib/api/types/recipe";
import type { HouseholdSummary } from "~/lib/api/types/household";
import type { GroupSummary } from "~/lib/api/types/user";

const groupId = "group-1";
const householdId = "household-1";

function fakeRecipe(overrides: Partial<Recipe> = {}): Recipe {
  return {
    groupId,
    householdId,
    settings: { public: true },
    ...overrides,
  } as Recipe;
}

function fakeGroup(overrides: Partial<GroupSummary> = {}): GroupSummary {
  return {
    id: groupId,
    preferences: { privateGroup: false },
    ...overrides,
  } as GroupSummary;
}

function fakeHousehold(overrides: Partial<HouseholdSummary> = {}): HouseholdSummary {
  return {
    id: householdId,
    groupId,
    preferences: { privateHousehold: false },
    ...overrides,
  } as HouseholdSummary;
}

describe("isRecipeFullyPublic", () => {
  test("public recipe in a public group and household", () => {
    expect(isRecipeFullyPublic(fakeRecipe(), fakeGroup(), fakeHousehold())).toBe(true);
  });

  test("public recipe in another household of the same group", () => {
    const recipe = fakeRecipe({ householdId: "household-2" });
    const otherHousehold = fakeHousehold({ id: "household-2" });
    expect(isRecipeFullyPublic(recipe, fakeGroup(), otherHousehold)).toBe(true);
  });

  test("rejects when the recipe is not marked public", () => {
    const recipe = fakeRecipe({ settings: { public: false } });
    expect(isRecipeFullyPublic(recipe, fakeGroup(), fakeHousehold())).toBe(false);
  });

  test("rejects when the group is private", () => {
    const group = fakeGroup({ preferences: { privateGroup: true } });
    expect(isRecipeFullyPublic(fakeRecipe(), group, fakeHousehold())).toBe(false);
  });

  test("rejects when the recipe's household is private", () => {
    const household = fakeHousehold({ preferences: { privateHousehold: true } });
    expect(isRecipeFullyPublic(fakeRecipe(), fakeGroup(), household)).toBe(false);
  });

  test("rejects a household that isn't the recipe's, even when it's public", () => {
    const recipe = fakeRecipe({ householdId: "household-2" });
    expect(isRecipeFullyPublic(recipe, fakeGroup(), fakeHousehold())).toBe(false);
  });

  test("rejects a group that isn't the recipe's, even when it's public", () => {
    const recipe = fakeRecipe({ groupId: "group-2" });
    expect(isRecipeFullyPublic(recipe, fakeGroup(), fakeHousehold())).toBe(false);
  });

  test("rejects when preferences are missing", () => {
    expect(isRecipeFullyPublic(fakeRecipe(), fakeGroup({ preferences: undefined }), fakeHousehold())).toBe(false);
    expect(isRecipeFullyPublic(fakeRecipe(), fakeGroup(), fakeHousehold({ preferences: undefined }))).toBe(false);
  });

  test("defaults safe when group or household haven't loaded yet", () => {
    expect(isRecipeFullyPublic(fakeRecipe(), undefined, fakeHousehold())).toBe(false);
    expect(isRecipeFullyPublic(fakeRecipe(), fakeGroup(), undefined)).toBe(false);
  });

  test("rejects when the recipe is undefined", () => {
    expect(isRecipeFullyPublic(undefined, fakeGroup(), fakeHousehold())).toBe(false);
  });
});
