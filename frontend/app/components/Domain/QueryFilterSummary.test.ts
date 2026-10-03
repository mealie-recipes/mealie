import { mount } from "@vue/test-utils";
import { describe, expect, test, vi } from "vitest";
import QueryFilterSummary from "./QueryFilterSummary.vue";
import { Organizer } from "~/lib/api/types/non-generated";

// vi.mock factories are hoisted above imports, so anything they use has to be hoisted too
const { CATEGORY_ID, USER_ID, mockStore } = vi.hoisted(() => ({
  CATEGORY_ID: "c0000000-0000-4000-8000-000000000001",
  USER_ID: "u0000000-0000-4000-8000-000000000001",
  mockStore: (items: object[]) => () => ({ store: { value: items }, actions: {} }),
}));

vi.mock("~/composables/store", () => ({
  useCategoryStore: mockStore([{ id: CATEGORY_ID, name: "Dinner" }]),
  useTagStore: mockStore([]),
  useToolStore: mockStore([]),
  useFoodStore: mockStore([]),
  useLabelStore: mockStore([]),
  useHouseholdStore: mockStore([]),
}));

vi.mock("~/composables/store/use-user-store", () => ({
  useUserStore: mockStore([{ id: USER_ID, fullName: "Jane Doe" }]),
}));

const fieldDefs = [
  { name: "recipe_category.id", label: "Categories", type: Organizer.Category },
  { name: "user_id", label: "Users", type: Organizer.User },
  { name: "last_made", label: "Last Made", type: "relativeDate" as const },
];

function render(parts: object[]) {
  return mount(QueryFilterSummary, {
    props: { fieldDefs, queryFilter: { parts } },
    global: { stubs: { "v-chip": { template: "<span><slot /></span>" } } },
  });
}

describe("QueryFilterSummary", () => {
  test("shows organizer names instead of ids", () => {
    const wrapper = render([
      { attributeName: "recipe_category.id", relationalOperator: "IN", value: [CATEGORY_ID] },
      { logicalOperator: "AND", attributeName: "user_id", relationalOperator: "IN", value: [USER_ID] },
    ]);

    const text = wrapper.text();
    expect(text).toContain("Categories");
    expect(text).toContain("is one of");
    expect(text).toContain("Dinner");
    expect(text).toContain("AND");
    expect(text).toContain("Jane Doe");
    expect(text).not.toContain(CATEGORY_ID);
    expect(text).not.toContain(USER_ID);
  });

  test("shows relative dates as a number of days", () => {
    const wrapper = render([{ attributeName: "last_made", relationalOperator: "<=", value: "$NOW-30d" }]);

    expect(wrapper.text()).toContain("Last Made");
    expect(wrapper.text()).toContain("is older than");
    expect(wrapper.text()).toContain("30 days ago");
  });
});
