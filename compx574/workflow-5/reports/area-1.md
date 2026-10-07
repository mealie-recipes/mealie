# Area 1 sub-agent final report (verbatim)

Received 2026-10-08 12:50 NZDT. Resumed run: 273,470 tokens, 9 tool uses, 89 s.

---

Area 1 (auth, users, app, validators) is finished. 26 of the 32 Python routes are implemented. Against Python :9000, the last full run of 69 request pairs all matched on status and JSON body, and the write flow matched on both servers except one timing-dependent case. The server on :9011 is stopped and nothing was committed.

**Implemented (26):**
- Auth: token (password login), refresh, logout.
- Users: register, self, self/ratings, self/ratings/{recipe_id}, self/favorites, PUT password, PUT {item_id}, reset-password, api-tokens create and delete, and {id} ratings, favorites, set rating, add favourite, remove favourite.
- App: about, startup-info, theme.
- Validators: user/name, user/email, group, household, recipe.

**Not registered (6):** the 4 OIDC routes, `forgot-password` (sends email) and `POST /users/{id}/image` (needs Pillow WebP conversion).

**Partly implemented:**
- Register: creating a new group returns 501. Python only reaches that path when ALLOW_SIGNUP=true, which is off. Seeding and the signup notification are also missing.
- Login: no LDAP.
- Password change and user update: no IS_DEMO guard.
- `/validators/household`: Python always returns 500 there (its repo is built without a group, so `get_by_name` raises). PHP returns the same 500 after checking the query. That route only returns an error, so the rule against fixed-error stubs may apply to it.

**Verification:**
- Read-only and rejection cases: 69 matched, 0 differ on the new shared DB. They cover success with data, 404 and not-found, 422 for malformed and nil UUIDs, body `0`, wrong types, unauthenticated, and 403 permission cases.
- Write flow, run on both servers with test users I created and then deleted: register, login (bcrypt works both ways), API token create/use/delete, a 403 on another user's token, self update, ratings and favourites (including recomputing `recipes.rating`), password change, and reset-password. Results were identical except one timing case: whether the old session token stops working right after a password change depends on whether it was issued in the same second.
- Remaining differences: the `json_invalid` 422 message text, and `Set-Cookie` header formatting.
- 422 messages are rebuilt in Python's exact dev-mode format, including the file and line suffix. The old-DB test rows went with the DB swap. I deleted their two profile folders under `dev/data/users/`.

**Shared-layer problems:**
- **Affects every area:** in `bootstrap/app.php`, the catch-all `Throwable` renderer turns `HttpResponseException` thrown from middleware into a 500. So `mealie:user` and `mealie:admin` give 500 instead of 401 when there is no valid token. I worked around it with my own wrapper middleware, `RequireUser`.
- `MealieAuth` returns "Could not validate credentials" for an unknown API token, where Python returns 401 "Unauthorized".
- `Errors::validation` and `Guid::requireUuid4` cannot produce Python's 422 text. I wrote my own helpers: `Pyd`, `Uuid`, `Settings`, `Translator`, `Users`.

**Rules:**
- I read the whole split document, including the other areas' file tables, though not their contracts or code.
- At runtime PHP reads `mealie/lang/messages/*.json` (for translated messages) and copies `mealie/assets/users/random_*.webp` (the random profile image on register). It does not change any Python files.
- For the reset-password check I inserted `password_reset_tokens` rows for my own test users and removed them afterwards.

Files: `php-w5/routes/auth-users.php`, `php-w5/app/Areas/AuthUsers/`, `compx574/workflow-5-contracts/area-1.md`.
