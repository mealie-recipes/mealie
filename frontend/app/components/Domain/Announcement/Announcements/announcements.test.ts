import { describe, test, expect } from "vitest";

const announcementFiles = import.meta.glob<{ default: unknown }>(
  "~/components/Domain/Announcement/Announcements/*.vue",
);

// Expected format: YYYY-MM-DD_N_slug  e.g. 2026-03-27_1_welcome
const FILE_FORMAT = /^\d{4}-\d{2}-\d{2}_\d+_.+$/;

describe("Announcement files", () => {
  const filenames = Object.keys(announcementFiles).map(path =>
    path.split("/").at(-1)!.replace(".vue", ""),
  );

  test("directory is not empty", () => {
    expect(filenames.length).toBeGreaterThan(0);
  });

  test("all filenames match YYYY-MM-DD_N_slug format", () => {
    for (const name of filenames) {
      expect(name, `"${name}" does not match the expected format`).toMatch(FILE_FORMAT);
    }
  });

  test("all date prefixes are valid dates", () => {
    for (const name of filenames) {
      const datePart = name.split("_", 1)[0]!;
      const date = new Date(datePart);
      expect(isNaN(date.getTime()), `"${name}" has an invalid date prefix "${datePart}"`).toBe(false);
    }
  });

  test("all filenames are unique", () => {
    const unique = new Set(filenames);
    expect(unique.size).toBe(filenames.length);
  });
});
