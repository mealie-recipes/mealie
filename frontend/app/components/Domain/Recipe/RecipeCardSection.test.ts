import { flushPromises, mount, type VueWrapper } from "@vue/test-utils";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { nextTick, reactive, ref } from "vue";
import RecipeCardSection from "./RecipeCardSection.vue";

const mocks = vi.hoisted(() => ({
  preferences: { value: { useMobileCards: false, orderBy: "name", orderDirection: "asc" } },
  fetchMore: vi.fn(),
}));

vi.mock("~/composables/use-logged-in-state", () => ({
  useLoggedInState: () => ({ isOwnGroup: ref(true) }),
}));

vi.mock("~/composables/recipes", () => ({
  useLazyRecipes: () => ({
    fetchMore: mocks.fetchMore,
    getRandom: vi.fn(),
    searchError: ref(""),
  }),
}));

vi.mock("~/composables/use-users/preferences", () => ({
  useUserSortPreferences: () => mocks.preferences,
}));

const tag = { id: "t0000000-0000-4000-8000-000000000001", name: "Dinner", slug: "dinner", groupId: "g1" };
const recipes = [{ id: "1", name: "Soup", slug: "soup", description: "", rating: 0, image: "", tags: [tag] }];

const wrappers: VueWrapper[] = [];

const passthrough = { template: "<div><slot /></div>" };

async function mountSection() {
  const wrapper = mount(RecipeCardSection, {
    props: { recipes, disableToolbar: true },
    global: {
      mocks: { $globals: { icons: {} } },
      stubs: {
        VRow: passthrough,
        VCol: passthrough,
        VCard: passthrough,
        VCardTitle: passthrough,
        VCardActions: passthrough,
        VList: passthrough,
        VListItem: passthrough,
        VListItemTitle: passthrough,
        VListItemSubtitle: passthrough,
        VExpandTransition: passthrough,
        VFadeTransition: passthrough,
        VImg: passthrough,
        VHover: { template: "<div><slot :is-hovering=\"false\" :props=\"{}\" /></div>" },
        VChip: { template: "<button class=\"tag-chip\" type=\"button\"><slot /></button>" },
        RecipeCardImage: true,
        RecipeCardRating: true,
        RecipeFavoriteBadge: true,
        RecipeContextMenu: true,
        SafeMarkdown: true,
        AppLoader: true,
        AppScrollToTop: true,
      },
      directives: { intersect: {} },
    },
  });
  wrappers.push(wrapper);
  await flushPromises();
  return wrapper;
}

describe("RecipeCardSection", () => {
  beforeEach(() => {
    mocks.fetchMore.mockReset().mockResolvedValue([]);
    vi.stubGlobal("useDisplay", () => ({ smAndDown: ref(false) }));
    vi.stubGlobal("useMealieAuth", () => ({ user: ref({ groupSlug: "family" }) }));
    vi.stubGlobal("useNuxtApp", () => ({ $globals: { icons: {} } }));
    vi.stubGlobal("useRoute", () => reactive({ path: "/g/family", params: { groupSlug: "family" } }));
    vi.stubGlobal("useRouter", () => ({ push: vi.fn() }));
    vi.stubGlobal("useScrollPosition", () => ({
      savePosition: vi.fn(),
      getSavedPage: vi.fn(() => null),
      restorePosition: vi.fn(),
    }));
  });

  afterEach(() => {
    wrappers.forEach(wrapper => wrapper.unmount());
    wrappers.length = 0;
    vi.unstubAllGlobals();
  });

  test.each([
    ["desktop cards", false],
    ["mobile cards", true],
  ])("clicking a tag on %s emits itemSelected", async (_, useMobileCards) => {
    mocks.preferences.value.useMobileCards = useMobileCards;
    const wrapper = await mountSection();

    const chip = wrapper.find(".tag-chip");
    expect(chip.exists()).toBe(true);
    await chip.trigger("click");

    expect(wrapper.emitted("itemSelected")).toEqual([[tag, "tags"]]);
  });

  test("discards stale search results and resets pagination", async () => {
    const wrapper = await mountSection();
    let completeOld!: (recipes: unknown[]) => void;
    mocks.fetchMore.mockImplementationOnce(() => new Promise(resolve => completeOld = resolve));
    await wrapper.setProps({ query: { search: "pork", searchMode: "all" } });
    await nextTick();
    mocks.fetchMore.mockResolvedValueOnce([{ id: "new", name: "Lettuce" }]);
    await wrapper.setProps({ query: { search: "lettuce", searchMode: "any" } });
    await flushPromises();
    const events = wrapper.emitted("replaceRecipes")!;
    expect(events.at(-1)).toEqual([[{ id: "new", name: "Lettuce" }]]);
    completeOld([{ id: "old", name: "Pork" }]);
    await flushPromises();
    expect(wrapper.emitted("replaceRecipes")!.at(-1)).toEqual(events.at(-1));
    expect(mocks.fetchMore.mock.calls.at(-1)?.[0]).toBe(1);
  });
});
