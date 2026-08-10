import { describe, expect, test } from "vitest";
import { isRecipeFullyPublic } from "./recipe-visibility";
import type { Recipe } from "~/lib/api/types/recipe";
import type { HouseholdInDB } from "~/lib/api/types/household";
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

function fakeHousehold(overrides: Partial<HouseholdInDB> = {}): HouseholdInDB {
  return {
    id: householdId,
    preferences: { privateHousehold: false },
    ...overrides,
  } as HouseholdInDB;
}

describe("isRecipeFullyPublic", () => {
  test("matching ids, fully public group and household", () => {
    expect(isRecipeFullyPublic(fakeRecipe(), fakeGroup(), fakeHousehold())).toBe(true);
  });

  test("rejects a mismatched householdId", () => {
    const recipe = fakeRecipe({ householdId: "other-household" });
    expect(isRecipeFullyPublic(recipe, fakeGroup(), fakeHousehold())).toBe(false);
  });

  test("rejects a mismatched groupId", () => {
    const recipe = fakeRecipe({ groupId: "other-group" });
    expect(isRecipeFullyPublic(recipe, fakeGroup(), fakeHousehold())).toBe(false);
  });

  test("rejects when the recipe itself is not marked public", () => {
    const recipe = fakeRecipe({ settings: { public: false } });
    expect(isRecipeFullyPublic(recipe, fakeGroup(), fakeHousehold())).toBe(false);
  });

  test("rejects when the group is private", () => {
    const group = fakeGroup({ preferences: { privateGroup: true } });
    expect(isRecipeFullyPublic(fakeRecipe(), group, fakeHousehold())).toBe(false);
  });

  test("rejects when the household is private", () => {
    const household = fakeHousehold({ preferences: { privateHousehold: true } });
    expect(isRecipeFullyPublic(fakeRecipe(), fakeGroup(), household)).toBe(false);
  });

  test("defaults safe when group or household haven't loaded yet", () => {
    expect(isRecipeFullyPublic(fakeRecipe(), undefined, fakeHousehold())).toBe(false);
    expect(isRecipeFullyPublic(fakeRecipe(), fakeGroup(), undefined)).toBe(false);
  });

  test("rejects when the recipe is undefined", () => {
    expect(isRecipeFullyPublic(undefined, fakeGroup(), fakeHousehold())).toBe(false);
  });
});
