import type { ShoppingListItemOut } from "~/lib/api/types/household";
import { useCopyList } from "~/composables/use-copy";

type CopyTypes = "plain" | "markdown";

/**
 * Composable for managing shopping list copy functionality
 */
export function useShoppingListCopy() {
  const copy = useCopyList();

  function copyListItems(itemsByLabel: { [key: string]: ShoppingListItemOut[] }, copyType: CopyTypes) {
    const text: string[] = [];
    Object.entries(itemsByLabel).forEach(([label, items], idx) => {
      if (idx) {
        text.push("");
      }

      text.push(formatCopiedLabelHeading(copyType, label));
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
