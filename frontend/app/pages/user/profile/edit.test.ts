import { flushPromises, mount } from "@vue/test-utils";
import { ref } from "vue";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { createI18n } from "vue-i18n";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import messages from "@/lang/messages/en-US.json";
import ProfileEditPage from "./edit.vue";

const mocks = vi.hoisted(() => ({
  updateOne: vi.fn(),
  getSession: vi.fn(),
}));

vi.mock("~/composables/api", () => ({
  useUserApi: () => ({ users: { updateOne: mocks.updateOne, changePassword: vi.fn() } }),
}));
vi.mock("~/composables/use-users/preferences", () => ({
  useUserActivityPreferences: () => ref({ defaultActivity: "recipes" }),
}));
vi.mock("~/composables/use-default-activity", () => ({
  default: () => ({
    getDefaultActivityLabels: () => [],
    getActivityLabel: () => "",
    getActivityKey: () => undefined,
  }),
}));
vi.mock("~/components/Domain/User/UserAvatar.vue", () => ({ default: { render: () => null } }));
vi.mock("~/components/Domain/User/UserPasswordStrength.vue", () => ({ default: { render: () => null } }));

function mockUser(email: string) {
  return {
    id: "a5f4e3d2-0000-4000-8000-000000000001",
    username: "user",
    fullName: "Test User",
    email,
    authMethod: "Mealie",
    admin: false,
    group: "home",
    household: "family",
  };
}

describe("profile email validation", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mocks.updateOne.mockResolvedValue({ response: { status: 200 } });
    vi.stubGlobal("definePageMeta", vi.fn());
    vi.stubGlobal("useSeoMeta", vi.fn());
  });

  afterEach(() => vi.unstubAllGlobals());

  async function submitWithEmail(email: string) {
    vi.stubGlobal("useMealieAuth", () => ({ user: ref(mockUser(email)), getSession: mocks.getSession }));
    const wrapper = mount(ProfileEditPage, {
      global: {
        plugins: [
          createVuetify({ components }),
          createI18n({ legacy: false, locale: "en-US", messages: { "en-US": messages } }),
        ],
        stubs: {
          BasePageTitle: true,
          BaseCardSectionTitle: true,
          BaseButton: true,
          AppButtonUpload: true,
          ToggleState: {
            setup: (_: unknown, { slots }: { slots: { default?: (p: object) => unknown } }) =>
              () => slots.default?.({ modelValue: false }),
          },
        },
        mocks: { $appInfo: { allowPasswordLogin: true }, $globals: { icons: {} } },
      },
    });
    try {
      await (wrapper.vm as unknown as { updateUser: () => Promise<void> }).updateUser();
      await flushPromises();
      return wrapper.text();
    }
    finally {
      wrapper.unmount();
    }
  }

  test("does not save a malformed email address", async () => {
    const text = await submitWithEmail("not-an-email");
    expect(mocks.updateOne).not.toHaveBeenCalled();
    expect(text).toContain("Email Must Be Valid");
  });

  test("saves a valid email address", async () => {
    await submitWithEmail("user@example.com");
    expect(mocks.updateOne).toHaveBeenCalledWith(
      "a5f4e3d2-0000-4000-8000-000000000001",
      expect.objectContaining({ email: "user@example.com" }),
    );
  });
});
