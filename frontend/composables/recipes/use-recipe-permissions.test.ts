import { describe, test, expect } from "vitest";
import { ref, Ref } from "@nuxtjs/composition-api";
import { useRecipePermissions } from "./use-recipe-permissions";
import { HouseholdSummary } from "~/lib/api/types/household";
import { Recipe } from "~/lib/api/types/recipe";
import { UserOut } from "~/lib/api/types/user";

describe("test use recipe permissions", () => {
  const commonUserId = "my-user-id";
  const commonGroupId = "my-group-id";
  const commonHouseholdId = "my-household-id";

  const createRecipe = (overrides: Partial<Recipe>, isLocked = false): Recipe => ({
    id: "my-recipe-id",
    userId: commonUserId,
    groupId: commonGroupId,
    householdId: commonHouseholdId,
    settings: {
      locked: isLocked,
    },
    ...overrides,
  });

  const createUser = (overrides: Partial<UserOut>): UserOut => ({
    id: commonUserId,
    groupId: commonGroupId,
    groupSlug: "my-group",
    group: "my-group",
    householdId: commonHouseholdId,
    householdSlug: "my-household",
    household: "my-household",
    email: "bender.rodriguez@example.com",
    cacheKey: "1234",
    ...overrides,
  });

  const createRecipeHousehold = (overrides: Partial<HouseholdSummary>, lockRecipeEdits = false): Ref<HouseholdSummary> => (
    ref({
      id: commonHouseholdId,
      groupId: commonGroupId,
      name: "My Household",
      slug: "my-household",
      preferences: {
        id: "my-household-preferences-id",
        lockRecipeEditsFromOtherHouseholds: lockRecipeEdits,
      },
      ...overrides,
    })
  );

  test("when user is null, cannot edit", () => {
    const result = useRecipePermissions(createRecipe({}), createRecipeHousehold({}), null);
    expect(result.canEditRecipe.value).toBe(false);
  });

  test("when user is recipe owner, can edit", () => {
    const result = useRecipePermissions(createRecipe({}), ref(), createUser({}));
    expect(result.canEditRecipe.value).toBe(true);
  });

  test(
    "when user is not recipe owner, is correct group and household, recipe is unlocked, and household is unlocked, can edit",
    () => {
      const result = useRecipePermissions(
        createRecipe({}),
        createRecipeHousehold({}),
        createUser({ id: "other-user-id" }),
      );
      expect(result.canEditRecipe.value).toBe(true);
    }
  );

  test(
    "when user is not recipe owner, is correct group and household, recipe is unlocked, but household is locked, can edit",
    () => {
      const result = useRecipePermissions(
        createRecipe({}),
        createRecipeHousehold({}, true),
        createUser({ id: "other-user-id" }),
      );
      expect(result.canEditRecipe.value).toBe(true);
    }
  );

  test("when user is not recipe owner, and user is other group, cannot edit", () => {
    const result = useRecipePermissions(
      createRecipe({}),
      createRecipeHousehold({}),
      createUser({ id: "other-user-id", groupId: "other-group-id"}),
    );
    expect(result.canEditRecipe.value).toBe(false);
  });

  test("when user is not recipe owner, and user is other household, and household is unlocked, can edit", () => {
    const result = useRecipePermissions(
      createRecipe({}),
      createRecipeHousehold({}),
      createUser({ id: "other-user-id", householdId: "other-household-id" }),
    );
    expect(result.canEditRecipe.value).toBe(true);
  });

  test("when user is not recipe owner, and user is other household, and household is locked, cannot edit", () => {
    const result = useRecipePermissions(
      createRecipe({}),
      createRecipeHousehold({}, true),
      createUser({ id: "other-user-id", householdId: "other-household-id" }),
    );
    expect(result.canEditRecipe.value).toBe(false);
  });

  test("when user is not recipe owner, and recipe is locked, cannot edit", () => {
    const result = useRecipePermissions(
      createRecipe({}, true),
      createRecipeHousehold({}),
      createUser({ id: "other-user-id"}),
    );
    expect(result.canEditRecipe.value).toBe(false);
  });

  test("when user is recipe owner, and recipe is locked, and household is locked, can edit", () => {
    const result = useRecipePermissions(createRecipe({}, true), createRecipeHousehold({}, true), createUser({}));
    expect(result.canEditRecipe.value).toBe(true);
  });
});
