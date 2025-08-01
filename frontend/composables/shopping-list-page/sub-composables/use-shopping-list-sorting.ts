import type { ShoppingListOut, ShoppingListItemOut } from "~/lib/api/types/household";

interface ListItemGroup {
  position: number;
  createdAt: string;
  items: ShoppingListItemOut[];
}

/**
 * Composable for managing shopping list item sorting and organization
 */
export function useShoppingListSorting() {
  const { t } = useI18n();

  function sortItems(a: ShoppingListItemOut | ListItemGroup, b: ShoppingListItemOut | ListItemGroup) {
    // Sort by position ASC, then by createdAt ASC
    const posA = a.position ?? 0;
    const posB = b.position ?? 0;
    if (posA !== posB) {
      return posA - posB;
    }
    const createdA = a.createdAt ?? "";
    const createdB = b.createdAt ?? "";
    if (createdA !== createdB) {
      return createdA < createdB ? -1 : 1;
    }
    return 0;
  }

  function groupAndSortListItemsByFood(shoppingList: ShoppingListOut) {
    if (!shoppingList?.listItems?.length) {
      return;
    }

    const checkedItemKey = "__checkedItem";
    const listItemGroupsMap = new Map<string, ListItemGroup>();
    listItemGroupsMap.set(checkedItemKey, { position: Number.MAX_SAFE_INTEGER, createdAt: "", items: [] });

    // group items by checked status, food, or note
    shoppingList.listItems.forEach((item) => {
      const key = item.checked
        ? checkedItemKey
        : item.food?.name
          ? item.food.name
          : item.note || "";

      const group = listItemGroupsMap.get(key);
      if (!group) {
        listItemGroupsMap.set(key, { position: item.position || 0, createdAt: item.createdAt || "", items: [item] });
      }
      else {
        group.items.push(item);
      }
    });

    const listItemGroups = Array.from(listItemGroupsMap.values());
    listItemGroups.sort(sortItems);

    // sort group items, then aggregate them
    const sortedItems: ShoppingListItemOut[] = [];
    let nextPosition = 0;
    listItemGroups.forEach((listItemGroup) => {
      listItemGroup.items.sort(sortItems);
      listItemGroup.items.forEach((item) => {
        item.position = nextPosition;
        nextPosition += 1;
        sortedItems.push(item);
      });
    });

    shoppingList.listItems = sortedItems;
  }

  function sortListItems(shoppingList: ShoppingListOut) {
    if (!shoppingList?.listItems?.length) {
      return;
    }

    shoppingList.listItems.sort(sortItems);
  }

  function updateItemsByLabel(shoppingList: ShoppingListOut) {
    const items: { [prop: string]: ShoppingListItemOut[] } = {};
    const noLabelText = t("shopping-list.no-label");
    const noLabel = [] as ShoppingListItemOut[];

    shoppingList?.listItems?.forEach((item) => {
      if (item.checked) {
        return;
      }

      if (item.labelId) {
        if (item.label && item.label.name in items) {
          items[item.label.name].push(item);
        }
        else if (item.label) {
          items[item.label.name] = [item];
        }
      }
      else {
        noLabel.push(item);
      }
    });

    if (noLabel.length > 0) {
      items[noLabelText] = noLabel;
    }

    // sort the map by label order
    const orderedLabelNames = shoppingList?.labelSettings?.map(labelSetting => labelSetting.label.name);
    if (!orderedLabelNames) {
      return items;
    }

    const itemsSorted: { [prop: string]: ShoppingListItemOut[] } = {};
    if (noLabelText in items) {
      itemsSorted[noLabelText] = items[noLabelText];
    }

    orderedLabelNames.forEach((labelName) => {
      if (labelName in items) {
        itemsSorted[labelName] = items[labelName];
      }
    });

    return itemsSorted;
  }

  return {
    sortItems,
    groupAndSortListItemsByFood,
    sortListItems,
    updateItemsByLabel,
  };
}
