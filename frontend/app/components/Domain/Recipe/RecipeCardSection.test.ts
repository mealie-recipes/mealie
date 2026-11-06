import { flushPromises, mount } from "@vue/test-utils";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { ref } from "vue";
import RecipeCardSection from "./RecipeCardSection.vue";

const mocks = vi.hoisted(() => ({
  fetchMore: vi.fn(),
}));

vi.mock("~/composables/use-logged-in-state", () => ({
  useLoggedInState: () => ({
    isOwnGroup: ref(true),
  }),
}));

vi.mock("~/composables/recipes", () => ({
  useLazyRecipes: () => ({
    fetchMore: mocks.fetchMore,
    getRandom: vi.fn(),
  }),
}));

vi.mock("~/composables/use-users/preferences", () => ({
  useUserSortPreferences: () => ref({
    orderBy: "created_at",
    orderDirection: "desc",
    useMobileCards: false,
    sortIcon: "",
  }),
}));

function mountSection(query: { search?: string } | null = null) {
  return mount(RecipeCardSection, {
    props: {
      disableToolbar: true,
      query,
    },
    global: {
      stubs: {
        AppLoader: true,
        AppScrollToTop: true,
        VAlert: {
          props: ["title", "text"],
          template: "<div class=\"empty-state\"><h2>{{ title }}</h2><p>{{ text }}</p></div>",
        },
        VCard: true,
        VCol: true,
        VFadeTransition: { template: "<div><slot /></div>" },
        VRow: { template: "<div><slot /></div>" },
      },
      directives: {
        intersect: {},
      },
    },
  });
}

describe("RecipeCardSection", () => {
  beforeEach(() => {
    mocks.fetchMore.mockResolvedValue([]);

    vi.stubGlobal("useDisplay", () => ({ smAndDown: ref(false) }));
    vi.stubGlobal("useMealieAuth", () => ({ user: ref({ groupSlug: "family" }) }));
    vi.stubGlobal("useNuxtApp", () => ({ $globals: { icons: { tags: "tags" } } }));
    vi.stubGlobal("useRoute", () => ({ params: { groupSlug: "family" }, path: "/g/family/recipes" }));
    vi.stubGlobal("useRouter", () => ({ push: vi.fn() }));
    vi.stubGlobal("useScrollPosition", () => ({
      getSavedPage: () => null,
      restorePosition: vi.fn(),
      savePosition: vi.fn(),
    }));
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    mocks.fetchMore.mockReset();
  });

  test("shows the empty state when a text search has no recipes", async () => {
    const wrapper = mountSection({ search: "miso" });
    await flushPromises();

    expect(wrapper.find(".empty-state").text()).toContain("No recipes found");
    expect(wrapper.find(".empty-state").text()).toContain("We couldn't find any recipes matching your search.");

    wrapper.unmount();
  });

  test("does not show the search empty state without a text search", async () => {
    const wrapper = mountSection();
    await flushPromises();

    expect(wrapper.find(".empty-state").exists()).toBe(false);

    wrapper.unmount();
  });
});
