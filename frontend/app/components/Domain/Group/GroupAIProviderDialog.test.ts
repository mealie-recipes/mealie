import { flushPromises, mount, type VueWrapper } from "@vue/test-utils";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { nextTick } from "vue";
import GroupAIProviderDialog from "./GroupAIProviderDialog.vue";
import type { AIProviderOut } from "~/lib/api/types/group";

const wrappers: VueWrapper[] = [];

const mocks = vi.hoisted(() => ({
  getOne: vi.fn(),
}));

vi.mock("~/composables/use-ai-providers", () => ({
  useAIProviders: () => ({
    loading: ref(false),
    getOne: mocks.getOne,
    testOne: vi.fn(),
    testSavedOne: vi.fn(),
  }),
}));

function provider(overrides: Partial<AIProviderOut>): AIProviderOut {
  return {
    id: "id",
    name: "name",
    model: "model",
    baseUrl: null,
    timeout: 300,
    requestHeaders: {},
    requestParams: {},
    ...overrides,
  } as AIProviderOut;
}

function mountDialog(providerId?: string) {
  const wrapper = mount(GroupAIProviderDialog, {
    props: {
      modelValue: true,
      providerId,
    },
    global: {
      mocks: {
        $globals: { icons: { robot: "robot", save: "save", createAlt: "createAlt" } },
      },
      stubs: {
        BaseDialog: {
          template: "<div><slot /><slot name=\"custom-card-action\" /></div>",
        },
        AppLoader: { template: "<div />" },
        BaseKeyValueEditor: { template: "<div />" },
        VForm: { template: "<form><slot /></form>" },
        VTextField: {
          props: ["modelValue"],
          template: "<input :value=\"modelValue\" @input=\"$emit('update:modelValue', $event.target.value)\">",
        },
        VNumberInput: { template: "<div />" },
        VExpansionPanels: { template: "<div><slot /></div>" },
        VExpansionPanel: { template: "<div><slot /></div>" },
        VExpansionPanelTitle: { template: "<div><slot /></div>" },
        VExpansionPanelText: { template: "<div><slot /></div>" },
        VAlert: { template: "<div><slot /></div>" },
        VDivider: { template: "<div />" },
        VBtn: { template: "<button type=\"button\"><slot /></button>" },
      },
    },
  });

  wrappers.push(wrapper);
  return wrapper;
}

describe("groupAIProviderDialog", () => {
  beforeEach(() => {
    mocks.getOne.mockReset();
    vi.stubGlobal("useNuxtApp", () => ({ $globals: { icons: {} } }));
  });

  afterEach(() => {
    wrappers.forEach(wrapper => wrapper.unmount());
    wrappers.length = 0;
    vi.unstubAllGlobals();
  });

  test("a stale fetch for a previously-selected provider does not clobber the form after switching providers", async () => {
    let resolveA: (value: unknown) => void;
    let resolveB: (value: unknown) => void;
    const pendingA = new Promise((resolve) => { resolveA = resolve; });
    const pendingB = new Promise((resolve) => { resolveB = resolve; });

    mocks.getOne.mockImplementation((id: string) => {
      if (id === "provider-a") return pendingA;
      if (id === "provider-b") return pendingB;
      throw new Error(`unexpected provider id: ${id}`);
    });

    const wrapper = mountDialog("provider-a");
    await nextTick();

    // Switch to provider B before A's fetch has resolved (e.g. the user closed A's
    // edit dialog and opened B's before the network responded).
    await wrapper.setProps({ providerId: "provider-b" });
    await nextTick();

    // B's fetch resolves first...
    resolveB!({ data: provider({ id: "provider-b", name: "Provider B", model: "model-b" }) });
    await flushPromises();

    const nameInput = () => wrapper.findAll("input")[0];
    expect(nameInput().element.value).toBe("Provider B");

    // ...and A's now-stale fetch resolves afterward. It must be ignored rather than
    // overwriting the form with provider A's data while provider B is being edited.
    resolveA!({ data: provider({ id: "provider-a", name: "Provider A", model: "model-a" }) });
    await flushPromises();

    expect(nameInput().element.value).toBe("Provider B");
  });
});
