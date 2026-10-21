import { mount } from "@vue/test-utils";
import { createI18n } from "vue-i18n";
import { describe, expect, it, vi } from "vitest";
import { createVuetify } from "vuetify";
import { VTextField } from "vuetify/components/VTextField";
import messages from "@/lang/messages/en-US.json";
import CookTime from "./CookTime.vue";

function editor(value: number | null = null) {
  return mount(CookTime, {
    props: { modelValue: value, isEditMode: true },
    global: {
      plugins: [createVuetify(), createI18n({ legacy: false, locale: "en-US", messages: { "en-US": messages } })],
      components: { VTextField },
    },
  });
}
describe("instruction duration in minutes with seconds storage", () => {
  it("always shows a blank optional input without emitting a duration", () => {
    const wrapper = editor();
    expect(wrapper.findAll("input")).toHaveLength(1);
    expect(wrapper.find("input").element.value).toBe("");
    expect(wrapper.find("input").attributes("placeholder")).toBe("Minutes");
    expect(wrapper.findAll("button")).toHaveLength(0);
    expect(wrapper.emitted("update:modelValue")).toBeUndefined();
    wrapper.unmount();
  });
  it("converts minutes to seconds, edits, and clears", async () => {
    const wrapper = editor();
    for (const [input, output] of [["60", 3600], ["35791394", 2147483640], ["42", 2520], ["", null], ["0", null]] as const) {
      await wrapper.find("input").setValue(input);
      expect(wrapper.emitted("update:modelValue")?.at(-1)).toEqual([output]);
    }
    await wrapper.setProps({ modelValue: 120 });
    expect(wrapper.find("input").element.value).toBe("2");
    wrapper.unmount();
  });
  it.each([1, 61, 3661, 1048708914, 2094174799, 2147483647])("preserves exact imported %s seconds on editing", async (value) => {
    const wrapper = editor(value);
    expect(wrapper.emitted("update:modelValue")).toBeUndefined();
    expect(wrapper.find("input").element.value).toBe(String(Math.floor(value / 60)));
    expect(wrapper.find("input").attributes("type")).toBe("number");
    expect(wrapper.text()).toContain("Saved duration:");
    expect(await wrapper.findComponent(VTextField).vm.validate()).toEqual([]);
    expect(wrapper.emitted("update:modelValue")).toBeUndefined();
    await wrapper.find("input").setValue("2");
    expect(wrapper.emitted("update:modelValue")?.at(-1)).toEqual([120]);
    wrapper.unmount();
  });
  it.each(["-1", "1.5", "1.001", "35791394.1", "35791395"])("rejects invalid %s minutes", async (value) => {
    const wrapper = editor(90);
    await wrapper.find("input").setValue(value);
    expect(wrapper.emitted("update:modelValue")).toBeUndefined();
    expect(await wrapper.findComponent(VTextField).vm.validate()).toEqual(["Must Be A Whole Number"]);
    wrapper.unmount();
  });
  it.each(["1e", "-"])("does not clear sanitized incomplete input %s", async (value) => {
    const wrapper = editor(90);
    const field = wrapper.find("input");
    field.element.value = value;
    expect(field.element.value).toBe("");
    // jsdom sanitizes number input but does not implement keyboard-driven badInput.
    const badInput = vi.spyOn(field.element.validity, "badInput", "get").mockReturnValue(true);
    try {
      await field.trigger("input");
      expect(wrapper.emitted("update:modelValue")).toBeUndefined();
      expect(await wrapper.findComponent(VTextField).vm.validate()).toEqual(["Must Be A Whole Number"]);
      badInput.mockReturnValue(false);
      await field.trigger("input");
      expect(wrapper.emitted("update:modelValue")).toEqual([[null]]);
      expect(await wrapper.findComponent(VTextField).vm.validate()).toEqual([]);
    }
    finally {
      badInput.mockRestore();
      wrapper.unmount();
    }
  });
  it.each([[3661, "1h 1m 1s"], [90, "1m 30s"], [60, "1m"], [30, "30s"], [null, ""]] as const)("displays %s with units", async (value, text) => {
    const wrapper = editor(value);
    await wrapper.setProps({ isEditMode: false });
    expect(wrapper.text()).toBe(text);
    expect(wrapper.findAll("input")).toHaveLength(0);
    wrapper.unmount();
  });
});
