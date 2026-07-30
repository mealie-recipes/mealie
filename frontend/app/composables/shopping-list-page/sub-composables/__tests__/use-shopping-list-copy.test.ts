import * as vueusecore from "@vueuse/core";
import { describe, expect, test, vi } from "vitest";
import type { ShoppingListItemOut } from "~/lib/api/types/household";
import { makeWrapper } from "~/tests/utils";
import { useShoppingListCopy } from "../use-shopping-list-copy";
import { MOCK_ITEM } from "./mocks";

vi.mock("@vueuse/core", { spy: true });

const mockCopy = vi.fn().mockImplementation(args => new Promise(resolve => resolve(args)));

vi.mocked(vueusecore.useClipboard).mockImplementation(() => {
  return {
    isSupported: computed(() => true),
    copied: computed(() => true),
    text: computed(() => ""),
    copy: mockCopy,
  };
});
const wrapper = () => makeWrapper(useShoppingListCopy);

const TEST_HEADER = "SPECIAL HEADER!";

const MOCK_LIST: { [key: string]: ShoppingListItemOut[] } = {
  [TEST_HEADER]: [MOCK_ITEM],
  [TEST_HEADER + "2"]: [MOCK_ITEM],
};

describe("Shopping list copy composable", () => {
  describe("copyListItems", () => {
    test("copies markdown lists correctly", () => {
      const { copyListItems } = wrapper();
      copyListItems(MOCK_LIST, "markdown");
      const expected = [
        "# SPECIAL HEADER!",
        "- [ ] MOCK_ITEM",
        "",
        "# SPECIAL HEADER!2",
        "- [ ] MOCK_ITEM",
      ].join("\n");

      expect(mockCopy).toBeCalledWith(expected);
    });
    test("copies plain text lists correctly", () => {
      const { copyListItems } = wrapper();
      copyListItems(MOCK_LIST, "plain");
      const expected = [
        "[SPECIAL HEADER!]",
        "MOCK_ITEM",
        "",
        "[SPECIAL HEADER!2]",
        "MOCK_ITEM",
      ].join("\n");

      expect(mockCopy).toBeCalledWith(expected);
    });
  });

  describe("formatCopiedLabelHeading", () => {
    test("copies markdown headers correctly", () => {
      const { formatCopiedLabelHeading } = wrapper();
      const header = formatCopiedLabelHeading("markdown", TEST_HEADER);
      expect(header).toEqual(`# ${TEST_HEADER}`);
    });
    test("copies plain text headers correctly", () => {
      const { formatCopiedLabelHeading } = wrapper();
      const header = formatCopiedLabelHeading("plain", TEST_HEADER);
      expect(header).toEqual(`[${TEST_HEADER}]`);
    });
  });

  describe("formatCopiedListItem", () => {
    test("copies markdown items correctly", () => {
      const { formatCopiedListItem } = wrapper();
      const header = formatCopiedListItem("markdown", MOCK_ITEM);
      expect(header).toEqual(`- [ ] ${MOCK_ITEM.display}`);
    });
    test("copies plain text items correctly", () => {
      const { formatCopiedListItem } = wrapper();
      const header = formatCopiedListItem("plain", MOCK_ITEM);
      expect(header).toEqual(MOCK_ITEM.display);
    });
    test("copies items without a display as empty", () => {
      const { formatCopiedListItem } = wrapper();
      const header = formatCopiedListItem("plain", { ...MOCK_ITEM, display: undefined });
      expect(header).toEqual("");
    });
  });
});
