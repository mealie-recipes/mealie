import type { ShoppingListItemOut } from "~/lib/api/types/household";
import { useCopyList } from "~/composables/use-copy";

type CopyTypes = "plain" | "markdown";

/**
 * Composable for managing shopping list copy functionality
 */
export function useShoppingListCopy() {
  const copy = useCopyList();
  const { t } = useI18n();

  function copyListItems(itemsByLabel: { [key: string]: ShoppingListItemOut[] }, copyType: CopyTypes) {
    const text: string[] = [];
    const labelGroups = Object.entries(itemsByLabel);

    // If the list has no labeled items at all, everything is grouped under the single
    // "no label" bucket. In that case the heading is just noise, so we skip it.
    const noLabelText = t("shopping-list.no-label");
    const onlyHasNoLabelGroup = labelGroups.length === 1 && labelGroups[0][0] === noLabelText;

    labelGroups.forEach(([label, items], idx) => {
      if (idx) {
        text.push("");
      }

      if (!onlyHasNoLabelGroup) {
        text.push(formatCopiedLabelHeading(copyType, label));
      }
      items.forEach(item => text.push(formatCopiedListItem(copyType, item)));
    });

    copy.copyPlain(text);
  }

  function formatCopiedListItem(copyType: CopyTypes, item: ShoppingListItemOut): string {
    const display = item.display || "";
    switch (copyType) {
      case "markdown":
        return `- [ ] ${display}`;
      default:
        return display;
    }
  }

  function formatCopiedLabelHeading(copyType: CopyTypes, label: string): string {
    switch (copyType) {
      case "markdown":
        return `# ${label}`;
      default:
        return `[${label}]`;
    }
  }

  return {
    copyListItems,
    formatCopiedListItem,
    formatCopiedLabelHeading,
  };
}
