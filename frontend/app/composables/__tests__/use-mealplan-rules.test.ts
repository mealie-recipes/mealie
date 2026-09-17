import { describe, expect, test, vi } from "vitest";
import {
  buildRuleQueryFilter,
  getApplicableRules,
  getDayOfWeek,
  resetMealplanRuleStore,
  useMealplanRules,
} from "../use-mealplan-rules";
import type { PlanRulesDay, PlanRulesOut, PlanRulesType } from "~/lib/api/types/meal-plan";

const getAll = vi.fn();
vi.mock("~/composables/api", () => ({
  useUserApi: () => ({
    mealplanRules: { getAll },
  }),
}));

function createRule(day: PlanRulesDay, entryType: PlanRulesType, queryFilterString = ""): PlanRulesOut {
  return {
    id: `${day}-${entryType}-${queryFilterString}`,
    groupId: "my-group-id",
    householdId: "my-household-id",
    day,
    entryType,
    queryFilterString,
  };
}

// 2026-08-19 is a Wednesday
const wednesday = new Date(2026, 7, 19);

describe("getDayOfWeek", () => {
  test.each([
    [new Date(2026, 7, 16), "sunday"],
    [new Date(2026, 7, 17), "monday"],
    [new Date(2026, 7, 19), "wednesday"],
    [new Date(2026, 7, 22), "saturday"],
  ])("maps %s to its english weekday", (date, expected) => {
    expect(getDayOfWeek(date)).toEqual(expected);
  });
});

describe("getApplicableRules", () => {
  test("matches rules with the same day and entry type", () => {
    const rule = createRule("wednesday", "dinner");
    expect(getApplicableRules([rule], wednesday, "dinner")).toEqual([rule]);
  });

  test("matches rules with an unset day or entry type", () => {
    const anyDay = createRule("unset", "dinner");
    const anyType = createRule("wednesday", "unset");
    const anything = createRule("unset", "unset");

    expect(getApplicableRules([anyDay, anyType, anything], wednesday, "dinner")).toEqual([
      anyDay,
      anyType,
      anything,
    ]);
  });

  test("excludes rules for another day or entry type", () => {
    const otherDay = createRule("thursday", "dinner");
    const otherType = createRule("wednesday", "lunch");

    expect(getApplicableRules([otherDay, otherType], wednesday, "dinner")).toEqual([]);
  });
});

describe("buildRuleQueryFilter", () => {
  test("returns null when no rules apply", () => {
    const rules = [createRule("thursday", "dinner", "rating > 3")];
    expect(buildRuleQueryFilter(rules, wednesday, "dinner")).toBeNull();
  });

  test("returns null when the applicable rules have no query filter", () => {
    const rules = [createRule("wednesday", "dinner", "")];
    expect(buildRuleQueryFilter(rules, wednesday, "dinner")).toBeNull();
  });

  test("wraps a single query filter in parentheses", () => {
    const rules = [createRule("wednesday", "dinner", "rating > 3")];
    expect(buildRuleQueryFilter(rules, wednesday, "dinner")).toEqual("(rating > 3)");
  });

  test("joins every applicable query filter with AND", () => {
    const rules = [
      createRule("unset", "unset", "rating > 3"),
      createRule("wednesday", "dinner", "tags.id IN [\"my-tag-id\"]"),
      createRule("thursday", "dinner", "last_made < 2026-01-01"),
      createRule("wednesday", "lunch", "created_at > 2026-01-01"),
    ];

    expect(buildRuleQueryFilter(rules, wednesday, "dinner")).toEqual(
      "(rating > 3) AND (tags.id IN [\"my-tag-id\"])",
    );
  });
});

describe("useMealplanRules", () => {
  test("hydrates the store on first use only", async () => {
    resetMealplanRuleStore();

    const rule = createRule("unset", "unset", "rating > 3");
    getAll.mockResolvedValue({ data: { items: [rule] } });

    const { rules, initialized } = useMealplanRules();
    await vi.waitFor(() => expect(initialized.value).toBe(true));

    expect(rules.value).toEqual([rule]);
    expect(getAll).toHaveBeenCalledTimes(1);

    useMealplanRules();
    expect(getAll).toHaveBeenCalledTimes(1);
  });
});
