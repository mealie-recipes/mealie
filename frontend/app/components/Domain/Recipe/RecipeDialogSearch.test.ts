import { mount, type VueWrapper } from "@vue/test-utils";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { nextTick, reactive, ref } from "vue";
import RecipeDialogSearch from "./RecipeDialogSearch.vue";

const routerPush = vi.fn();
const wrappers: VueWrapper[] = [];

const mocks = vi.hoisted(() => ({
  useRecipeSearch: vi.fn(),
}));

vi.mock("~/composables/use-logged-in-state", () => ({
  useLoggedInState: () => ({
    isOwnGroup: ref(true),
  }),
}));

vi.mock("~/composables/api", () => ({
  useUserApi: () => ({}),
}));

vi.mock("~/composables/api/api-client", () => ({
  usePublicExploreApi: () => ({
    explore: {},
  }),
}));

vi.mock("~/composables/recipes/use-recipe-search", () => ({
  useRecipeSearch: mocks.useRecipeSearch,
}));

const recipes = [
  {
    id: "1",
    name: "First Recipe",
    slug: "first-recipe",
    description: "",
    rating: 0,
  },
  {
    id: "2",
    name: "Second Recipe",
    slug: "second-recipe",
    description: "",
    rating: 0,
  },
];

function keydown(key: string) {
  document.dispatchEvent(new KeyboardEvent("keydown", { key, cancelable: true }));
}

async function mountDialog(attrs: Record<string, unknown> = {}) {
  const wrapper = mount(RecipeDialogSearch, {
    attrs,
    global: {
      mocks: {
        $globals: {
          icons: {
            close: "close",
            search: "search",
          },
        },
        $vuetify: {
          display: {
            xs: false,
          },
        },
      },
      stubs: {
        RecipeCardMobile: {
          props: ["name"],
          template: "<button class=\"recipe-card\" type=\"button\">{{ name }}</button>",
        },
        VBtn: {
          template: "<button type=\"button\"><slot /></button>",
        },
        VCard: {
          template: "<div><slot /></div>",
        },
        VCardActions: {
          template: "<div><slot /></div>",
        },
        VDialog: {
          props: ["modelValue"],
          template: "<div v-if=\"modelValue\"><slot /></div>",
        },
        VIcon: {
          template: "<span><slot /></span>",
        },
        VTextField: {
          template: "<input>",
        },
        VToolbar: {
          template: "<div><slot /></div>",
        },
      },
    },
  });

  (wrapper.vm as unknown as { open: () => void }).open();
  await nextTick();

  wrappers.push(wrapper);

  return wrapper;
}

describe("RecipeDialogSearch", () => {
  beforeEach(() => {
    routerPush.mockClear();
    mocks.useRecipeSearch.mockReturnValue({
      query: ref(""),
      data: ref(recipes),
    });

    vi.stubGlobal("useMealieAuth", () => ({
      user: ref({ groupSlug: "family" }),
    }));
    vi.stubGlobal("useRoute", () => reactive({ params: { groupSlug: "family" } }));
    vi.stubGlobal("useRouter", () => ({
      push: routerPush,
    }));

    Element.prototype.scrollIntoView = vi.fn();
  });

  afterEach(() => {
    wrappers.forEach(wrapper => wrapper.unmount());
    wrappers.length = 0;
    vi.unstubAllGlobals();
  });

  test("ArrowUp and ArrowDown clamp recipe selection", async () => {
    const wrapper = await mountDialog();

    keydown("ArrowDown");
    await nextTick();
    expect(wrapper.findAll(".keyboard-selected")).toHaveLength(1);
    expect(wrapper.findAll(".recipe-card")[0].classes()).toContain("keyboard-selected");

    keydown("ArrowDown");
    await nextTick();
    keydown("ArrowDown");
    await nextTick();
    expect(wrapper.findAll(".keyboard-selected")).toHaveLength(1);
    expect(wrapper.findAll(".recipe-card")[1].classes()).toContain("keyboard-selected");

    keydown("ArrowUp");
    await nextTick();
    expect(wrapper.findAll(".recipe-card")[0].classes()).toContain("keyboard-selected");

    keydown("ArrowUp");
    await nextTick();
    keydown("ArrowUp");
    await nextTick();
    expect(wrapper.findAll(".keyboard-selected")).toHaveLength(0);
  });

  test("Enter navigates to the selected recipe", async () => {
    await mountDialog();

    keydown("ArrowDown");
    await nextTick();
    keydown("ArrowDown");
    await nextTick();
    keydown("Enter");

    expect(routerPush).toHaveBeenCalledWith("/g/family/r/second-recipe");
  });

  test("Enter selects the first recipe when no recipe is keyboard-selected", async () => {
    await mountDialog();

    keydown("Enter");

    expect(routerPush).toHaveBeenCalledWith("/g/family/r/first-recipe");
  });

  test("Enter emits selected instead of navigating when selected attr is provided", async () => {
    const wrapper = await mountDialog({ selected: vi.fn() });

    keydown("Enter");

    expect(wrapper.emitted("selected")).toEqual([[recipes[0]]]);
    expect(routerPush).not.toHaveBeenCalled();
  });

  test("keyboard navigation is a no-op when there are no results", async () => {
    mocks.useRecipeSearch.mockReturnValue({
      query: ref(""),
      data: ref([]),
    });
    const wrapper = await mountDialog();

    keydown("ArrowDown");
    await nextTick();
    keydown("ArrowUp");
    await nextTick();
    keydown("Enter");

    expect(wrapper.findAll(".keyboard-selected")).toHaveLength(0);
    expect(routerPush).not.toHaveBeenCalled();
    expect(wrapper.emitted("selected")).toBeUndefined();
  });
});
