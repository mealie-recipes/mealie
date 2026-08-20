import { flushPromises, shallowMount } from "@vue/test-utils";
import RecipeQuickOrganizeDialog from "../RecipeQuickOrganizeDialog.vue";

const { api, alert } = vi.hoisted(() => ({
  api: {
    bulk: {
      bulkOrganize: vi.fn(),
    },
    recipes: {
      patchOne: vi.fn(),
    },
  },
  alert: {
    error: vi.fn(),
    success: vi.fn(),
  },
}));

vi.mock("~/composables/api", () => ({
  useUserApi: () => api,
}));

vi.mock("~/composables/use-toast", () => ({
  alert,
}));

const tag = { id: "tag-1", name: "Dinner", slug: "dinner" };
const category = { id: "category-1", name: "Main", slug: "main" };
const recipe = {
  id: "recipe-1",
  slug: "recipe-1",
  name: "Recipe",
  tags: [],
  recipeCategory: [],
};

const stubs = {
  BaseDialog: {
    template: "<div><slot /><slot name='card-actions' /></div>",
  },
  BaseButton: {
    props: {
      cancel: Boolean,
      disabled: Boolean,
      loading: Boolean,
      save: Boolean,
    },
    template: "<button :data-save='save ? true : undefined' :data-cancel='cancel ? true : undefined' :disabled='disabled' @click='$emit(\"click\")'><slot /></button>",
  },
  RecipeOrganizerSelector: {
    props: ["modelValue", "selectorType"],
    setup() {
      return { category, tag };
    },
    template: `
      <div>
        <button :data-selector='selectorType' @click='$emit("update:modelValue", selectorType === "tags" ? [tag] : [category])'>select</button>
        <button :data-clear='selectorType' @click='$emit("update:modelValue", [])'>clear</button>
      </div>
    `,
  },
  VRadioGroup: {
    emits: ["update:modelValue"],
    template: "<div><slot /><button data-operation='remove' @click='$emit(\"update:modelValue\", \"remove\")'>remove</button></div>",
  },
};

function mountDialog(props: Record<string, unknown>) {
  return shallowMount(RecipeQuickOrganizeDialog, {
    props,
    global: {
      mocks: {
        $globals: { icons: { organizers: "organizers" } },
      },
      stubs,
    },
  });
}

describe("RecipeQuickOrganizeDialog", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    api.bulk.bulkOrganize.mockResolvedValue({ data: [recipe], error: null });
    api.recipes.patchOne.mockResolvedValue({ data: recipe, error: null });
    vi.stubGlobal("useNuxtApp", () => ({ $globals: { icons: { organizers: "organizers" } } }));
  });

  it.each([
    {
      operation: "add" as const,
      selectedOrganizers: ["tags", "categories"],
      tags: [tag],
      categories: [category],
      returnedRecipe: recipe,
    },
    {
      operation: "remove" as const,
      selectedOrganizers: ["tags"],
      tags: [tag],
      categories: [],
      returnedRecipe: { ...recipe, tags: [tag] },
    },
  ])("sends selected IDs and the $operation operation to the atomic bulk API", async ({
    operation,
    selectedOrganizers,
    tags,
    categories,
    returnedRecipe,
  }) => {
    api.bulk.bulkOrganize.mockResolvedValue({ data: [returnedRecipe], error: null });
    const wrapper = mountDialog({ modelValue: true, mode: "bulk", recipes: [recipe, { ...recipe, id: "recipe-2" }] });

    for (const selectorType of selectedOrganizers) {
      await wrapper.get(`[data-selector="${selectorType}"]`).trigger("click");
    }
    if (operation === "remove") {
      await wrapper.get("button[data-operation='remove']").trigger("click");
    }
    await wrapper.find("button[data-save]").trigger("click");
    await flushPromises();

    expect(api.bulk.bulkOrganize).toHaveBeenCalledWith({
      recipes: ["recipe-1", "recipe-2"],
      operation,
      tags,
      categories,
    });
    expect(wrapper.emitted("saved")).toHaveLength(1);
    expect(wrapper.emitted("saved")![0][0][0]).toBe(returnedRecipe);
    expect(wrapper.emitted("update:modelValue")).toEqual([[false]]);
  });

  it("sends remove and keeps the dialog open when bulk organization fails", async () => {
    api.bulk.bulkOrganize.mockResolvedValue({ data: null, error: new Error("failed") });
    const wrapper = mountDialog({ modelValue: true, mode: "bulk", recipes: [recipe] });

    await wrapper.get("[data-selector=\"tags\"]").trigger("click");
    await wrapper.get("button[data-operation='remove']").trigger("click");
    await wrapper.find("button[data-save]").trigger("click");
    await flushPromises();

    expect(api.bulk.bulkOrganize).toHaveBeenCalledWith({
      recipes: ["recipe-1"],
      operation: "remove",
      tags: [tag],
      categories: [],
    });
    expect(wrapper.emitted("saved")).toBeUndefined();
    expect(wrapper.emitted("update:modelValue")).toBeUndefined();
    expect(alert.error).toHaveBeenCalled();
  });

  it("saves both organizer fields for a single recipe", async () => {
    const returnedRecipe = { ...recipe, tags: [tag], recipeCategory: [category] };
    api.recipes.patchOne.mockResolvedValue({ data: returnedRecipe, error: null });
    const wrapper = mountDialog({ modelValue: true, recipes: [recipe] });

    await wrapper.get("[data-selector=\"tags\"]").trigger("click");
    await wrapper.get("[data-selector=\"categories\"]").trigger("click");
    await wrapper.find("button[data-save]").trigger("click");
    await flushPromises();

    expect(api.recipes.patchOne).toHaveBeenCalledWith("recipe-1", {
      tags: [tag],
      recipeCategory: [category],
    });
    expect(wrapper.emitted("saved")).toEqual([[[returnedRecipe]]]);
    expect(wrapper.emitted("update:modelValue")).toEqual([[false]]);
  });

  it("can clear all organizers in a single recipe without mutating the input", async () => {
    const existingRecipe = { ...recipe, tags: [tag], recipeCategory: [category] };
    api.recipes.patchOne.mockResolvedValue({ data: existingRecipe, error: null });
    const wrapper = mountDialog({ modelValue: false, recipes: [existingRecipe] });
    await wrapper.setProps({ modelValue: true });

    await wrapper.get("button[data-clear='tags']").trigger("click");
    await wrapper.get("button[data-clear='categories']").trigger("click");
    await wrapper.find("button[data-save]").trigger("click");
    await flushPromises();

    expect(api.recipes.patchOne).toHaveBeenCalledWith("recipe-1", {
      tags: [],
      recipeCategory: [],
    });
    expect(existingRecipe.tags).toEqual([tag]);
    expect(existingRecipe.recipeCategory).toEqual([category]);
  });

  it("cancels a single-recipe edit without mutating the input recipe", async () => {
    const existingRecipe = { ...recipe, tags: [tag], recipeCategory: [category] };
    const wrapper = mountDialog({ modelValue: false, recipes: [existingRecipe] });
    await wrapper.setProps({ modelValue: true });

    await wrapper.get("[data-selector=\"tags\"]").trigger("click");
    await wrapper.get("button[data-cancel]").trigger("click");

    expect(existingRecipe.tags).toEqual([tag]);
    expect(existingRecipe.recipeCategory).toEqual([category]);
    expect(wrapper.emitted("saved")).toBeUndefined();
    expect(wrapper.emitted("update:modelValue")).toEqual([[false]]);
  });

  it("keeps a single-recipe dialog open and emits nothing when save fails", async () => {
    api.recipes.patchOne.mockResolvedValue({ data: null, error: new Error("failed") });
    const wrapper = mountDialog({ modelValue: true, recipes: [recipe] });

    await wrapper.get("[data-selector=\"tags\"]").trigger("click");
    await wrapper.find("button[data-save]").trigger("click");
    await flushPromises();

    expect(wrapper.emitted("saved")).toBeUndefined();
    expect(wrapper.emitted("update:modelValue")).toBeUndefined();
    expect(alert.error).toHaveBeenCalled();
  });

  it("does not submit bulk organization twice while the first request is pending", async () => {
    let resolveRequest!: (value: { data: typeof recipe[]; error: null }) => void;
    const request = new Promise<{ data: typeof recipe[]; error: null }>((resolve) => {
      resolveRequest = resolve;
    });
    api.bulk.bulkOrganize.mockReturnValueOnce(request);
    const wrapper = mountDialog({ modelValue: true, mode: "bulk", recipes: [recipe] });

    await wrapper.get("[data-selector=\"tags\"]").trigger("click");
    const saveButton = wrapper.find("button[data-save]");
    await saveButton.trigger("click");
    await saveButton.trigger("click");

    expect(api.bulk.bulkOrganize).toHaveBeenCalledTimes(1);

    resolveRequest({ data: [recipe], error: null });
    await flushPromises();
    expect(wrapper.emitted("saved")).toHaveLength(1);
  });

  it("disables bulk save until an organizer is selected", () => {
    const wrapper = mountDialog({ modelValue: true, mode: "bulk", recipes: [recipe] });

    expect(wrapper.find("button[data-save]").attributes("disabled")).toBeDefined();
  });
});
