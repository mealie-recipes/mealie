import { mount, type VueWrapper } from "@vue/test-utils";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { nextTick, ref } from "vue";
import RecipePageInstructions from "./RecipePageInstructions.vue";
import type { Recipe, RecipeStep } from "~/lib/api/types/recipe";

const isEditFormRef = ref(true);

vi.mock("~/composables/recipe-page/shared-state", () => ({
  usePageState: () => ({
    isCookMode: ref(false),
    toggleCookMode: vi.fn(),
    isEditForm: isEditFormRef,
  }),
}));

vi.mock("~/composables/recipe-page/use-extract-ingredient-references", () => ({
  useExtractIngredientReferences: () => ({
    extractIngredientReferences: vi.fn().mockReturnValue([]),
  }),
}));

vi.mock("~/composables/api", () => ({
  useUserApi: () => ({
    recipes: {
      createAsset: vi.fn(),
      createAssetFromUrl: vi.fn(),
    },
  }),
  useStaticRoutes: () => ({
    recipeAssetPath: vi.fn(),
  }),
}));

const wrappers: VueWrapper[] = [];

function mountInstructions(
  steps = ref<RecipeStep[]>([
    { id: "step-1", text: "First step text", summary: "Summary 1", title: "" },
    { id: "step-2", text: "Second step text", summary: "Summary 2", title: "" },
  ]),
  recipe = ref<Recipe>({
    id: "recipe-1",
    slug: "test-recipe",
    name: "Test Recipe",
    recipeInstructions: steps.value,
  } as Recipe),
) {
  const wrapper = mount(RecipePageInstructions, {
    props: {
      "modelValue": steps.value,
      "onUpdate:modelValue": (val: RecipeStep[]) => {
        steps.value = val;
      },
      "assets": [],
      "onUpdate:assets": () => {},
      "recipe": recipe.value,
    },
    global: {
      mocks: {
        $globals: {
          icons: {
            arrowUpDown: "arrowUpDown",
            delete: "delete",
            dotsVertical: "dotsVertical",
            link: "link",
            image: "image",
            edit: "edit",
            eye: "eye",
            clock: "clock",
          },
        },
      },
      stubs: {
        VueDraggable: {
          props: ["modelValue"],
          template: "<div><slot /></div>",
        },
        MarkdownEditor: {
          props: ["modelValue"],
          emits: ["update:modelValue"],
          template: `<div class="markdown-editor"><textarea :value="modelValue" @input="$emit('update:modelValue', $event.target.value)" /></div>`,
        },
        CookTime: {
          template: "<div class=\"cook-time\"><input class=\"cook-time-input\" /></div>",
        },
        BaseButtonGroup: true,
        DropZone: {
          template: "<div><slot /></div>",
        },
        SafeMarkdown: true,
        VSheet: true,
        VCard: {
          template: "<div><slot /></div>",
        },
        VCardTitle: {
          template: "<div class=\"v-card-title\"><slot /></div>",
        },
        VCardText: {
          template: "<div class=\"v-card-text\"><slot /></div>",
        },
        VTextField: {
          props: ["modelValue"],
          emits: ["update:modelValue"],
          template: `<div class="v-text-field"><input :value="modelValue" @input="$emit('update:modelValue', $event.target.value)" /></div>`,
        },
        VIcon: true,
        VBtn: true,
        VHover: {
          template: "<div><slot :isHovering=\"false\" /></div>",
        },
        VExpandTransition: {
          template: "<div><slot /></div>",
        },
        VDivider: true,
      },
    },
    attachTo: document.body,
  });

  wrappers.push(wrapper);
  return { wrapper, steps };
}

describe("RecipePageInstructions keyboard shortcuts", () => {
  beforeEach(() => {
    isEditFormRef.value = true;
    vi.stubGlobal("useNuxtApp", () => ({
      $globals: {
        icons: {
          arrowUpDown: "arrowUpDown",
          delete: "delete",
          dotsVertical: "dotsVertical",
          link: "link",
          image: "image",
          edit: "edit",
          eye: "eye",
          clock: "clock",
        },
      },
    }));
  });

  afterEach(() => {
    wrappers.forEach(wrapper => wrapper.unmount());
    wrappers.length = 0;
    vi.unstubAllGlobals();
  });

  test("ctrl-enter on first step inserts a new step below and focuses its textarea", async () => {
    const { steps } = mountInstructions();

    const firstStepEl = document.querySelector("[data-step-id=\"step-1\"]");
    const textarea = firstStepEl?.querySelector("textarea") as HTMLTextAreaElement;
    expect(textarea).toBeTruthy();
    textarea.focus();

    const event = new KeyboardEvent("keydown", {
      key: "Enter",
      ctrlKey: true,
      bubbles: true,
      cancelable: true,
    });
    textarea.dispatchEvent(event);
    await nextTick();
    await nextTick();

    expect(steps.value).toHaveLength(3);
    expect(steps.value[0].id).toBe("step-1");
    expect(steps.value[2].id).toBe("step-2");

    const newStepId = steps.value[1].id;
    const newStepEl = document.querySelector(`[data-step-id="${newStepId}"]`);
    const newTextarea = newStepEl?.querySelector("textarea");
    expect(document.activeElement).toBe(newTextarea);
    expect(event.defaultPrevented).toBe(true);
  });

  test("meta-enter (Cmd+Enter) on step inserts a new step below and focuses its textarea", async () => {
    const { steps } = mountInstructions();

    const firstStepEl = document.querySelector("[data-step-id=\"step-1\"]");
    const textarea = firstStepEl?.querySelector("textarea") as HTMLTextAreaElement;
    textarea.focus();

    const event = new KeyboardEvent("keydown", {
      key: "Enter",
      metaKey: true,
      bubbles: true,
      cancelable: true,
    });
    textarea.dispatchEvent(event);
    await nextTick();
    await nextTick();

    expect(steps.value).toHaveLength(3);
    expect(steps.value[0].id).toBe("step-1");
    expect(steps.value[2].id).toBe("step-2");
    expect(event.defaultPrevented).toBe(true);
  });

  test("ctrl-enter in summary input inserts a new step below and focuses summary input", async () => {
    const { steps } = mountInstructions();

    const firstStepEl = document.querySelector("[data-step-id=\"step-1\"]");
    const summaryInput = firstStepEl?.querySelector(".recipe-step-title input") as HTMLInputElement;
    expect(summaryInput).toBeTruthy();
    summaryInput.focus();

    const event = new KeyboardEvent("keydown", {
      key: "Enter",
      ctrlKey: true,
      bubbles: true,
      cancelable: true,
    });
    summaryInput.dispatchEvent(event);
    await nextTick();
    await nextTick();

    expect(steps.value).toHaveLength(3);
    const newStepId = steps.value[1].id;
    const newStepEl = document.querySelector(`[data-step-id="${newStepId}"]`);
    const newSummaryInput = newStepEl?.querySelector(".recipe-step-title input");
    expect(document.activeElement).toBe(newSummaryInput);
    expect(event.defaultPrevented).toBe(true);
  });

  test("ctrl-delete removes current step and focuses previous step textarea", async () => {
    const { steps } = mountInstructions();

    const secondStepEl = document.querySelector("[data-step-id=\"step-2\"]");
    const textarea = secondStepEl?.querySelector("textarea") as HTMLTextAreaElement;
    textarea.focus();

    const event = new KeyboardEvent("keydown", {
      key: "Delete",
      ctrlKey: true,
      bubbles: true,
      cancelable: true,
    });
    textarea.dispatchEvent(event);
    await nextTick();
    await nextTick();

    expect(steps.value).toHaveLength(1);
    expect(steps.value[0].id).toBe("step-1");

    const prevStepEl = document.querySelector("[data-step-id=\"step-1\"]");
    const prevTextarea = prevStepEl?.querySelector("textarea");
    expect(document.activeElement).toBe(prevTextarea);
    expect(event.defaultPrevented).toBe(true);
  });

  test("cmd-delete removes current step and focuses previous step", async () => {
    const { steps } = mountInstructions();

    const secondStepEl = document.querySelector("[data-step-id=\"step-2\"]");
    const textarea = secondStepEl?.querySelector("textarea") as HTMLTextAreaElement;
    textarea.focus();

    const event = new KeyboardEvent("keydown", {
      key: "Delete",
      metaKey: true,
      bubbles: true,
      cancelable: true,
    });
    textarea.dispatchEvent(event);
    await nextTick();
    await nextTick();

    expect(steps.value).toHaveLength(1);
    expect(steps.value[0].id).toBe("step-1");
    expect(event.defaultPrevented).toBe(true);
  });

  test("ctrl-arrow-up on second step swaps it with first step and refocuses textarea", async () => {
    const { steps } = mountInstructions();

    const secondStepEl = document.querySelector("[data-step-id=\"step-2\"]");
    const textarea = secondStepEl?.querySelector("textarea") as HTMLTextAreaElement;
    textarea.focus();

    const event = new KeyboardEvent("keydown", {
      key: "ArrowUp",
      ctrlKey: true,
      bubbles: true,
      cancelable: true,
    });
    textarea.dispatchEvent(event);
    await nextTick();
    await nextTick();

    expect(steps.value[0].id).toBe("step-2");
    expect(steps.value[1].id).toBe("step-1");

    const movedStepEl = document.querySelector("[data-step-id=\"step-2\"]");
    const movedTextarea = movedStepEl?.querySelector("textarea");
    expect(document.activeElement).toBe(movedTextarea);
    expect(event.defaultPrevented).toBe(true);
  });

  test("cmd-arrow-up moves step up", async () => {
    const { steps } = mountInstructions();

    const secondStepEl = document.querySelector("[data-step-id=\"step-2\"]");
    const textarea = secondStepEl?.querySelector("textarea") as HTMLTextAreaElement;
    textarea.focus();

    const event = new KeyboardEvent("keydown", {
      key: "ArrowUp",
      metaKey: true,
      bubbles: true,
      cancelable: true,
    });
    textarea.dispatchEvent(event);
    await nextTick();
    await nextTick();

    expect(steps.value[0].id).toBe("step-2");
    expect(steps.value[1].id).toBe("step-1");
    expect(event.defaultPrevented).toBe(true);
  });

  test("ctrl-arrow-up on first step is a no-op", async () => {
    const { steps } = mountInstructions();

    const firstStepEl = document.querySelector("[data-step-id=\"step-1\"]");
    const textarea = firstStepEl?.querySelector("textarea") as HTMLTextAreaElement;
    textarea.focus();

    const event = new KeyboardEvent("keydown", {
      key: "ArrowUp",
      ctrlKey: true,
      bubbles: true,
      cancelable: true,
    });
    textarea.dispatchEvent(event);
    await nextTick();

    expect(steps.value[0].id).toBe("step-1");
    expect(steps.value[1].id).toBe("step-2");
  });

  test("ctrl-arrow-down on first step swaps it with second step and refocuses textarea", async () => {
    const { steps } = mountInstructions();

    const firstStepEl = document.querySelector("[data-step-id=\"step-1\"]");
    const textarea = firstStepEl?.querySelector("textarea") as HTMLTextAreaElement;
    textarea.focus();

    const event = new KeyboardEvent("keydown", {
      key: "ArrowDown",
      ctrlKey: true,
      bubbles: true,
      cancelable: true,
    });
    textarea.dispatchEvent(event);
    await nextTick();
    await nextTick();

    expect(steps.value[0].id).toBe("step-2");
    expect(steps.value[1].id).toBe("step-1");

    const movedStepEl = document.querySelector("[data-step-id=\"step-1\"]");
    const movedTextarea = movedStepEl?.querySelector("textarea");
    expect(document.activeElement).toBe(movedTextarea);
    expect(event.defaultPrevented).toBe(true);
  });

  test("cmd-arrow-down moves step down", async () => {
    const { steps } = mountInstructions();

    const firstStepEl = document.querySelector("[data-step-id=\"step-1\"]");
    const textarea = firstStepEl?.querySelector("textarea") as HTMLTextAreaElement;
    textarea.focus();

    const event = new KeyboardEvent("keydown", {
      key: "ArrowDown",
      metaKey: true,
      bubbles: true,
      cancelable: true,
    });
    textarea.dispatchEvent(event);
    await nextTick();
    await nextTick();

    expect(steps.value[0].id).toBe("step-2");
    expect(steps.value[1].id).toBe("step-1");
    expect(event.defaultPrevented).toBe(true);
  });

  test("ctrl-arrow-down on last step is a no-op", async () => {
    const { steps } = mountInstructions();

    const secondStepEl = document.querySelector("[data-step-id=\"step-2\"]");
    const textarea = secondStepEl?.querySelector("textarea") as HTMLTextAreaElement;
    textarea.focus();

    const event = new KeyboardEvent("keydown", {
      key: "ArrowDown",
      ctrlKey: true,
      bubbles: true,
      cancelable: true,
    });
    textarea.dispatchEvent(event);
    await nextTick();

    expect(steps.value[0].id).toBe("step-1");
    expect(steps.value[1].id).toBe("step-2");
  });

  test("plain keys do not trigger shortcuts", async () => {
    const { steps } = mountInstructions();

    const firstStepEl = document.querySelector("[data-step-id=\"step-1\"]");
    const textarea = firstStepEl?.querySelector("textarea") as HTMLTextAreaElement;

    const enterEvent = new KeyboardEvent("keydown", {
      key: "Enter",
      ctrlKey: false,
      metaKey: false,
      bubbles: true,
      cancelable: true,
    });
    textarea.dispatchEvent(enterEvent);
    await nextTick();
    expect(steps.value).toHaveLength(2);
    expect(enterEvent.defaultPrevented).toBe(false);

    const deleteEvent = new KeyboardEvent("keydown", {
      key: "Delete",
      ctrlKey: false,
      metaKey: false,
      bubbles: true,
      cancelable: true,
    });
    textarea.dispatchEvent(deleteEvent);
    await nextTick();
    expect(steps.value).toHaveLength(2);
    expect(deleteEvent.defaultPrevented).toBe(false);

    const upEvent = new KeyboardEvent("keydown", {
      key: "ArrowUp",
      ctrlKey: false,
      metaKey: false,
      bubbles: true,
      cancelable: true,
    });
    textarea.dispatchEvent(upEvent);
    await nextTick();
    expect(steps.value[0].id).toBe("step-1");
    expect(upEvent.defaultPrevented).toBe(false);
  });

  test("shortcuts do not trigger when isEditForm is false", async () => {
    isEditFormRef.value = false;
    const { steps } = mountInstructions();

    const firstStepEl = document.querySelector("[data-step-id=\"step-1\"]");
    const event = new KeyboardEvent("keydown", {
      key: "Enter",
      ctrlKey: true,
      bubbles: true,
      cancelable: true,
    });
    firstStepEl?.dispatchEvent(event);
    await nextTick();

    expect(steps.value).toHaveLength(2);
    expect(event.defaultPrevented).toBe(false);
  });
});
