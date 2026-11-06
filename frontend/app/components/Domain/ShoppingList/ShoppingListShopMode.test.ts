import { mount } from "@vue/test-utils";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { defineComponent, nextTick } from "vue";
import ShoppingListShopMode from "./ShoppingListShopMode.vue";
import { MOCK_ITEM } from "~/composables/shopping-list-page/sub-composables/__tests__/mocks";
import type { ShoppingListItemOut } from "~/lib/api/types/household";

vi.mock("~/composables/recipes", () => ({
  useIngredientTextParser: () => ({
    useParsedIngredientText: (item: ShoppingListItemOut) => ({
      quantity: item.quantity ? String(item.quantity) : undefined,
      unit: item.unit?.name,
      name: item.food?.name,
      note: item.note,
    }),
  }),
}));

const VSwitch = defineComponent({
  name: "VSwitch",
  props: { modelValue: Boolean, label: { type: String, default: "" } },
  emits: ["update:modelValue"],
  template: `<label class="switch"><input type="checkbox" :checked="modelValue" @change="$emit('update:modelValue', !modelValue)">{{ label }}</label>`,
});

const stubs = {
  VSwitch,
  VIcon: { template: "<i />" },
  VBtn: { template: `<button class="close" @click="$emit('click')"><slot /></button>`, emits: ["click"] },
  SafeMarkdown: { props: ["source"], template: "<div>{{ source }}</div>" },
};

const milk = {
  ...MOCK_ITEM,
  id: "milk",
  food: { id: "1", name: "Milk" },
  quantity: 2,
  unit: { id: "u", name: "l" },
  note: "low fat, the one in the blue carton",
} as ShoppingListItemOut;
const butter = { ...MOCK_ITEM, id: "butter", food: { id: "2", name: "Butter" } } as ShoppingListItemOut;
const onlyNote = { ...MOCK_ITEM, id: "note", note: "Birthday candles" } as ShoppingListItemOut;
const done = { ...MOCK_ITEM, id: "done", checked: true, food: { id: "3", name: "Rice" } } as ShoppingListItemOut;

function mountMode(props: Record<string, unknown> = {}) {
  return mount(ShoppingListShopMode, {
    props: {
      listName: "Sample list",
      sections: [
        { label: "Dairy", items: [milk, butter] },
        { label: "Other", items: [onlyNote] },
      ],
      checkedItems: [done],
      remainingCount: 3,
      getLabelColor: () => undefined,
      showChecked: false,
      ...props,
    },
    global: {
      stubs,
      mocks: { $globals: { icons: { close: "close" } } },
    },
  });
}

function rows(wrapper: ReturnType<typeof mountMode>) {
  return wrapper.findAll(".shop-item");
}

// jsdom has no PointerEvent, and trigger() can't set coordinates on the MouseEvent it falls back to
function pointer(row: ReturnType<typeof rows>[number], type: string, clientX: number, clientY: number) {
  row.element.dispatchEvent(new MouseEvent(type, { clientX, clientY, bubbles: true }));
}

async function tap(row: ReturnType<typeof rows>[number]) {
  pointer(row, "pointerdown", 10, 10);
  await row.trigger("click");
}

describe("ShoppingListShopMode", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-01-01T12:00:00Z"));
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  describe("content", () => {
    test("shows the remaining count and the sections in order", () => {
      const wrapper = mountMode();
      expect(wrapper.find(".shop-mode__remaining").text()).toBe("3 left");
      expect(wrapper.findAll(".shop-mode__section-title").map(title => title.text())).toEqual(["Dairy · 2", "Other · 1"]);
    });

    test("shows name, amount and note of a row", () => {
      const row = rows(mountMode())[0]!;
      expect(row.find(".shop-item__name").text()).toBe("Milk");
      expect(row.find(".shop-item__quantity").text()).toBe("2");
      expect(row.find(".shop-item__unit").text()).toBe("l");
      expect(row.find(".shop-item__note").text()).toBe(milk.note);
      expect(row.find(".shop-item__note").classes()).toContain("text-truncate");
    });

    test("names a row without a food after its note, and shows the note only once", () => {
      const row = rows(mountMode())[2]!;
      expect(row.find(".shop-item__name").text()).toBe("Birthday candles");
      expect(row.find(".shop-item__note").exists()).toBe(false);
    });

    test("has no controls for editing or adding", () => {
      const html = mountMode().html();
      expect(html).not.toMatch(/handle|ShoppingListAddItemForm|QuickAdd|v-menu/);
      expect(mountMode().findAll("input[type='text'], select, textarea")).toHaveLength(0);
    });
  });

  describe("tapping a row", () => {
    test("toggles the item", async () => {
      const wrapper = mountMode();
      await tap(rows(wrapper)[1]!);
      expect(wrapper.emitted("toggle")).toEqual([[butter]]);
    });

    test.each([
      ["sideways", 30, 10],
      ["down", 10, 30],
    ])("doesn't toggle when the finger moved %s", async (_, clientX, clientY) => {
      const wrapper = mountMode();
      const row = rows(wrapper)[0]!;
      pointer(row, "pointerdown", 10, 10);
      pointer(row, "pointermove", clientX, clientY);
      await row.trigger("click");
      expect(wrapper.emitted("toggle")).toBeUndefined();
    });

    test("tolerates a small finger movement", async () => {
      const wrapper = mountMode();
      const row = rows(wrapper)[0]!;
      pointer(row, "pointerdown", 10, 10);
      pointer(row, "pointermove", 14, 15);
      await row.trigger("click");
      expect(wrapper.emitted("toggle")).toHaveLength(1);
    });

    test("doesn't toggle when the browser took the touch over for scrolling", async () => {
      const wrapper = mountMode();
      const row = rows(wrapper)[0]!;
      pointer(row, "pointerdown", 10, 10);
      await row.trigger("pointercancel");
      await row.trigger("click");
      expect(wrapper.emitted("toggle")).toBeUndefined();
    });

    test("a moved touch doesn't affect the next tap", async () => {
      const wrapper = mountMode();
      const row = rows(wrapper)[0]!;
      pointer(row, "pointerdown", 10, 10);
      await row.trigger("pointercancel");
      await tap(row);
      expect(wrapper.emitted("toggle")).toHaveLength(1);
    });

    test("ignores the second tap of a double tap, on the same row", async () => {
      const wrapper = mountMode();
      const row = rows(wrapper)[0]!;
      await tap(row);
      vi.advanceTimersByTime(150);
      await tap(row);
      expect(wrapper.emitted("toggle")).toHaveLength(1);
    });

    test("ignores the second tap of a double tap on the row that moved up", async () => {
      const wrapper = mountMode();
      await tap(rows(wrapper)[0]!);
      vi.advanceTimersByTime(150);
      await tap(rows(wrapper)[1]!);
      expect(wrapper.emitted("toggle")).toEqual([[milk]]);
    });

    test("accepts the next tap after the guard", async () => {
      const wrapper = mountMode();
      await tap(rows(wrapper)[0]!);
      vi.advanceTimersByTime(400);
      await tap(rows(wrapper)[1]!);
      expect(wrapper.emitted("toggle")).toEqual([[milk], [butter]]);
    });

    test.each(["enter", "space"])("works with the %s key", async (key) => {
      const wrapper = mountMode();
      await rows(wrapper)[0]!.trigger(`keydown.${key}`);
      expect(wrapper.emitted("toggle")).toEqual([[milk]]);
    });
  });

  describe("completed switch", () => {
    test("shows the count in its label", () => {
      expect(mountMode().find(".switch").text()).toBe("Show completed (1)");
    });

    test("hides checked items while off", () => {
      const wrapper = mountMode();
      expect(rows(wrapper).map(row => row.attributes("aria-pressed"))).not.toContain("true");
      expect(wrapper.text()).not.toContain("Rice");
    });

    test("asks to turn on through the model", async () => {
      const wrapper = mountMode();
      await wrapper.find(".switch input").trigger("change");
      expect(wrapper.emitted("update:showChecked")).toEqual([[true]]);
    });

    test("shows checked items at the end while on", () => {
      const all = rows(mountMode({ showChecked: true }));
      expect(all).toHaveLength(4);
      expect(all[3]!.text()).toContain("Rice");
      expect(all[3]!.classes()).toContain("shop-item--checked");
      expect(all[3]!.attributes("aria-pressed")).toBe("true");
    });

    test("a tap on a checked item asks to toggle it back", async () => {
      const wrapper = mountMode({ showChecked: true });
      await tap(rows(wrapper)[3]!);
      expect(wrapper.emitted("toggle")).toEqual([[done]]);
    });

    test("a list that changes the item ids is simply rendered from the new list", async () => {
      // unchecking can make the backend merge the item into another one, under that one's id
      const wrapper = mountMode({ showChecked: true });
      const merged = { ...milk, id: "merged-into", quantity: 3 };
      await wrapper.setProps({
        sections: [{ label: "Dairy", items: [merged, butter] }],
        checkedItems: [],
        remainingCount: 2,
      });
      await nextTick();
      expect(rows(wrapper)).toHaveLength(2);
      await tap(rows(wrapper)[0]!);
      expect(wrapper.emitted("toggle")).toEqual([[merged]]);
    });
  });

  test("the close button asks to close", async () => {
    const wrapper = mountMode();
    await wrapper.find(".close").trigger("click");
    expect(wrapper.emitted("close")).toHaveLength(1);
  });
});
