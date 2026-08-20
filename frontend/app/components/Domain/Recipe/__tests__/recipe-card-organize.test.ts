import { shallowMount } from "@vue/test-utils";
import RecipeCard from "../RecipeCard.vue";
import RecipeCardMobile from "../RecipeCardMobile.vue";

vi.mock("~/composables/use-logged-in-state", () => ({
  useLoggedInState: () => ({ isOwnGroup: { value: true } }),
}));

const commonStubs = {
  NuxtLink: {
    props: {
      to: {
        type: String,
        required: true,
      },
    },
    template: "<a v-bind='$attrs' :href='to'><slot /></a>",
  },
  VHover: {
    template: "<div><slot :is-hovering='false' :props='{}' /></div>",
  },
  VTooltip: {
    template: "<div><slot name='activator' :props='{}' /></div>",
  },
  VCard: {
    template: "<div class='recipe-card-stub'><slot /></div>",
  },
  VBtn: {
    inheritAttrs: false,
    template: "<button v-bind='$attrs'><slot /></button>",
  },
};

const globals = {
  icons: {
    organizers: "organizers",
    checkboxBlankCircleOutline: "empty-circle",
    checkboxMarkedCircle: "selected-circle",
    dotsVertical: "dots-vertical",
    dotsHorizontal: "dots-horizontal",
  },
};

describe.each([
  ["desktop", RecipeCard, { name: "Recipe", slug: "recipe", recipeId: "1" }],
  ["mobile", RecipeCardMobile, { name: "Recipe", description: "", slug: "recipe", recipeId: "1" }],
])("%s recipe card", (_name, component, props) => {
  beforeEach(() => {
    vi.stubGlobal("useMealieAuth", () => ({ user: { value: { groupSlug: "group" } } }));
    vi.stubGlobal("useRoute", () => ({ params: { groupSlug: "group" } }));
    vi.stubGlobal("useLoggedInState", () => ({ isOwnGroup: { value: true } }));
  });

  it("uses a native recipe link and keeps organize clicks in the dialog", async () => {
    const wrapper = shallowMount(component, {
      props: {
        ...props,
        showOrganizer: true,
      },
      global: {
        mocks: {
          $globals: globals,
        },
        stubs: commonStubs,
      },
    });

    const link = wrapper.get("a.recipe-card-link");
    expect(link.attributes("href")).toBe("/g/group/r/recipe");
    expect(link.attributes("aria-label")).toContain("Recipe");
    expect(wrapper.getComponent(commonStubs.VCard).attributes("to")).toBeUndefined();

    const organizeButton = wrapper.get("button[aria-label=\"Organize\"]");
    const click = new MouseEvent("click", { bubbles: true, cancelable: true });
    organizeButton.element.dispatchEvent(click);

    expect(click.defaultPrevented).toBe(true);
    expect(wrapper.emitted("organize")).toHaveLength(1);
  });

  it("removes navigation and toggles selection from card activation", async () => {
    const wrapper = shallowMount(component, {
      props: {
        ...props,
        selectMode: true,
        selected: false,
      },
      global: {
        mocks: {
          $globals: globals,
        },
        stubs: commonStubs,
      },
    });

    expect(wrapper.find("a.recipe-card-link").exists()).toBe(false);
    expect(wrapper.getComponent(commonStubs.VCard).attributes("tabindex")).toBeUndefined();
    await wrapper.get(".recipe-card-stub").trigger("click");
    expect(wrapper.emitted("click") || wrapper.emitted("selected")).toHaveLength(1);
    expect(wrapper.find("button[aria-label=\"Organize\"]").exists()).toBe(false);
  });

  it("exposes the recipe selection state through one labeled toggle control", async () => {
    const wrapper = shallowMount(component, {
      props: {
        ...props,
        selectMode: true,
        selected: false,
      },
      global: {
        mocks: {
          $globals: globals,
        },
        stubs: commonStubs,
      },
    });

    const selectionButton = wrapper.get("button.recipe-card-selection");
    expect(selectionButton.attributes("aria-label")).toBe("Select Recipe");
    expect(selectionButton.attributes("aria-pressed")).toBe("false");
    expect(wrapper.findAll("[tabindex]")).toHaveLength(0);

    await wrapper.setProps({ selected: true });

    expect(selectionButton.attributes("aria-label")).toBe("Deselect Recipe");
    expect(selectionButton.attributes("aria-pressed")).toBe("true");
  });

  it("activates the selection toggle exactly once from the keyboard target", async () => {
    const wrapper = shallowMount(component, {
      props: {
        ...props,
        selectMode: true,
        selected: false,
      },
      global: {
        mocks: {
          $globals: globals,
        },
        stubs: commonStubs,
      },
    });

    await wrapper.get("button.recipe-card-selection").trigger("click");

    const eventName = component === RecipeCard ? "click" : "selected";
    expect(wrapper.emitted(eventName)).toHaveLength(1);
  });

  it("uses the selected-state icon for the selection control", () => {
    const wrapper = shallowMount(component, {
      props: {
        ...props,
        selectMode: true,
        selected: false,
      },
      global: {
        mocks: {
          $globals: globals,
        },
        stubs: commonStubs,
      },
    });

    expect(wrapper.text()).toContain("empty-circle");
    expect(wrapper.text()).not.toContain("selected-circle");
  });
});
