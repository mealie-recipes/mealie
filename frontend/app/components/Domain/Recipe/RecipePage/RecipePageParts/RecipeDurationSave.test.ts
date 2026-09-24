import { readFileSync } from "node:fs";
import { mount } from "@vue/test-utils";
import { defineComponent, h, ref } from "vue";
import { createI18n } from "vue-i18n";
import { describe, expect, it, vi } from "vitest";
import { createVuetify } from "vuetify";
import { VForm } from "vuetify/components/VForm";
import { makeValidationProps, useValidation } from "vuetify/lib/composables/validation.js";
import ts from "typescript";
import messages from "@/lang/messages/en-US.json";
import CookTime from "./CookTime.vue";

// Exercise the production save handler, not a duplicate of its validation logic.
const source = readFileSync("app/components/Domain/Recipe/RecipePage/RecipePage.vue", "utf8");
const handler = source.match(/async function saveRecipe\(\) \{[\s\S]*?\n\}/)![0];
const compiled = ts.transpileModule(handler, { compilerOptions: { target: ts.ScriptTarget.ES2022 } }).outputText;

// Keep a text input so invalid text can be tested without jsdom's number-input sanitization.
// Use the real Vuetify validation and form registration used by VTextField.
const Field = defineComponent({
  props: makeValidationProps(),
  emits: ["update:modelValue"],
  setup(props, { emit }) {
    const { errorMessages } = useValidation(props);
    return () => h("div", [
      h("input", { value: props.modelValue, onInput: (event: Event) => emit("update:modelValue", (event.target as HTMLInputElement).value) }),
      h("span", errorMessages.value.join(" ")),
    ]);
  },
});

function editor() {
  const recipe = ref({ slug: "duration-test", name: "Other edits", recipeInstructions: [{ durationMinutes: 90 as number | null }] });
  const instructionForm = ref<InstanceType<typeof VForm> | null>(null);
  const isEditForm = ref(true);
  const updateOne = vi.fn(async () => ({ data: null, error: null }));
  const setMode = vi.fn();
  const save = new Function("api", "recipe", "setMode", "PageMode", "instructionForm", "isEditForm", `${compiled}; return saveRecipe;`)(
    { recipes: { updateOne } }, recipe, setMode, { VIEW: "view" }, instructionForm, isEditForm,
  );
  const wrapper = mount(defineComponent({
    setup() {
      return () => h(VForm, { ref: instructionForm, onSubmit: (event: Event) => event.preventDefault() }, {
        default: () => h(CookTime, {
          "modelValue": recipe.value.recipeInstructions[0]!.durationMinutes,
          "isEditMode": true,
          "onUpdate:modelValue": value => recipe.value.recipeInstructions[0]!.durationMinutes = value,
        }),
      });
    },
  }), {
    global: {
      plugins: [createVuetify(), createI18n({ legacy: false, locale: "en-US", messages: { "en-US": messages } })],
      stubs: { VTextField: Field },
    },
  });
  return { wrapper, recipe, updateOne, setMode, save, instructionForm, isEditForm };
}

describe("recipe duration save validation", () => {
  it.each(["1.5", "-1", "2147483648", "invalid"])("blocks the actual save handler for %s and permits correction", async (invalid) => {
    for (const [corrected, expected] of [["42", 42], ["", null], ["0", null]] as const) {
      const { wrapper, recipe, updateOne, setMode, save } = editor();
      await wrapper.find("input").setValue(invalid);
      await save();
      expect(updateOne).not.toHaveBeenCalled();
      expect(setMode).not.toHaveBeenCalled();
      expect(wrapper.find("input").element.value).toBe(invalid);
      expect(wrapper.text()).toContain(messages.recipe["step-duration-invalid"]);
      expect(recipe.value.recipeInstructions[0]!.durationMinutes).toBe(90);
      await wrapper.find("input").setValue(corrected);
      await save();
      expect(updateOne).toHaveBeenCalledExactlyOnceWith("duration-test", recipe.value);
      expect(recipe.value.recipeInstructions[0]!.durationMinutes).toBe(expected);
      expect(recipe.value.name).toBe("Other edits");
      expect(setMode).toHaveBeenCalledWith("view");
      wrapper.unmount();
    }
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
