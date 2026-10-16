import { mount } from "@vue/test-utils";
import { defineComponent, h } from "vue";
import { createI18n } from "vue-i18n";
import { describe, expect, it } from "vitest";
import messages from "@/lang/messages/en-US.json";
import CookTime from "./CookTime.vue";

const Field = defineComponent({
  props: ["modelValue", "label", "rules", "placeholder"],
  emits: ["update:modelValue"],
  setup(props, { emit }) {
    return () => h("input", { "value": props.modelValue, "placeholder": props.placeholder, "aria-label": props.label, "onInput": (event: Event) => emit("update:modelValue", (event.target as HTMLInputElement).value) });
  },
});
function editor(value: number | null = null) {
  return mount(CookTime, {
    props: { modelValue: value, isEditMode: true },
    global: {
      plugins: [createI18n({ legacy: false, locale: "en-US", messages: { "en-US": messages } })],
      stubs: { VTextField: Field, VBtn: { template: "<button><slot /></button>" } },
    },
  });
}
describe("instruction duration in minutes with seconds storage", () => {
  it("reveals a blank optional input without emitting a duration", async () => {
    const wrapper = editor();
    expect(wrapper.findAll("input")).toHaveLength(0);
    expect(wrapper.text()).toBe("Add time");
    await wrapper.find("button").trigger("click");
    expect(wrapper.findAll("input")).toHaveLength(1);
    expect(wrapper.find("input").element.value).toBe("");
    expect(wrapper.find("input").attributes("placeholder")).toBe("Minutes");
    expect(wrapper.findAll("button")).toHaveLength(0);
    expect(wrapper.emitted("update:modelValue")).toBeUndefined();
    wrapper.unmount();
  });
  it("converts minutes to seconds, edits, and clears", async () => {
    const wrapper = editor();
    await wrapper.find("button").trigger("click");
    for (const [input, output] of [["60", 3600], ["1.5", 90], ["42", 2520], ["", null], ["0", null]] as const) {
      await wrapper.find("input").setValue(input);
      expect(wrapper.emitted("update:modelValue")?.at(-1)).toEqual([output]);
    }
    await wrapper.setProps({ modelValue: 120 });
    expect(wrapper.find("input").element.value).toBe("2");
    wrapper.unmount();
  });
  it("keeps a cleared field blank and resets disclosure on leaving edit mode", async () => {
    const wrapper = editor(90);
    await wrapper.find("input").setValue("");
    await wrapper.setProps({ modelValue: null });
    expect(wrapper.find("input").element.value).toBe("");
    await wrapper.setProps({ isEditMode: false });
    expect(wrapper.text()).toBe("");
    await wrapper.setProps({ isEditMode: true });
    expect(wrapper.findAll("input")).toHaveLength(0);
    await wrapper.find("button").trigger("click");
    expect(wrapper.find("input").element.value).toBe("");
    expect(wrapper.emitted("update:modelValue")).toEqual([[null]]);
    wrapper.unmount();
  });
  it.each([1, 61, 3661, 2147483647])("preserves exact imported %s seconds on editing", async (value) => {
    const wrapper = editor(value);
    expect(wrapper.emitted("update:modelValue")).toBeUndefined();
    await wrapper.find("input").setValue(String(value / 60));
    expect(wrapper.emitted("update:modelValue")?.at(-1)).toEqual([value]);
    wrapper.unmount();
  });
  it.each(["-1", "1.001", "35791395"])("rejects invalid %s minutes", async (value) => {
    const wrapper = editor(90);
    await wrapper.find("input").setValue(value);
    expect(wrapper.emitted("update:modelValue")).toBeUndefined();
    expect(wrapper.findComponent(Field).props("rules")[0](value)).not.toBe(true);
    wrapper.unmount();
  });
  it.each([[3661, "1h 1m 1s"], [90, "1m 30s"], [60, "1m"], [30, "30s"], [null, ""]] as const)("displays %s with units", async (value, text) => {
    const wrapper = editor(value);
    await wrapper.setProps({ isEditMode: false });
    expect(wrapper.text()).toBe(text);
    expect(wrapper.findAll("input")).toHaveLength(0);
    wrapper.unmount();
  });
});
