import { flushPromises, mount } from "@vue/test-utils";
import { beforeEach, afterEach, expect, it, vi } from "vitest";
import RecipeDialogShareFile from "./RecipeDialogShareFile.vue";

const { exportRaw, shareRecipeFile, downloadRecipeFile } = vi.hoisted(() => ({
  exportRaw: vi.fn(), shareRecipeFile: vi.fn().mockResolvedValue("shared"), downloadRecipeFile: vi.fn(),
}));
vi.mock("~/composables/api", () => ({ useUserApi: () => ({ recipes: { exportRaw } }) }));
vi.mock("~/lib/recipe/recipe-file", () => ({
  createRecipeFile: () => new File(["{}"], "soup.json", { type: "application/json" }),
  shareRecipeFile, downloadRecipeFile,
}));

function render() {
  return mount(RecipeDialogShareFile, {
    props: { modelValue: false, slug: "soup" },
    global: { stubs: {
      "BaseDialog": { template: "<div><slot /></div>" },
      "v-card-text": { template: "<div><slot /></div>" },
      "v-btn": { props: ["disabled"], template: "<button :disabled='disabled'><slot /></button>" },
      "v-progress-linear": true,
      "v-alert": { template: "<div><slot /></div>" },
    } },
  });
}

beforeEach(() => { vi.clearAllMocks(); exportRaw.mockResolvedValue({ data: { name: "Soup" }, error: null }); });
afterEach(() => { vi.unstubAllGlobals(); });

it("prepares only on opening; a second gesture shares the prepared file", async () => {
  const wrapper = render();
  expect(exportRaw).not.toHaveBeenCalled();
  await wrapper.setProps({ modelValue: true });
  await flushPromises();
  expect(exportRaw).toHaveBeenCalledExactlyOnceWith("soup");
  expect(shareRecipeFile).not.toHaveBeenCalled();
  await wrapper.findAll("button")[0]!.trigger("click");
  expect(shareRecipeFile).toHaveBeenCalledOnce();
  wrapper.unmount();
});

it("reports unavailable sharing without downloading; download remains explicit", async () => {
  shareRecipeFile.mockResolvedValueOnce("unavailable");
  const wrapper = render();
  await wrapper.setProps({ modelValue: true });
  await flushPromises();
  await wrapper.findAll("button")[0]!.trigger("click");
  await flushPromises();
  expect(wrapper.text()).toContain("File sharing is unavailable");
  expect(downloadRecipeFile).not.toHaveBeenCalled();
  await wrapper.findAll("button")[1]!.trigger("click");
  expect(downloadRecipeFile).toHaveBeenCalledOnce();
  wrapper.unmount();
});

it("does not enable sharing or download after an unauthorized export", async () => {
  exportRaw.mockResolvedValue({ data: null, error: new Error("Forbidden") });
  const wrapper = render();
  await wrapper.setProps({ modelValue: true });
  await flushPromises();
  expect(wrapper.text()).toContain("Something Went Wrong!");
  expect(wrapper.findAll("button").every(button => button.attributes("disabled") !== undefined)).toBe(true);
  expect(shareRecipeFile).not.toHaveBeenCalled();
  expect(downloadRecipeFile).not.toHaveBeenCalled();
  wrapper.unmount();
});

it("ignores a pending export after closing", async () => {
  let resolve!: (value: unknown) => void;
  exportRaw.mockImplementation(() => new Promise((r) => { resolve = r; }));
  const wrapper = render();
  await wrapper.setProps({ modelValue: true });
  await wrapper.setProps({ modelValue: false });
  resolve({ data: { name: "Soup" }, error: null });
  await flushPromises();
  expect(wrapper.findAll("button").every(button => button.attributes("disabled") !== undefined)).toBe(true);
  wrapper.unmount();
});
