import { beforeEach, describe, expect, test, vi } from "vitest";
import { useAddToShoppingListDialog, useNewShoppingListForm } from "../use-add-to-shopping-list-dialog";
import type { ShoppingListSummary } from "~/lib/api/types/household";

const getAll = vi.fn();
const createOne = vi.fn();
const alertError = vi.hoisted(() => vi.fn());

vi.mock("~/composables/api", () => ({
  useUserApi: () => ({
    shopping: {
      lists: { getAll, createOne },
    },
  }),
}));
vi.mock("~/composables/use-toast", () => ({
  alert: { error: alertError },
}));
vi.mock("vue-i18n", async importOriginal => ({
  ...(await importOriginal<typeof import("vue-i18n")>()),
  useI18n: () => ({ t: (key: string) => key }),
}));

function createList(id: string, name = `List ${id}`): ShoppingListSummary {
  return {
    id,
    name,
    groupId: "my-group-id",
    userId: "my-user-id",
    householdId: "my-household-id",
    recipeReferences: [],
    labelSettings: [],
  };
}

beforeEach(() => {
  getAll.mockReset();
  createOne.mockReset();
  alertError.mockReset();
});

describe("useAddToShoppingListDialog", () => {
  test("loads the lists before opening the dialog", async () => {
    const lists = [createList("1"), createList("2")];
    getAll.mockResolvedValue({ data: { items: lists } });
    const { shoppingLists, open, addAllToList } = useAddToShoppingListDialog();

    await addAllToList();

    expect(shoppingLists.value).toEqual(lists);
    expect(open.value).toBe(true);
  });

  test("keeps a list that was created from the dialog", async () => {
    getAll.mockResolvedValue({ data: { items: [createList("1")] } });
    const { shoppingLists, getShoppingLists, addShoppingList } = useAddToShoppingListDialog();
    await getShoppingLists();

    addShoppingList(createList("2"));

    expect(shoppingLists.value?.map(({ id }) => id)).toEqual(["1", "2"]);
  });

  test("can take a created list before any lists were loaded", () => {
    const { shoppingLists, addShoppingList } = useAddToShoppingListDialog();

    addShoppingList(createList("1"));

    expect(shoppingLists.value?.map(({ id }) => id)).toEqual(["1"]);
  });

  test("doesn't add the same list twice", async () => {
    getAll.mockResolvedValue({ data: { items: [createList("1")] } });
    const { shoppingLists, getShoppingLists, addShoppingList } = useAddToShoppingListDialog();
    await getShoppingLists();

    addShoppingList(createList("1"));

    expect(shoppingLists.value).toHaveLength(1);
  });
});

describe("useNewShoppingListForm", () => {
  test("creates a list from the trimmed name and closes the form", async () => {
    const list = createList("1", "Groceries");
    createOne.mockResolvedValue({ data: list });
    const { form, create } = useNewShoppingListForm();
    form.show = true;
    form.name = "  Groceries ";

    const created = await create();

    expect(createOne).toHaveBeenCalledExactlyOnceWith({ name: "Groceries" });
    expect(created).toEqual(list);
    expect(form).toEqual({ show: false, name: "", loading: false });
    expect(alertError).not.toHaveBeenCalled();
  });

  test.each(["", "   "])("doesn't create a list named %j", async (name) => {
    const { form, create } = useNewShoppingListForm();
    form.show = true;
    form.name = name;

    expect(await create()).toBeNull();
    expect(createOne).not.toHaveBeenCalled();
    expect(form.show).toBe(true);
  });

  test("is loading while the list is being created, and ignores another submit until it's done", async () => {
    let resolve!: (value: unknown) => void;
    createOne.mockReturnValue(new Promise(r => (resolve = r)));
    const { form, create } = useNewShoppingListForm();
    form.name = "Groceries";

    const pending = create();
    expect(form.loading).toBe(true);
    expect(await create()).toBeNull();

    resolve({ data: createList("1", "Groceries") });
    await pending;

    expect(form.loading).toBe(false);
    expect(createOne).toHaveBeenCalledOnce();
  });

  test("reports a failure and leaves the form open for another try", async () => {
    createOne.mockResolvedValue({ data: null });
    const { form, create } = useNewShoppingListForm();
    form.show = true;
    form.name = "Groceries";

    expect(await create()).toBeNull();

    expect(alertError).toHaveBeenCalledExactlyOnceWith("shopping-list.failed-to-create-shopping-list");
    expect(form).toEqual({ show: true, name: "Groceries", loading: false });
  });

  test("reset discards what was typed", () => {
    const { form, reset } = useNewShoppingListForm();
    form.show = true;
    form.name = "Groceries";

    reset();

    expect(form).toEqual({ show: false, name: "", loading: false });
  });
});
