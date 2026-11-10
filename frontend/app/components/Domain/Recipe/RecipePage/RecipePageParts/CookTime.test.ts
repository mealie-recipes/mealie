import { mount } from "@vue/test-utils";
import { createI18n } from "vue-i18n";
import { describe, expect, it } from "vitest";
import { createVuetify } from "vuetify";
import { VNumberInput } from "vuetify/components/VNumberInput";
import messages from "@/lang/messages/en-US.json";
import CookTime from "./CookTime.vue";

function editor(value: number | null = null) {
  return mount(CookTime, {
    props: { modelValue: value, isEditMode: true },
    global: {
      plugins: [createVuetify(), createI18n({ legacy: false, locale: "en-US", messages: { "en-US": messages } })],
      components: { VNumberInput },
    },
  });
}
describe("instruction duration in minutes with seconds storage", () => {
  it("always shows a blank optional input without emitting a duration", () => {
    const wrapper = editor();
    expect(wrapper.findAll("input")).toHaveLength(1);
    expect(wrapper.find("input").element.value).toBe("");
    expect(wrapper.find("input").attributes("placeholder")).toBe("Minutes");
    expect(wrapper.emitted("update:modelValue")).toBeUndefined();
    wrapper.unmount();
  });
  it("converts minutes to seconds, edits, and clears", async () => {
    const wrapper = editor();
    for (const [input, output] of [["60", 3600], ["35791394", 2147483640], ["42", 2520], ["", null]] as const) {
      await wrapper.find("input").setValue(input);
      expect(wrapper.emitted("update:modelValue")?.at(-1)).toEqual([output]);
      await wrapper.setProps({ modelValue: output });
    }
    await wrapper.setProps({ modelValue: 120 });
    expect(wrapper.find("input").element.value).toBe("2");
    wrapper.unmount();
  });
  it("blocks typing a minus sign", async () => {
    const wrapper = editor();
    const event = new KeyboardEvent("keypress", { key: "-", bubbles: true, cancelable: true });
    wrapper.find("input").element.dispatchEvent(event);
    expect(event.defaultPrevented).toBe(true);
    wrapper.unmount();
  });
  it("clears the duration for 0 minutes but keeps showing 0", async () => {
    const wrapper = editor(120);
    await wrapper.find("input").setValue("0");
    expect(wrapper.emitted("update:modelValue")?.at(-1)).toEqual([null]);
    await wrapper.setProps({ modelValue: null });
    expect(wrapper.find("input").element.value).toBe("0");
    wrapper.unmount();
  });
  it.each([1, 61, 3661, 1048708914, 2094174799, 2147483647])("preserves exact imported %s seconds until edited", async (value) => {
    const wrapper = editor(value);
    expect(wrapper.find("input").element.value).toBe(String(Math.floor(value / 60)));
    expect(wrapper.text()).toContain("Saved duration:");
    await wrapper.find("input").trigger("blur");
    expect(wrapper.emitted("update:modelValue")).toBeUndefined();
    await wrapper.find("input").setValue("2");
    expect(wrapper.emitted("update:modelValue")?.at(-1)).toEqual([120]);
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
