import { mount } from "@vue/test-utils";
import { defineComponent, h } from "vue";
import { createI18n } from "vue-i18n";
import { describe, expect, it } from "vitest";
import messages from "@/lang/messages/en-US.json";
import CookTime from "./CookTime.vue";

const Field = defineComponent({
  props: ["modelValue", "label", "rules"],
  emits: ["update:modelValue"],
  setup(props, { emit }) {
    return () => h("input", { "value": props.modelValue, "aria-label": props.label, "onInput": (event: Event) => emit("update:modelValue", (event.target as HTMLInputElement).value) });
  },
});
function editor(value: number | null = null) {
  return mount(CookTime, {
    props: { modelValue: value, isEditMode: true },
    global: {
      plugins: [createI18n({ legacy: false, locale: "en-US", messages: { "en-US": messages } })],
      stubs: { VTextField: Field },
    },
  });
}
describe("instruction minutes", () => {
  it("always shows one blank input, saves, edits, and clears with blank or zero without buttons", async () => {
    const wrapper = editor();
    expect(wrapper.findAll("input")).toHaveLength(1);
    expect(wrapper.find("input").element.value).toBe("");
    expect(wrapper.findAll("button")).toHaveLength(0);
    for (const [input, output] of [["90", 90], ["42", 42], ["", null], ["0", null]] as const) {
      await wrapper.find("input").setValue(input);
      expect(wrapper.emitted("update:modelValue")?.at(-1)).toEqual([output]);
    }
    await wrapper.setProps({ modelValue: 120 });
    expect(wrapper.find("input").element.value).toBe("120");
    wrapper.unmount();
  });
  it.each(["-1", "1.5", "2147483648"])("rejects invalid %s", async (value) => {
    const wrapper = editor(90);
    await wrapper.find("input").setValue(value);
    expect(wrapper.emitted("update:modelValue")).toBeUndefined();
    expect(wrapper.findComponent(Field).props("rules")[0](value)).not.toBe(true);
    wrapper.unmount();
  });
  it.each([[90, "1h 30m"], [60, "1h"], [30, "30m"], [null, ""]] as const)("displays %s with units", async (value, text) => {
    const wrapper = editor(value);
    await wrapper.setProps({ isEditMode: false });
    expect(wrapper.text()).toBe(text);
    expect(wrapper.findAll("input")).toHaveLength(0);
    wrapper.unmount();
  });
});
