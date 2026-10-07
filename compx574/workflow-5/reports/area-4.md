# Area 4 sub-agent final report (verbatim)

Received 2026-10-08 ~12:56 NZDT. Resumed run: 353,514 tokens, 27 tool uses, 238 s.

---

Area 4 (groups, admin, explore): 64 of the 80 Python routes are implemented. The comparisons against Python found no difference in status codes or response bodies, apart from 500 responses, which have a different body format.

**What I built**
- Routes are in `php-w5/routes/groups-admin.php`; classes are under `php-w5/app/Areas/GroupsAdmin/` (`Controllers/*`, `Support/*`).
- The contract is `compx574/workflow-5-contracts/area-4.md`. It covers every endpoint and has the "Not implemented" and "Helpers duplicated" sections. It now reflects the final code.
- Implemented: groups 22/27, admin 32/38, explore 10/15.
- 16 routes are not registered:
  - Groups: the two AI-provider test routes, data migrations, and seeders foods/units. The seeders could have been ported; I left them out for time, and the contract says so.
  - Admin: GET /admin/about (needs GitHub and the recipe_scrapers package), sending email, backup create/upload/restore, and debug/openai.
  - Explore: cookbooks (their output needs the queryFilter parser) and the three explore recipe routes. I did not copy area 2's full Recipe serializer.

**Verification (Python :9000 vs PHP :9014, same request)**
- Read and rejected-input cases: 110 run, 107 matched, 3 differ. Groups 42/43, admin 43/45, explore 22/22.
- They include signed-in success with real data, malformed and non-v4 UUIDs (422), a body of `0` (422), no token (401), and a non-admin or non-`can_manage` user (403).
- The 3 that differ are all 500s. The stored AI provider has an empty API key, which makes Python fail validation and return 500. PHP matches the status, but the body is `{"detail":"Internal Server Error"}` where Python returns plain text.
- Write cycles: a 36-step script ran against each server and the outputs (ids and timestamps masked) were identical. It covered:
  - labels: create, duplicate (409), update, search, delete twice
  - group preferences: update, then restored
  - AI providers: create, duplicate, update headers/params, read through the admin route, delete
  - admin groups: create, duplicate name, update so the group is public, then the explore routes on it
  - admin households: create, update, delete blocked by a user, delete
  - admin users: create, promote, update without `tokens` (400 in both), reset token, unlock, delete
- Every row and user directory I created was deleted. The group preferences I changed were restored.
- Not checked:
  - the three maintenance clean POSTs, because they delete files in the shared data directory
  - getting a download token for an existing backup, because there are no backups
  - `groups/storage` and the maintenance sizes beyond the current data: they matched today, but they depend on filesystem directory sizes

**Shared layer**
- The bug you fixed (401/403 from `MealieAuth` coming back as 500) is what I hit. I worked around it with my own wrapper middleware, `GroupsAdmin\Support\Auth`, which my routes still use. It is now redundant but harmless; for the merge.
- `App\Support\Pagination` was not enough for this area. It has no search, uses the wrong default order, handles `perPage=-1`/`page=-1` differently, and does not reject unknown or non-filterable `orderBy` columns with a 400. I wrote my own pager instead.
- `Illuminate\Support\Facades\DB` clashes with any class named `Db` that imports it. I renamed the import in my own class.
- 422 messages cannot match exactly, because Python puts the source file and line in the message. Status and response shape match.

**Rules**
I followed them all. I did not commit, and my server on :9014 is stopped. One thing to know: the queryFilter that Python always adds for explore households (only non-private households) is written as plain SQL, not with a filter parser. A queryFilter sent by the user is ignored.
