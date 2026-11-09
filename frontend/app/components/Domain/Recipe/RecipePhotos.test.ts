import { flushPromises, shallowMount } from "@vue/test-utils";
import { beforeEach, describe, expect, test, vi } from "vitest";
import { ref } from "vue";
import RecipePhotos from "./RecipePhotos.vue";
import { makeRecipe } from "~/tests/factories";
import type { RecipeAsset } from "~/lib/api/types/recipe";

const mocks = vi.hoisted(() => ({
  createAsset: vi.fn(),
  getOne: vi.fn(),
  patchOne: vi.fn(),
  updateImage: vi.fn(),
  error: vi.fn(),
}));

vi.mock("~/composables/api", () => ({
  useUserApi: () => ({ recipes: mocks }),
  useStaticRoutes: () => ({ recipeAssetPath: (id: string, name: string) => `/api/media/${id}/${name}` }),
}));
vi.mock("~/composables/recipe-page/shared-state", () => ({
  usePageState: () => ({ imageKey: ref(1) }),
}));
vi.mock("~/composables/use-toast", () => ({ alert: { error: mocks.error } }));

const photo: RecipeAsset = { name: "Dish", fileName: "dish.jpg", icon: "mdi-file-image" };
const card: RecipeAsset = { name: "Card", fileName: "card.png", icon: "mdi-file-image" };
const document: RecipeAsset = { name: "Notes", fileName: "notes.pdf", icon: "mdi-file-pdf-box" };
const pass = { template: "<div><slot /></div>" };

function mountPhotos(canEdit = true, assets = [photo, card, document]) {
  const recipe = makeRecipe({ assets, settings: { showAssets: false } });
  const wrapper = shallowMount(RecipePhotos, {
    props: { modelValue: recipe, canEdit },
    global: {
      mocks: { $globals: { icons: {} } },
      stubs: {
        VSpacer: true,
        VIcon: true,
        VImg: true,
        VCardText: true,
        VCard: pass,
        VList: pass,
        VMenu: { template: "<div><slot name='activator' :props='{}' /><slot /></div>" },
        VBtn: { template: "<button><slot /></button>" },
        VListItem: { props: ["title"], template: "<button>{{ title }}</button>" },
        RecipeImageLightbox: {
          name: "RecipeImageLightbox",
          props: ["imageUrl", "modelValue", "navigation"],
          emits: ["next", "previous", "update:modelValue"],
          template: "<div />",
        },
        BaseDialog: { name: "BaseDialog", props: ["modelValue"], emits: ["delete"], template: "<div />" },
      },
    },
  });
  return { wrapper, recipe };
}

async function selectFiles(wrapper: ReturnType<typeof mountPhotos>["wrapper"], files: File[]) {
  const input = wrapper.get("input");
  Object.defineProperty(input.element, "files", { value: files, configurable: true });
  await input.trigger("change");
  await flushPromises();
}

beforeEach(() => {
  vi.resetAllMocks();
});

describe("RecipePhotos", () => {
  test("shows existing image assets even when Show Assets is off, and cycles through them", async () => {
    const { wrapper } = mountPhotos();
    expect(wrapper.findAll(".photo-preview")).toHaveLength(2);
    await wrapper.get(".photo-preview").trigger("click");
    const lightbox = wrapper.findComponent({ name: "RecipeImageLightbox" });
    expect(lightbox.props("imageUrl")).toContain("dish.jpg");
    await lightbox.vm.$emit("previous");
    expect(lightbox.props("imageUrl")).toContain("card.png");
    await lightbox.vm.$emit("next");
    expect(lightbox.props("imageUrl")).toContain("dish.jpg");
    wrapper.unmount();
  });

  test("uploads multiple photos, preserves successful uploads after a failure, and clears the file input", async () => {
    mocks.createAsset.mockResolvedValueOnce({ error: {} }).mockResolvedValueOnce({ data: card });
    const { wrapper, recipe } = mountPhotos(true, [photo, document]);
    await selectFiles(wrapper, [new File(["a"], "bad.jpg"), new File(["b"], "card.PNG")]);
    expect(mocks.createAsset).toHaveBeenCalledTimes(2);
    expect(mocks.createAsset).toHaveBeenNthCalledWith(2, recipe.slug, expect.objectContaining({ name: "card", extension: "png" }));
    expect(recipe.assets).toEqual([photo, document, card]);
    expect(mocks.error).toHaveBeenCalledOnce();
    expect(wrapper.emitted("saved")).toHaveLength(1);
    expect((wrapper.get("input").element as HTMLInputElement).value).toBe("");
    expect(wrapper.emitted("busy")).toEqual([[true], [false]]);
    wrapper.unmount();
  });

  test("rejects non-image files and accepts photos through drag and drop", async () => {
    mocks.createAsset.mockResolvedValue({ data: card });
    const { wrapper } = mountPhotos();
    await wrapper.get("section").trigger("drop", {
      dataTransfer: { files: [new File(["a"], "notes.pdf"), new File(["b"], "card.png")] },
    });
    await flushPromises();
    expect(mocks.createAsset).toHaveBeenCalledOnce();
    expect(mocks.error).toHaveBeenCalledOnce();
    wrapper.unmount();
  });

  test("allows readers to view photos but hides mutation controls and ignores drops", async () => {
    const { wrapper } = mountPhotos(false);
    expect(wrapper.find("input").exists()).toBe(false);
    expect(wrapper.text()).not.toContain("Set as cover");
    expect(wrapper.text()).not.toContain("Delete");
    await wrapper.get("section").trigger("drop", { dataTransfer: { files: [new File(["a"], "new.jpg")] } });
    expect(mocks.createAsset).not.toHaveBeenCalled();
    await wrapper.get(".photo-preview").trigger("click");
    expect(wrapper.findComponent({ name: "RecipeImageLightbox" }).props("modelValue")).toBe(true);
    wrapper.unmount();
  });

  test("removes only the selected photo and preserves current server assets", async () => {
    mocks.getOne.mockResolvedValue({ data: makeRecipe({ assets: [photo, card, document] }) });
    mocks.patchOne.mockResolvedValue({ data: makeRecipe({ assets: [card, document] }) });
    const { wrapper, recipe } = mountPhotos(true, [photo]);
    const remove = wrapper.findAll("button").find(button => button.text() === "Delete")!;
    await remove.trigger("click");
    expect(mocks.patchOne).not.toHaveBeenCalled();
    await wrapper.findComponent({ name: "BaseDialog" }).vm.$emit("delete");
    await flushPromises();
    expect(mocks.patchOne).toHaveBeenCalledExactlyOnceWith(recipe.slug, { assets: [card, document] });
    expect(recipe.assets).toEqual([card, document]);
    wrapper.unmount();
  });

  test("keeps the photo after a failed delete", async () => {
    mocks.getOne.mockResolvedValue({ error: {} });
    const { wrapper, recipe } = mountPhotos(true, [photo]);
    await wrapper.findAll("button").find(button => button.text() === "Delete")!.trigger("click");
    await wrapper.findComponent({ name: "BaseDialog" }).vm.$emit("delete");
    await flushPromises();
    expect(recipe.assets).toEqual([photo]);
    expect(mocks.error).toHaveBeenCalledOnce();
    wrapper.unmount();
  });

  test("sets a photo as the cover without removing the attachment", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, blob: () => Promise.resolve(new Blob(["photo"])) }));
    mocks.updateImage.mockResolvedValue({ data: { image: "new-version" } });
    const { wrapper, recipe } = mountPhotos(true, [photo]);
    await wrapper.findAll("button").find(button => button.text() === "Set as cover")!.trigger("click");
    await flushPromises();
    expect(mocks.updateImage).toHaveBeenCalledWith(recipe.slug, expect.objectContaining({ name: "dish.jpg" }));
    expect(recipe.image).toBe("new-version");
    expect(recipe.assets).toEqual([photo]);
    wrapper.unmount();
    vi.unstubAllGlobals();
  });
});
