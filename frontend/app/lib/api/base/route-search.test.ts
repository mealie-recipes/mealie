import { describe, expect, test } from "vitest";
import { route } from "./route";

describe("search query URLs", () => {
  test("round trips signed terms and quoted exclusions", () => {
    const search = "+pork lettuce wrap -\"chili peppers\"";
    const url = new URL(route("/api/recipes", { search, searchMode: "any" }), "http://localhost");
    expect(url.searchParams.get("search")).toBe(search);
    expect(url.searchParams.get("searchMode")).toBe("any");
    expect(url.search).toContain("%2Bpork");
  });
});
