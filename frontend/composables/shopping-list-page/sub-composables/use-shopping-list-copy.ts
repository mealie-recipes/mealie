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

    // Copy text into subsections based on label
    Object.entries(itemsByLabel).forEach(([label, items], idx) => {
      // for every group except the first, add a blank line
      if (idx) {
        text.push("");
      }

      // add an appropriate heading for the label depending on the copy format
      text.push(formatCopiedLabelHeading(copyType, label));

      // now add the appropriately formatted list items with the given label
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
