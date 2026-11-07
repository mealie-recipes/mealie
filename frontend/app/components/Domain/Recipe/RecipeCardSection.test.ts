import { flushPromises, mount, type VueWrapper } from "@vue/test-utils";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { reactive, ref } from "vue";
import RecipeCardSection from "./RecipeCardSection.vue";

const preferences = ref({
  orderBy: "name",
  orderDirection: "asc",
  useMobileCards: false,
  sortIcon: "sort",
});

vi.mock("~/composables/use-logged-in-state", () => ({
  useLoggedInState: () => ({
    isOwnGroup: ref(true),
  }),
}));

vi.mock("~/composables/recipes", () => ({
  useLazyRecipes: () => ({
    fetchMore: vi.fn().mockResolvedValue([]),
    getRandom: vi.fn(),
  }),
}));

vi.mock("~/composables/use-users/preferences", () => ({
  useUserSortPreferences: () => preferences,
}));

const recipes = [
  {
    id: "1",
    name: "First Recipe",
    slug: "first-recipe",
    description: "",
    rating: 0,
    image: "",
    tags: [{ id: "tag-1", name: "Dinner", slug: "dinner" }],
  },
];

const tag = recipes[0].tags[0];
const wrappers: VueWrapper[] = [];

const cardStub = {
  emits: ["item-selected"],
  template: "<button class=\"recipe-card\" type=\"button\" @click=\"$emit('item-selected', tag, 'tags')\" />",
  data: () => ({ tag }),
};

async function mountSection() {
  const wrapper = mount(RecipeCardSection, {
    props: {
      recipes,
      disableToolbar: true,
    },
    global: {
      directives: {
        intersect: {},
      },
      mocks: {
        $globals: {
          icons: {},
        },
      },
      stubs: {
        RecipeCard: cardStub,
        RecipeCardMobile: cardStub,
        AppLoader: true,
        AppScrollToTop: true,
        VCard: true,
        VCol: { template: "<div><slot /></div>" },
        VFadeTransition: { template: "<div><slot /></div>" },
        VRow: { template: "<div><slot /></div>" },
      },
    },
  });

  await flushPromises();
  wrappers.push(wrapper);

  return wrapper;
}

describe("RecipeCardSection", () => {
  beforeEach(() => {
    preferences.value.useMobileCards = false;

    vi.stubGlobal("useMealieAuth", () => ({
      user: ref({ groupSlug: "family" }),
    }));
    vi.stubGlobal("useNuxtApp", () => ({ $globals: { icons: {} } }));
    vi.stubGlobal("useRoute", () => reactive({ path: "/g/family", params: { groupSlug: "family" } }));
    vi.stubGlobal("useRouter", () => ({ push: vi.fn() }));
    vi.stubGlobal("useDisplay", () => ({ smAndDown: ref(false) }));
    vi.stubGlobal("useScrollPosition", () => ({
      savePosition: vi.fn(),
      getSavedPage: vi.fn().mockReturnValue(null),
      restorePosition: vi.fn(),
    }));
  });

  afterEach(() => {
    wrappers.forEach(wrapper => wrapper.unmount());
    wrappers.length = 0;
    vi.unstubAllGlobals();
  });

  test("forwards item-selected from a recipe card", async () => {
    const wrapper = await mountSection();

    await wrapper.find(".recipe-card").trigger("click");

    expect(wrapper.emitted("itemSelected")).toEqual([[tag, "tags"]]);
  });

  test("forwards item-selected from a mobile recipe card", async () => {
    preferences.value.useMobileCards = true;
    const wrapper = await mountSection();

    await wrapper.find(".recipe-card").trigger("click");

    expect(wrapper.emitted("itemSelected")).toEqual([[tag, "tags"]]);
  });
});
