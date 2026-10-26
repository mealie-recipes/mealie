import { mount, type VueWrapper } from "@vue/test-utils";
import { afterEach, describe, expect, test } from "vitest";
import { nextTick } from "vue";
import RecipeDataAliasManagerDialog from "./RecipeDataAliasManagerDialog.vue";
import type { IngredientFood } from "~/lib/api/types/recipe";

const wrappers: VueWrapper[] = [];

function mountDialog(data: IngredientFood) {
  const wrapper = mount(RecipeDataAliasManagerDialog, {
    props: {
      data,
      modelValue: true,
    },
    global: {
      mocks: {
        $globals: {
          icons: {
            edit: "edit",
            check: "check",
            delete: "delete",
            create: "create",
          },
        },
      },
      stubs: {
        BaseDialog: {
          template: `
            <div>
              <slot />
              <slot name="custom-card-action" />
              <button class="dialog-submit" type="button" @click="$emit('submit')" />
              <button class="dialog-cancel" type="button" @click="$emit('cancel')" />
            </div>
          `,
        },
        BaseButton: {
          template: "<button type=\"button\"><slot /></button>",
        },
        BaseButtonGroup: {
          template: "<div />",
        },
        VCardText: {
          template: "<div><slot /></div>",
        },
        VContainer: {
          template: "<div><slot /></div>",
        },
        VRow: {
          template: "<div><slot /></div>",
        },
        VCol: {
          template: "<div><slot /></div>",
        },
        VTextField: {
          props: ["modelValue"],
          template: "<input :value=\"modelValue\" @input=\"$emit('update:modelValue', $event.target.value)\">",
        },
      },
    },
  });

  wrappers.push(wrapper);

  return wrapper;
}

describe("RecipeDataAliasManagerDialog", () => {
  afterEach(() => {
    wrappers.forEach(wrapper => wrapper.unmount());
    wrappers.length = 0;
  });

  test("cancel discards alias edits", async () => {
    const data = {
      id: "1",
      name: "abalone",
      aliases: [{ name: "alias-original" }],
    } as IngredientFood;
    const wrapper = mountDialog(data);

    await wrapper.find("input").setValue("alias-cancelled");
    await wrapper.find(".dialog-cancel").trigger("click");
    await nextTick();

    expect(wrapper.emitted("cancel")).toHaveLength(1);
    expect(wrapper.emitted("submit")).toBeUndefined();
    expect(data.aliases).toEqual([{ name: "alias-original" }]);
  });

  test("confirm emits the edited aliases", async () => {
    const data = {
      id: "1",
      name: "abalone",
      aliases: [{ name: "alias-original" }],
    } as IngredientFood;
    const wrapper = mountDialog(data);

    await wrapper.find("input").setValue("alias-renamed");
    await wrapper.find(".dialog-submit").trigger("click");
    await nextTick();

    expect(wrapper.emitted("submit")).toEqual([[[{ name: "alias-renamed" }]]]);
  });
});
