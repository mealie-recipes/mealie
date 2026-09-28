import { flushPromises, mount } from "@vue/test-utils";
import { afterEach, expect, test, vi } from "vitest";
import { createVuetify } from "vuetify";
import { VBtn, VCardText, VContainer, VDataTable, VIcon } from "vuetify/components";
import ReportPage from "./[id].vue";
import { i18n } from "~/tests/setup";
import type { ReportOut } from "~/lib/api/types/reports";

const { getOne } = vi.hoisted(() => ({ getOne: vi.fn() }));

vi.mock("~/composables/api", () => ({
  useUserApi: () => ({ groupReports: { getOne } }),
}));

afterEach(() => vi.unstubAllGlobals());

test("report entries expand to show their exception and collapse again", async () => {
  vi.stubGlobal("definePageMeta", vi.fn());
  vi.stubGlobal("useRoute", () => ({ params: { id: "report-1" } }));
  vi.stubGlobal("ResizeObserver", class {
    observe() {}
    unobserve() {}
    disconnect() {}
  });
  i18n.global.setDateTimeFormat("en-US", { short: { year: "numeric", month: "short", day: "numeric" } });
  const report: ReportOut = {
    id: "report-1",
    groupId: "group-1",
    name: "Migration report",
    category: "migration",
    entries: [
      { id: "failed", reportId: "report-1", message: "Failed recipe", success: false, exception: "Invalid recipe data" },
      { id: "success", reportId: "report-1", message: "Imported recipe", success: true, exception: "" },
      { id: "no-details", reportId: "report-1", message: "No details", success: false },
    ].map(entry => ({ ...entry, timestamp: "2026-09-25T12:00:00Z" })),
  };
  getOne.mockResolvedValue({ data: report });
  const wrapper = mount(ReportPage, {
    global: {
      plugins: [createVuetify({ components: { VBtn, VCardText, VContainer, VDataTable, VIcon } })],
      stubs: { BasePageTitle: true, BaseCardSectionTitle: true, VImg: true },
      mocks: {
        $globals: { icons: { checkboxMarkedCircle: "success", close: "error" } },
      },
    },
  });

  try {
    await flushPromises();
    expect(getOne).toHaveBeenCalledWith("report-1");
    const rows = wrapper.findAll("tbody > tr");
    expect(rows).toHaveLength(3);
    expect(wrapper.text()).not.toContain("Invalid recipe data");

    await rows[0].get("button").trigger("click");
    const details = wrapper.findAll("tbody > tr")[1];
    expect(details.text()).toBe("Invalid recipe data");
    expect(details.get("td").attributes("colspan")).toBe("4");

    await rows[0].get("button").trigger("click");
    expect(wrapper.text()).not.toContain("Invalid recipe data");
    expect(wrapper.findAll("tbody > tr")).toHaveLength(3);
    expect(rows[1].find("button").exists()).toBe(false);
    expect(rows[2].find("button").exists()).toBe(false);
  }
  finally {
    wrapper.unmount();
  }
});
