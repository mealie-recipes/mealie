import { mount } from "@vue/test-utils";
import { ref } from "vue";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import RegistrationPage from "./index.vue";
import { i18n } from "~/tests/setup";

const mocks = vi.hoisted(() => ({
  register: vi.fn(),
  error: vi.fn(),
  success: vi.fn(),
  push: vi.fn(),
  resetAccount: vi.fn(),
  resetCredentials: vi.fn(),
}));

vi.mock("~/composables/api", () => ({
  useUserApi: () => ({ register: { register: mocks.register } }),
}));
vi.mock("~/composables/api/api-client", () => ({
  usePublicApi: () => ({ validators: { group: vi.fn() } }),
}));
vi.mock("~/composables/use-toast", () => ({
  alert: { error: mocks.error, success: mocks.success },
}));
vi.mock("~/composables/use-router", () => ({ useRouteQuery: () => ref("invalid-token") }));
vi.mock("~/composables/use-locales", () => ({ useLocales: () => ({ locale: ref("en-US") }) }));
vi.mock("~/composables/use-validators", () => ({
  validators: {},
  useAsyncValidator: () => ({ validate: vi.fn(), valid: ref(true) }),
}));
vi.mock("~/components/Domain/User/UserRegistrationForm.vue", () => ({ default: { render: () => null } }));
vi.mock("~/composables/use-users/user-registration-form", () => ({
  useUserRegistrationForm: () => ({
    accountDetails: {
      email: ref("user@example.com"),
      username: ref("user"),
      fullName: ref("Test User"),
      advancedOptions: ref(false),
      reset: mocks.resetAccount,
    },
    credentials: {
      password1: ref("password"),
      password2: ref("password"),
      reset: mocks.resetCredentials,
    },
  }),
}));

describe("registration result handling", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.stubGlobal("definePageMeta", vi.fn());
    vi.stubGlobal("useRouter", () => ({ push: mocks.push }));
  });

  afterEach(() => vi.unstubAllGlobals());

  async function submit() {
    // Exercise the page's submission logic without rendering the multi-step form.
    const wrapper = mount({ ...RegistrationPage, render: () => null });
    try {
      await (wrapper.vm as unknown as { submitRegistration: () => Promise<void> }).submitRegistration();
    }
    finally {
      wrapper.unmount();
    }
  }

  test("does not add a generic error when the interceptor handles detail.message", async () => {
    mocks.register.mockResolvedValue({
      response: null,
      error: { response: { data: { detail: { message: "Invalid group token" } } } },
    });
    await submit();
    expect(mocks.error).not.toHaveBeenCalled();
    expect(mocks.push).not.toHaveBeenCalled();
    expect(mocks.resetAccount).not.toHaveBeenCalled();
  });

  test.each([
    null,
    { response: { data: { detail: "Invalid group token" } } },
    { response: { data: { detail: { message: "" } } } },
    { response: { data: { detail: [{ msg: "Field required" }] } } },
  ])("keeps the fallback for errors not shown by the interceptor: %j", async (error) => {
    mocks.register.mockResolvedValue({ response: null, error });
    await submit();
    expect(mocks.error).toHaveBeenCalledExactlyOnceWith(i18n.global.t("events.something-went-wrong"));
    expect(mocks.push).not.toHaveBeenCalled();
  });

  test("resets the form and redirects after successful registration", async () => {
    mocks.register.mockResolvedValue({ response: { status: 201 }, error: null });
    await submit();
    expect(mocks.resetAccount).toHaveBeenCalledOnce();
    expect(mocks.resetCredentials).toHaveBeenCalledOnce();
    expect(mocks.success).toHaveBeenCalledOnce();
    expect(mocks.push).toHaveBeenCalledExactlyOnceWith("/login");
    expect(mocks.error).not.toHaveBeenCalled();
  });
});
