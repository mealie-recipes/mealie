import { describe, expect, test, vi } from "vitest";
import { useQueryFilterBuilder } from "../use-query-filter-builder";
import { Organizer } from "~/lib/api/types/non-generated";

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
  type: Organizer.Label,
};

const RATING_FIELD_DEF = {
  name: "rating",
  label: "Rating",
  type: "number" as const,
};

describe("food label fields", () => {
  test("are handled as an organizer, so the shared picker and hydration apply", () => {
    const { isOrganizerType } = useQueryFilterBuilder();

    expect(isOrganizerType(Organizer.Label)).toBe(true);
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
    field.relationalOperatorValue = getRelOps(Organizer.Label).value["NOT IN"];

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

const TOTAL_TIME_FIELD_DEF = {
  name: "total_time_seconds",
  label: "Total Time",
  type: "duration" as const,
};

describe("duration fields", () => {
  test("default to the <= operator and offer comparisons and null checks", () => {
    const { getFieldFromFieldDef } = useQueryFilterBuilder();

    const field = getFieldFromFieldDef(TOTAL_TIME_FIELD_DEF);

    expect(field.relationalOperatorValue.value).toBe("<=");
    expect(field.relationalOperatorChoices.map(choice => choice.value)).toEqual(["<=", ">=", "<", ">", "IS", "IS NOT"]);
  });

  test("build an unquoted seconds query filter string", () => {
    const { getFieldFromFieldDef, buildQueryFilterString } = useQueryFilterBuilder();

    const field = getFieldFromFieldDef(TOTAL_TIME_FIELD_DEF);
    field.value = 1800;

    expect(buildQueryFilterString([field], false)).toBe("total_time_seconds <= 1800");
  });

  test("are invalid without a duration", () => {
    const { getFieldFromFieldDef, buildQueryFilterString } = useQueryFilterBuilder();

    const field = getFieldFromFieldDef(TOTAL_TIME_FIELD_DEF);

    expect(buildQueryFilterString([field], false)).toBe("");
  });

  test.each([
    ["IS", "total_time_seconds IS NULL"],
    ["IS NOT", "total_time_seconds IS NOT NULL"],
  ] as const)("build an %s filter without a duration", (operator, expected) => {
    const { getFieldFromFieldDef, buildQueryFilterString, getRelOps } = useQueryFilterBuilder();

    const field = getFieldFromFieldDef(TOTAL_TIME_FIELD_DEF);
    field.relationalOperatorValue = getRelOps(field.type).value[operator];

    expect(buildQueryFilterString([field], false)).toBe(expected);
  });
});

describe("null filters", () => {
  test("restores the Last Made default when switching from a saved null filter to a comparison", () => {
    const { getFieldFromFieldDef, getRelOps, updateRelationalOperator, buildQueryFilterString } = useQueryFilterBuilder();
    const field = getFieldFromFieldDef({ name: "last_made", label: "Last Made", type: "relativeDate" });
    field.relationalOperatorValue = getRelOps(field.type).value.IS;
    field.value = "";

    updateRelationalOperator(field, "IS NOT");
    expect(field.value).toBe("");

    updateRelationalOperator(field, "<=");
    expect(field.value).toBe("$NOW-30d");
    expect(buildQueryFilterString([field], false)).toBe("last_made <= $NOW-30d");
  });

  test("restores the Total Time default when switching from a null filter to a comparison", () => {
    const { getFieldFromFieldDef, getRelOps, updateRelationalOperator, buildQueryFilterString } = useQueryFilterBuilder();
    const field = getFieldFromFieldDef(TOTAL_TIME_FIELD_DEF);
    field.relationalOperatorValue = getRelOps(field.type).value.IS;
    field.value = "";

    updateRelationalOperator(field, "<=");
    expect(field.value).toBe(30 * 60);
    expect(buildQueryFilterString([field], false)).toBe("total_time_seconds <= 1800");
  });

  test("are not available for date fields", () => {
    const { getFieldFromFieldDef } = useQueryFilterBuilder();

    const field = getFieldFromFieldDef({ name: "created_at", label: "Created At", type: "date" });

    expect(field.relationalOperatorChoices.map(choice => choice.value)).not.toContain("IS");
    expect(field.relationalOperatorChoices.map(choice => choice.value)).not.toContain("IS NOT");
  });

  test("are available for number fields", () => {
    const { getFieldFromFieldDef } = useQueryFilterBuilder();

    const field = getFieldFromFieldDef(RATING_FIELD_DEF);

    expect(field.relationalOperatorChoices).toEqual(expect.arrayContaining([
      {
        label: "query-filter.relational-operators.has-no-value",
        value: "IS",
      },
      {
        label: "query-filter.relational-operators.has-a-value",
        value: "IS NOT",
      },
    ]));
  });

  test.each([
    ["IS", "rating IS NULL"],
    ["IS NOT", "rating IS NOT NULL"],
  ] as const)("builds an %s filter without a field value", (operator, expected) => {
    const { getFieldFromFieldDef, buildQueryFilterString, getRelOps } = useQueryFilterBuilder();

    const field = getFieldFromFieldDef(RATING_FIELD_DEF);
    field.relationalOperatorValue = getRelOps(field.type).value[operator];

    expect(buildQueryFilterString([field], false)).toBe(expected);
  });
});
