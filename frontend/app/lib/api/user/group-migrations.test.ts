import { expect, test, vi } from "vitest";
import { GroupMigrationApi } from "./group-migrations";

test.each([true, false])("sends the chosen skip-duplicates option (%s)", async (skipDuplicates) => {
  const post = vi.fn().mockResolvedValue({ data: {} });
  const api = new GroupMigrationApi({ post } as never);
  await api.startMigration({
    addMigrationTag: false,
    skipDuplicates,
    migrationType: "copymethat",
    archive: new File(["archive"], "recipes.zip"),
  });
  const [url, form] = post.mock.calls[0];
  expect(url).toBe("/api/groups/migrations");
  expect(form.get("skip_duplicates")).toBe(String(skipDuplicates));
  expect(form.get("migration_type")).toBe("copymethat");
});
