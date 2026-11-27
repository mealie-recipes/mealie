import { mount } from "@vue/test-utils";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { reactive, ref } from "vue";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import RecipeOrganizerPage from "./RecipeOrganizerPage.vue";

vi.mock("~/components/Domain/Recipe/RecipeOrganizerDialog.vue", () => ({ default: { render: () => null } }));

const items = [
  { id: "t0000000-0000-4000-8000-000000000001", name: "Dinner", slug: "dinner" },
  { id: "t0000000-0000-4000-8000-000000000002", name: "Lunch", slug: "lunch" },
];

function render(canOrganize: boolean) {
  vi.stubGlobal("useMealieAuth", () => ({ user: ref({ groupSlug: "home", canOrganize }) }));

  return mount(RecipeOrganizerPage, {
    props: { items, icon: "tag", itemType: "tags" },
    global: {
      plugins: [createVuetify({ components })],
      stubs: {
        BaseButton: { template: "<button class=\"create-button\" type=\"button\" />" },
        ContextMenu: { template: "<div class=\"context-menu\" />" },
        BaseDialog: true,
        BaseCardSectionTitle: true,
      },
      mocks: { $globals: { icons: {} } },
    },
  });
}

describe("RecipeOrganizerPage", () => {
  beforeEach(() => {
    vi.stubGlobal("useNuxtApp", () => ({ $globals: { icons: {} } }));
    vi.stubGlobal("useRoute", () => reactive({ path: "/g/home/recipes/tags", params: { groupSlug: "home" }, query: {} }));
    vi.stubGlobal("useRouter", () => ({ replace: vi.fn() }));
  });

  afterEach(() => vi.unstubAllGlobals());

  test("shows the create button and item menus to a user who can organize", () => {
    const wrapper = render(true);

    expect(wrapper.text()).toContain("Dinner");
    expect(wrapper.find(".create-button").exists()).toBe(true);
    expect(wrapper.findAll(".context-menu")).toHaveLength(items.length);
  });

  test("hides the create button and item menus from a user who cannot organize", () => {
    const wrapper = render(false);

    expect(wrapper.text()).toContain("Dinner");
    expect(wrapper.find(".create-button").exists()).toBe(false);
    expect(wrapper.find(".context-menu").exists()).toBe(false);
  });
});
