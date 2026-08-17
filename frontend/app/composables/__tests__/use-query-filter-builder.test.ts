import { describe, expect, test, vi } from "vitest";
import { useQueryFilterBuilder } from "../use-query-filter-builder";

vi.mock("vue-i18n", async (importOriginal) => {
  const actual = await importOriginal<typeof import("vue-i18n")>();
  return {
    ...actual,
    useI18n: () => ({ t: (key: string) => key }),
  };
});

const LABEL_ID = "a5f1c6d2-0000-4000-8000-000000000001";
const OTHER_LABEL_ID = "a5f1c6d2-0000-4000-8000-000000000002";

const FOOD_LABEL_FIELD_DEF = {
  name: "recipe_ingredient.food.label_id",
  label: "Food Label",
  type: "foodLabel" as const,
};

describe("food label fields", () => {
  test("are treated as multi-select fields", () => {
    const { isMultiSelectType, isOrganizerType } = useQueryFilterBuilder();

    expect(isMultiSelectType("foodLabel")).toBe(true);
    // food labels are not recipe organizers, so organizer-specific handling must not pick them up
    expect(isOrganizerType("foodLabel")).toBe(false);
  });

  test("default to the IN operator", () => {
    const { getFieldFromFieldDef } = useQueryFilterBuilder();

    const field = getFieldFromFieldDef(FOOD_LABEL_FIELD_DEF);

    expect(field.relationalOperatorValue.value).toBe("IN");
    expect(field.relationalOperatorChoices.map(choice => choice.value)).toEqual([
      "IN",
      "NOT IN",
      "CONTAINS ALL",
    ]);
  });

  test("build a quoted list query filter string", () => {
    const { getFieldFromFieldDef, buildQueryFilterString } = useQueryFilterBuilder();

    const field = getFieldFromFieldDef(FOOD_LABEL_FIELD_DEF);
    field.values = [LABEL_ID, OTHER_LABEL_ID];

    expect(buildQueryFilterString([field], false)).toBe(
      `recipe_ingredient.food.label_id IN ["${LABEL_ID}","${OTHER_LABEL_ID}"]`,
    );
  });

  test("can exclude a label", () => {
    const { getFieldFromFieldDef, buildQueryFilterString, getRelOps } = useQueryFilterBuilder();

    const field = getFieldFromFieldDef(FOOD_LABEL_FIELD_DEF);
    field.values = [LABEL_ID];
    field.relationalOperatorValue = getRelOps("foodLabel").value["NOT IN"];

    expect(buildQueryFilterString([field], false)).toBe(
      `recipe_ingredient.food.label_id NOT IN ["${LABEL_ID}"]`,
    );
  });

  test("are invalid without a selected label", () => {
    const { getFieldFromFieldDef, buildQueryFilterString } = useQueryFilterBuilder();

    const field = getFieldFromFieldDef(FOOD_LABEL_FIELD_DEF);

    expect(buildQueryFilterString([field], false)).toBe("");
  });
});
