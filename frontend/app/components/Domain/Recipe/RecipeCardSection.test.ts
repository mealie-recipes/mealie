
import { flushPromises, mount, type VueWrapper } from "@vue/test-utils";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { reactive, ref } from "vue";
import RecipeCardSection from "./RecipeCardSection.vue";

const mocks = vi.hoisted(() => ({
  fetchMore: vi.fn(),
  preferences: {
    value: {
      useMobileCards: false,
      orderBy: "created_at",
      orderDirection: "desc",
      sortIcon: "",
    },
  },
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
  useUserSortPreferences: () => mocks.preferences,
}));

const tag = {
  id: "t0000000-0000-4000-8000-000000000001",
  name: "Dinner",
  slug: "dinner",
  groupId: "g1",
};

const recipes = [
  {
    id: "1",
    name: "Soup",
    slug: "soup",
    description: "",
    rating: 0,
    image: "",
    tags: [tag],
  },
];

const wrappers: VueWrapper[] = [];

const passthrough = { template: "<div><slot /></div>" };

const globalOptions = {
  stubs: {
    AppLoader: true,
    AppScrollToTop: true,
    VAvatar: passthrough,
    VCard: passthrough,
    VCardTitle: passthrough,
    VCardActions: passthrough,
    VIcon: passthrough,
    VCol: passthrough,
    VRow: passthrough,
    VList: passthrough,
    VListItem: passthrough,
    VListItemTitle: passthrough,
    VListItemSubtitle: passthrough,
    VExpandTransition: passthrough,
    VFadeTransition: passthrough,
    VImg: passthrough,
    VHover: {
      template: '<div><slot :is-hovering="false" :props="{}" /></div>',
    },
    VChip: {
      template: '<button class="tag-chip" type="button"><slot /></button>',
    },
    RecipeCardImage: true,
    RecipeCardRating: true,
    RecipeFavoriteBadge: true,
    RecipeContextMenu: true,
    SafeMarkdown: true,
  },
  mocks: {
    $globals: { icons: { tags: "tags" } },
  },
  directives: {
    intersect: {},
  },
};

function mountSearchSection(query: { search?: string } | null = null) {
  return mount(RecipeCardSection, {
    props: {
      disableToolbar: true,
      query,
    },
    global: globalOptions,
  });
}

async function mountTagSection() {
  const wrapper = mount(RecipeCardSection, {
    props: {
      recipes,
      disableToolbar: true,
    },
    global: globalOptions,
  });

  wrappers.push(wrapper);
  await flushPromises();
  return wrapper;
}

describe("RecipeCardSection", () => {
  beforeEach(() => {
    mocks.fetchMore.mockResolvedValue([]);
    mocks.preferences.value.useMobileCards = false;

    vi.stubGlobal("useDisplay", () => ({ smAndDown: ref(false) }));
    vi.stubGlobal("useMealieAuth", () => ({
      user: ref({ groupSlug: "family" }),
    }));
    vi.stubGlobal("useNuxtApp", () => ({
      $globals: { icons: { tags: "tags" } },
    }));
    vi.stubGlobal("useRoute", () =>
      reactive({
        path: "/g/family",
        params: { groupSlug: "family" },
      }),
    );
    vi.stubGlobal("useRouter", () => ({ push: vi.fn() }));
    vi.stubGlobal("useScrollPosition", () => ({
      savePosition: vi.fn(),
      getSavedPage: vi.fn(() => null),
      restorePosition: vi.fn(),
    }));
  });

  afterEach(() => {
    wrappers.forEach((wrapper) => wrapper.unmount());
    wrappers.length = 0;
    vi.unstubAllGlobals();
    mocks.fetchMore.mockReset();
  });

  test("shows the empty state when a text search has no recipes", async () => {
    const wrapper = mountSearchSection({ search: "miso" });
    await flushPromises();

    expect(wrapper.find(".search-empty-state").text()).toContain(
      "No recipes found",
    );
    expect(wrapper.find(".search-empty-state").text()).toContain(
      "We couldn't find any recipes matching your search.",
    );

    wrapper.unmount();
  });

  test("does not show the search empty state without a text search", async () => {
    const wrapper = mountSearchSection();
    await flushPromises();

    expect(wrapper.find(".search-empty-state").exists()).toBe(false);

    wrapper.unmount();
  });

  test.each([
    ["desktop cards", false],
    ["mobile cards", true],
  ])("clicking a tag on %s emits itemSelected", async (_, useMobileCards) => {
    mocks.preferences.value.useMobileCards = useMobileCards;
    const wrapper = await mountTagSection();

    const chip = wrapper.find(".tag-chip");
    expect(chip.exists()).toBe(true);
    await chip.trigger("click");

    expect(wrapper.emitted("itemSelected")).toEqual([[tag, "tags"]]);
  });
});
