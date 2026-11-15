import { flushPromises, shallowMount } from "@vue/test-utils";
import { afterEach, describe, expect, test, vi } from "vitest";
import { computed, ref } from "vue";
import RecipeTimeline from "./RecipeTimeline.vue";

const mocks = vi.hoisted(() => ({
  getAll: vi.fn(),
  getAllTimelineEvents: vi.fn(),
}));

vi.mock("./RecipeTimelineItem.vue", () => ({ default: { render: () => null } }));

vi.mock("~/composables/api", () => ({
  useUserApi: () => ({
    recipes: {
      getAll: mocks.getAll,
      getAllTimelineEvents: mocks.getAllTimelineEvents,
    },
  }),
}));

vi.mock("~/composables/use-users/preferences", () => ({
  useTimelinePreferences: () => ref({ orderDirection: "desc", types: ["info"] }),
}));

vi.mock("~/composables/recipes/use-recipe-timeline-events", () => ({
  useTimelineEventTypes: () => ({ eventTypeOptions: computed(() => []) }),
}));

vi.mock("~/composables/use-toast", () => ({
  alert: { error: vi.fn(), success: vi.fn() },
}));

const PER_PAGE = 32;

function eventsForRecipe(recipeId: string, page: number) {
  return Array.from({ length: PER_PAGE }, (_, i) => ({
    id: `event-${page}-${i}`,
    recipeId,
    subject: "made it",
    eventType: "info",
    timestamp: "2026-01-01T00:00:00Z",
  }));
}

afterEach(() => {
  vi.clearAllMocks();
  document.onscroll = null;
});

describe("RecipeTimeline", () => {
  test("does not fetch recipes when every event's recipe is already loaded", async () => {
    mocks.getAllTimelineEvents.mockImplementation((page: number) =>
      Promise.resolve({ data: { items: eventsForRecipe("recipe-1", page) } }),
    );
    mocks.getAll.mockResolvedValue({ data: { items: [{ id: "recipe-1", name: "Recipe", slug: "recipe" }] } });

    shallowMount(RecipeTimeline, {
      props: { queryFilter: "groupId=\"g\"", showRecipeCards: true },
      global: { mocks: { $globals: { icons: {} }, $vuetify: { display: { smAndDown: false } } } },
    });
    await flushPromises();

    // the second page holds only events for the recipe the first page loaded
    document.onscroll?.(new Event("scroll"));
    await flushPromises();

    expect(mocks.getAllTimelineEvents).toHaveBeenCalledTimes(2);
    expect(mocks.getAll).toHaveBeenCalledTimes(1);
    expect(mocks.getAll).toHaveBeenCalledWith(1, -1, { queryFilter: "id IN [\"recipe-1\"]" });
  });
});
