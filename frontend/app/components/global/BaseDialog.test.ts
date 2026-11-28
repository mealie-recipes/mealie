import { mount } from "@vue/test-utils";
import { describe, expect, test } from "vitest";
import BaseDialog from "./BaseDialog.vue";
import BaseDialogContent from "./BaseDialogContent.vue";

const xsDisplay = {
  $vuetify: {
    display: {
      xs: true,
    },
  },
};

const BaseButton = {
  template: "<button type=\"button\"><slot /></button>",
};

describe("BaseDialog", () => {
  test("caps a mobile bottom sheet above the safe area inset", ({ onTestFinished }) => {
    const wrapper = mount(BaseDialog, {
      props: {
        bottomSheet: true,
        modelValue: true,
      },
      global: {
        components: { BaseDialogContent },
        mocks: xsDisplay,
        stubs: {
          BaseButton,
          VBottomSheet: {
            props: ["contentProps"],
            template: "<div><div class=\"sheet-style\">{{ contentProps.style }}</div><slot /></div>",
          },
        },
      },
    });

    onTestFinished(() => wrapper.unmount());

    const style = wrapper.get(".sheet-style").text();
    expect(style).toContain("100dvh");
    expect(style).toContain("env(safe-area-inset-bottom");
  });
});

describe("BaseDialogContent", () => {
  test("sizes a bottom sheet card to its content under the viewport cap", ({ onTestFinished }) => {
    const wrapper = mount(BaseDialogContent, {
      props: { bottomSheet: true },
      global: {
        mocks: xsDisplay,
        stubs: { BaseButton },
      },
    });

    onTestFinished(() => wrapper.unmount());

    expect(wrapper.classes()).toContain("base-dialog-sheet-card");
    expect(wrapper.attributes("height")).not.toBe("100%");
  });

  test("keeps a regular dialog card filling the overlay", ({ onTestFinished }) => {
    const wrapper = mount(BaseDialogContent, {
      props: { bottomSheet: false },
      global: {
        mocks: xsDisplay,
        stubs: { BaseButton },
      },
    });

    onTestFinished(() => wrapper.unmount());

    expect(wrapper.attributes("height")).toBe("100%");
  });
});
