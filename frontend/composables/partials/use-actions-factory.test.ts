import { describe, expect, test, vi } from "vitest";
import { ref } from "vue";
import { useStoreActions } from "./use-actions-factory";
import type { BaseCRUDAPI } from "~/lib/api/base/base-clients";

describe("useStoreActions", () => {
  const mockApi = {
    getAll: vi.fn(),
    createOne: vi.fn(),
    updateOne: vi.fn(),
    deleteOne: vi.fn(),
  } as unknown as BaseCRUDAPI<unknown, unknown, unknown>;

  const mockStore = ref([]);
  const mockLoading = ref(false);

  test("deleteMany calls deleteOne for each ID and refreshes once", async () => {
    const actions = useStoreActions("test-store", mockApi, mockStore, mockLoading);

    mockApi.deleteOne = vi.fn().mockResolvedValue({ response: { data: {} } });
    mockApi.getAll = vi.fn().mockResolvedValue({ data: { items: [] } });

    const ids = ["1", "2", "3"];
    await actions.deleteMany(ids);

    expect(mockApi.deleteOne).toHaveBeenCalledTimes(3);
    expect(mockApi.deleteOne).toHaveBeenCalledWith("1");
    expect(mockApi.deleteOne).toHaveBeenCalledWith("2");
    expect(mockApi.deleteOne).toHaveBeenCalledWith("3");

    expect(mockApi.getAll).toHaveBeenCalledTimes(1);
  });

  test("deleteMany handles empty array", async () => {
    const actions = useStoreActions("test-store", mockApi, mockStore, mockLoading);

    mockApi.deleteOne = vi.fn();
    mockApi.getAll = vi.fn().mockResolvedValue({ data: { items: [] } });

    await actions.deleteMany([]);

    expect(mockApi.deleteOne).not.toHaveBeenCalled();
    expect(mockApi.getAll).toHaveBeenCalledTimes(1);
  });

  test("deleteMany sets loading state", async () => {
    const actions = useStoreActions("test-store", mockApi, mockStore, mockLoading);

    mockApi.deleteOne = vi.fn().mockResolvedValue({});
    mockApi.getAll = vi.fn().mockResolvedValue({ data: { items: [] } });

    const promise = actions.deleteMany(["1"]);
    expect(mockLoading.value).toBe(true);

    await promise;
    expect(mockLoading.value).toBe(false);
  });
});
