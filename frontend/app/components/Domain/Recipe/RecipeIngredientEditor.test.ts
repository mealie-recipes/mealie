import { mount, type VueWrapper } from "@vue/test-utils";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { nextTick, ref } from "vue";
import RecipeIngredientEditor from "./RecipeIngredientEditor.vue";
import type { RecipeIngredient } from "~/lib/api/types/recipe";

const { mockStore } = vi.hoisted(() => ({
  mockStore: (items: object[]) => () => ({ store: ref(items), actions: {} }),
}));

vi.mock("~/composables/store", () => ({
  useFoodStore: mockStore([]),
  useFoodData: () => ({ data: { name: "" }, reset: vi.fn() }),
  useUnitStore: mockStore([]),
  useUnitData: () => ({ data: { name: "" }, reset: vi.fn() }),
}));

vi.mock("~/composables/api", () => ({
  useUserApi: () => ({}),
  usePublicExploreApi: () => ({ explore: {} }),
}));

vi.mock("~/composables/recipes/use-recipe-search", () => ({
  useRecipeSearch: () => ({
    query: ref(""),
    data: ref([]),
    trigger: vi.fn(),
  }),
}));

vi.mock("~/composables/use-mealie-auth", () => ({
  useMealieAuth: () => ({ user: ref({ groupSlug: "home" }) }),
  useLoggedInState: () => ({ isOwnGroup: ref(true) }),
}));

vi.mock("vue-router", () => ({
  useRoute: () => ({ params: { groupSlug: "home" } }),
}));

const wrappers: VueWrapper[] = [];

function mountEditor(
  modelValue: RecipeIngredient = { referenceId: "ref-1", quantity: 1 },
  props: Record<string, unknown> = {},
) {
  const wrapper = mount(RecipeIngredientEditor, {
    props: {
      modelValue,
      ...props,
    },
    global: {
      mocks: {
        $vuetify: {
          display: {
            mdAndDown: false,
          },
        },
        $globals: {
          icons: {
            arrowUpDown: "arrowUpDown",
            alert: "alert",
            swapHorizontal: "swapHorizontal",
            dotsVertical: "dotsVertical",
            delete: "delete",
          },
        },
      },
      stubs: {
        RecipeIngredientEditorLayout: {
          template: "<div><slot name=\"dragHandle\" /><slot name=\"form\" /><slot name=\"contextMenu\" /></div>",
        },
        RecipeIngredientSubstitutionEditor: true,
        BaseButtonGroup: true,
        BaseButton: true,
        VNumberInput: {
          props: ["modelValue"],
          emits: ["update:modelValue"],
          template: "<div class=\"quantity-input\"><input class=\"v-number-input\" :value=\"modelValue\" @input=\"$emit('update:modelValue', $event.target.value)\" /></div>",
        },
        VAutocomplete: {
          props: ["modelValue", "search"],
          emits: ["update:modelValue", "update:search"],
          template: "<div class=\"v-autocomplete\"><input class=\"autocomplete-input\" :value=\"search\" @input=\"$emit('update:search', $event.target.value)\" /></div>",
        },
        VTextField: {
          props: ["modelValue"],
          emits: ["update:modelValue"],
          template: "<input class=\"v-text-field\" :value=\"modelValue\" @input=\"$emit('update:modelValue', $event.target.value)\" />",
        },
        VIcon: true,
        VTooltip: true,
      },
    },
  });

  wrappers.push(wrapper);
  return wrapper;
}

describe("RecipeIngredientEditor", () => {
  beforeEach(() => {
    vi.stubGlobal("useRoute", () => ({ params: { groupSlug: "home" } }));
    vi.stubGlobal("useMealieAuth", () => ({ user: ref({ groupSlug: "home" }) }));
    vi.stubGlobal("useLoggedInState", () => ({ isOwnGroup: ref(true) }));
    vi.stubGlobal("useNuxtApp", () => ({
      $globals: {
        icons: {
          arrowUpDown: "arrowUpDown",
          alert: "alert",
          swapHorizontal: "swapHorizontal",
          dotsVertical: "dotsVertical",
          delete: "delete",
        },
      },
    }));
  });

  afterEach(() => {
    wrappers.forEach(wrapper => wrapper.unmount());
    wrappers.length = 0;
    vi.unstubAllGlobals();
  });

  test("renders with data-reference-id attribute", () => {
    const wrapper = mountEditor({ referenceId: "test-ref-123", quantity: 2 });
    expect(wrapper.attributes("data-reference-id")).toBe("test-ref-123");
  });

  test("emits ctrl-enter when Ctrl+Enter is pressed in any input", async () => {
    const wrapper = mountEditor({ referenceId: "test-ref-123", quantity: 1 });
    const input = wrapper.find("input");

    const event = new KeyboardEvent("keydown", {
      key: "Enter",
      ctrlKey: true,
      bubbles: true,
      cancelable: true,
    });
    input.element.dispatchEvent(event);
    await nextTick();

    expect(wrapper.emitted("ctrl-enter")).toHaveLength(1);
    expect(event.defaultPrevented).toBe(true);
  });

  test("emits ctrl-enter when Cmd+Enter (metaKey) is pressed", async () => {
    const wrapper = mountEditor({ referenceId: "test-ref-123", quantity: 1 });
    const input = wrapper.find("input");

    const event = new KeyboardEvent("keydown", {
      key: "Enter",
      metaKey: true,
      bubbles: true,
      cancelable: true,
    });
    input.element.dispatchEvent(event);
    await nextTick();

    expect(wrapper.emitted("ctrl-enter")).toHaveLength(1);
    expect(event.defaultPrevented).toBe(true);
  });

  test("does not emit ctrl-enter on plain Enter keydown", async () => {
    const wrapper = mountEditor({ referenceId: "test-ref-123", quantity: 1 });
    const input = wrapper.find("input");

    const event = new KeyboardEvent("keydown", {
      key: "Enter",
      ctrlKey: false,
      metaKey: false,
      bubbles: true,
      cancelable: true,
    });
    input.element.dispatchEvent(event);
    await nextTick();

    expect(wrapper.emitted("ctrl-enter")).toBeUndefined();
    expect(event.defaultPrevented).toBe(false);
  });

  test("focusQuantity focuses the quantity input element", () => {
    const wrapper = mountEditor({ referenceId: "test-ref-123", quantity: 1 });
    const input = wrapper.find(".quantity-input input").element as HTMLInputElement;
    const focusSpy = vi.spyOn(input, "focus");

    wrapper.vm.focusQuantity();

    expect(focusSpy).toHaveBeenCalled();
  });

  test("emits delete when Ctrl+Delete is pressed in any input", async () => {
    const wrapper = mountEditor({ referenceId: "test-ref-123", quantity: 1 });
    const input = wrapper.find("input");

    const event = new KeyboardEvent("keydown", {
      key: "Delete",
      ctrlKey: true,
      bubbles: true,
      cancelable: true,
    });
    input.element.dispatchEvent(event);
    await nextTick();

    expect(wrapper.emitted("delete")).toHaveLength(1);
    expect(event.defaultPrevented).toBe(true);
  });

  test("emits delete when Cmd+Delete (metaKey) is pressed", async () => {
    const wrapper = mountEditor({ referenceId: "test-ref-123", quantity: 1 });
    const input = wrapper.find("input");

    const event = new KeyboardEvent("keydown", {
      key: "Delete",
      metaKey: true,
      bubbles: true,
      cancelable: true,
    });
    input.element.dispatchEvent(event);
    await nextTick();

    expect(wrapper.emitted("delete")).toHaveLength(1);
    expect(event.defaultPrevented).toBe(true);
  });

  test("does not emit delete on plain Delete keydown", async () => {
    const wrapper = mountEditor({ referenceId: "test-ref-123", quantity: 1 });
    const input = wrapper.find("input");

    const event = new KeyboardEvent("keydown", {
      key: "Delete",
      ctrlKey: false,
      metaKey: false,
      bubbles: true,
      cancelable: true,
    });
    input.element.dispatchEvent(event);
    await nextTick();

    expect(wrapper.emitted("delete")).toBeUndefined();
    expect(event.defaultPrevented).toBe(false);
  });

  test("does not emit delete when deleteDisabled is true", async () => {
    const wrapper = mountEditor(
      { referenceId: "test-ref-123", quantity: 1 },
      { deleteDisabled: true },
    );

    const input = wrapper.find("input");
    const event = new KeyboardEvent("keydown", {
      key: "Delete",
      ctrlKey: true,
      bubbles: true,
      cancelable: true,
    });
    input.element.dispatchEvent(event);
    await nextTick();

    expect(wrapper.emitted("delete")).toBeUndefined();
    expect(event.defaultPrevented).toBe(false);
  });

  test("emits move-up when Ctrl+ArrowUp is pressed in any input", async () => {
    const wrapper = mountEditor({ referenceId: "test-ref-123", quantity: 1 });
    const input = wrapper.find("input");

    const event = new KeyboardEvent("keydown", {
      key: "ArrowUp",
      ctrlKey: true,
      bubbles: true,
      cancelable: true,
    });
    input.element.dispatchEvent(event);
    await nextTick();

    expect(wrapper.emitted("move-up")).toHaveLength(1);
    expect(event.defaultPrevented).toBe(true);
  });

  test("emits move-up when Cmd+ArrowUp is pressed", async () => {
    const wrapper = mountEditor({ referenceId: "test-ref-123", quantity: 1 });
    const input = wrapper.find("input");

    const event = new KeyboardEvent("keydown", {
      key: "ArrowUp",
      metaKey: true,
      bubbles: true,
      cancelable: true,
    });
    input.element.dispatchEvent(event);
    await nextTick();

    expect(wrapper.emitted("move-up")).toHaveLength(1);
    expect(event.defaultPrevented).toBe(true);
  });

  test("emits move-down when Ctrl+ArrowDown is pressed in any input", async () => {
    const wrapper = mountEditor({ referenceId: "test-ref-123", quantity: 1 });
    const input = wrapper.find("input");

    const event = new KeyboardEvent("keydown", {
      key: "ArrowDown",
      ctrlKey: true,
      bubbles: true,
      cancelable: true,
    });
    input.element.dispatchEvent(event);
    await nextTick();

    expect(wrapper.emitted("move-down")).toHaveLength(1);
    expect(event.defaultPrevented).toBe(true);
  });

  test("emits move-down when Cmd+ArrowDown is pressed", async () => {
    const wrapper = mountEditor({ referenceId: "test-ref-123", quantity: 1 });
    const input = wrapper.find("input");

    const event = new KeyboardEvent("keydown", {
      key: "ArrowDown",
      metaKey: true,
      bubbles: true,
      cancelable: true,
    });
    input.element.dispatchEvent(event);
    await nextTick();

    expect(wrapper.emitted("move-down")).toHaveLength(1);
    expect(event.defaultPrevented).toBe(true);
  });

  test("does not emit move-up or move-down on plain ArrowUp or ArrowDown", async () => {
    const wrapper = mountEditor({ referenceId: "test-ref-123", quantity: 1 });
    const input = wrapper.find("input");

    const upEvent = new KeyboardEvent("keydown", {
      key: "ArrowUp",
      ctrlKey: false,
      metaKey: false,
      bubbles: true,
      cancelable: true,
    });
    input.element.dispatchEvent(upEvent);
    await nextTick();

    expect(wrapper.emitted("move-up")).toBeUndefined();
    expect(upEvent.defaultPrevented).toBe(false);

    const downEvent = new KeyboardEvent("keydown", {
      key: "ArrowDown",
      ctrlKey: false,
      metaKey: false,
      bubbles: true,
      cancelable: true,
    });
    input.element.dispatchEvent(downEvent);
    await nextTick();

    expect(wrapper.emitted("move-down")).toBeUndefined();
    expect(downEvent.defaultPrevented).toBe(false);
  });
});
