import { readFileSync } from "node:fs";
import { mount } from "@vue/test-utils";
import { defineComponent, h, ref } from "vue";
import { createI18n } from "vue-i18n";
import { describe, expect, it, vi } from "vitest";
import { createVuetify } from "vuetify";
import { VForm } from "vuetify/components/VForm";
import { VTextField } from "vuetify/components/VTextField";
import ts from "typescript";
import messages from "@/lang/messages/en-US.json";
import CookTime from "./CookTime.vue";

// Exercise the production save handler, not a duplicate of its validation logic.
const source = readFileSync("app/components/Domain/Recipe/RecipePage/RecipePage.vue", "utf8");
const handler = source.match(/async function saveRecipe\(\) \{[\s\S]*?\n\}/)![0];
const compiled = ts.transpileModule(handler, { compilerOptions: { target: ts.ScriptTarget.ES2022 } }).outputText;

function editor(value = 90) {
  const recipe = ref({ slug: "duration-test", name: "Other edits", recipeInstructions: [{ durationSeconds: value as number | null }] });
  const instructionForm = ref<InstanceType<typeof VForm> | null>(null);
  const isEditForm = ref(true);
  const updateOne = vi.fn(async () => ({ data: null, error: null }));
  const setMode = vi.fn();
  const save = new Function("api", "recipe", "setMode", "PageMode", "instructionForm", "isEditForm", "route", `${compiled}; return saveRecipe;`)(
    { recipes: { updateOne } }, recipe, setMode, { VIEW: "view" }, instructionForm, isEditForm, { params: { slug: "duration-test" } },
  );
  const wrapper = mount(defineComponent({
    setup() {
      return () => h(VForm, { ref: instructionForm, onSubmit: (event: Event) => event.preventDefault() }, {
        default: () => h(CookTime, {
          "modelValue": recipe.value.recipeInstructions[0]!.durationSeconds,
          "isEditMode": true,
          "onUpdate:modelValue": value => recipe.value.recipeInstructions[0]!.durationSeconds = value,
        }),
      });
    },
  }), {
    global: {
      plugins: [createVuetify(), createI18n({ legacy: false, locale: "en-US", messages: { "en-US": messages } })],
      components: { VTextField },
    },
  });
  return { wrapper, recipe, updateOne, setMode, save, instructionForm, isEditForm };
}

describe("recipe duration save validation", () => {
  it("initializes individual and bulk-added instructions with null durations", () => {
    const addSource = source.match(/function addStep\([\s\S]*?\n\}/)![0];
    const addCompiled = ts.transpileModule(addSource, { compilerOptions: { target: ts.ScriptTarget.ES2022 } }).outputText;
    const recipe = ref({ recipeInstructions: [] as { durationSeconds?: number | null }[] });
    const addStep = new Function("recipe", "uuid4", `${addCompiled}; return addStep;`)(recipe, () => "test-id");
    addStep();
    addStep(["One", "Two"]);
    expect(recipe.value.recipeInstructions.map(step => step.durationSeconds)).toEqual([null, null, null]);
  });
  it.each(["1.5", "1.001", "-1", "35791395"])("blocks the actual save handler for %s and permits correction", async (invalid) => {
    for (const [corrected, expected] of [["42", 2520], ["", null], ["0", null]] as const) {
      const { wrapper, recipe, updateOne, setMode, save } = editor();
      await wrapper.find("input").setValue(invalid);
      await save();
      expect(updateOne).not.toHaveBeenCalled();
      expect(setMode).not.toHaveBeenCalled();
      expect(wrapper.find("input").element.value).toBe(invalid);
      expect(wrapper.text()).toContain(messages.recipe["step-duration-invalid"]);
      expect(recipe.value.recipeInstructions[0]!.durationSeconds).toBe(90);
      await wrapper.find("input").setValue(corrected);
      await save();
      expect(updateOne).toHaveBeenCalledExactlyOnceWith("duration-test", recipe.value);
      expect(recipe.value.recipeInstructions[0]!.durationSeconds).toBe(expected);
      expect(recipe.value.name).toBe("Other edits");
      expect(setMode).toHaveBeenCalledWith("view");
      wrapper.unmount();
    }
  });
  it.each(["1e", "-"])("blocks sanitized incomplete native input %s until corrected or deliberately cleared", async (invalid) => {
    const { wrapper, recipe, updateOne, save } = editor();
    const field = wrapper.find("input");
    expect(field.attributes("type")).toBe("number");
    // jsdom sanitizes the value but cannot emulate keyboard-driven badInput.
    // Model that native validity flag on the actual VTextField input, not a text stub.
    field.element.value = invalid;
    expect(field.element.value).toBe("");
    const badInput = vi.spyOn(field.element.validity, "badInput", "get").mockReturnValue(true);
    await field.trigger("input");
    await save();
    await save();
    expect(updateOne).not.toHaveBeenCalled();
    expect(recipe.value.recipeInstructions[0]!.durationSeconds).toBe(90);
    expect(wrapper.text()).toContain(messages.recipe["step-duration-invalid"]);
    badInput.mockReturnValue(false);
    // An input event with an actually empty, valid control is a deliberate clear.
    await field.trigger("input");
    await save();
    expect(updateOne).toHaveBeenCalledExactlyOnceWith("duration-test", recipe.value);
    expect(recipe.value.recipeInstructions[0]!.durationSeconds).toBeNull();
    badInput.mockRestore();
    wrapper.unmount();
  });
  it.each([1, 61, 90, 1048708914, 2094174799, 2147483647])("saves untouched imported %s seconds through the native field", async (value) => {
    const { wrapper, recipe, updateOne, save } = editor(value);
    const field = wrapper.find("input");
    expect(field.attributes("type")).toBe("number");
    expect(field.element.value).toBe(String(Math.floor(value / 60)));
    expect(field.attributes("step")).toBe("1");
    expect(wrapper.text()).toContain("Saved duration:");
    await save();
    expect(updateOne).toHaveBeenCalledExactlyOnceWith("duration-test", recipe.value);
    expect(recipe.value.recipeInstructions[0]!.durationSeconds).toBe(value);
    // Deliberately editing replaces the imported duration with whole minutes.
    await field.setValue("2");
    await save();
    expect(updateOne).toHaveBeenCalledTimes(2);
    expect(recipe.value.recipeInstructions[0]!.durationSeconds).toBe(120);
    wrapper.unmount();
  });
  it("fails closed without the edit form but preserves non-edit saves", async () => {
    const { wrapper, recipe, updateOne, setMode, save, instructionForm, isEditForm } = editor();
    instructionForm.value = null;
    await save();
    expect(updateOne).not.toHaveBeenCalled();
    expect(setMode).not.toHaveBeenCalled();
    isEditForm.value = false;
    await save();
    expect(updateOne).toHaveBeenCalledExactlyOnceWith("duration-test", recipe.value);
    wrapper.unmount();
  });
  it("routes both Save controls through the validated handler and scopes validation to instructions", () => {
    expect(source).toMatch(/<RecipePageHeader[\s\S]*?@save="saveRecipe"/);
    expect(source).toMatch(/<v-fab[\s\S]*?@click="saveRecipe"/);
    expect(source).toMatch(/<v-form ref="instructionForm" @submit.prevent>\s*<RecipePageInstructions[\s\S]*?\/?>\s*<\/v-form>/);
  });
});
