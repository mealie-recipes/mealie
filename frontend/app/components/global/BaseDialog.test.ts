import { mount } from "@vue/test-utils";
import { describe, expect, test } from "vitest";
import BaseDialog from "./BaseDialog.vue";

function mountDialog(props: Record<string, unknown>) {
  return mount(BaseDialog, {
    props: { modelValue: true, ...props },
    global: {
      mocks: {
        $vuetify: { display: { xs: false } },
      },
      stubs: {
        // the keydown listener falls through to this element
        VDialog: { template: "<div class=\"dialog\"><slot /></div>" },
        BaseDialogContent: { template: "<div><slot /></div>" },
      },
    },
  });
}

describe("BaseDialog submit on Enter", () => {
  test("submits when submit is enabled", async () => {
    const wrapper = mountDialog({ canSubmit: true });
    await wrapper.find(".dialog").trigger("keydown", { key: "Enter" });
    expect(wrapper.emitted("submit")).toHaveLength(1);
  });

  test("does not submit when submit is disabled", async () => {
    const wrapper = mountDialog({ canSubmit: true, submitDisabled: true });
    await wrapper.find(".dialog").trigger("keydown", { key: "Enter" });
    expect(wrapper.emitted("submit")).toBeUndefined();
  });

  test("does not confirm when submit is disabled", async () => {
    const wrapper = mountDialog({ canConfirm: true, submitDisabled: true });
    await wrapper.find(".dialog").trigger("keydown", { key: "Enter" });
    expect(wrapper.emitted("confirm")).toBeUndefined();
  });

  test("does not submit when submit on Enter is turned off", async () => {
    const wrapper = mountDialog({ canSubmit: true, disableSubmitOnEnter: true });
    await wrapper.find(".dialog").trigger("keydown", { key: "Enter" });
    expect(wrapper.emitted("submit")).toBeUndefined();
  });
});
