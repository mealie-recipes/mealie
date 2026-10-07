# Area 1 contract — auth, users, app, validators

PHP: `php-w5/routes/auth-users.php`, classes in `php-w5/app/Areas/AuthUsers/` (namespace `App\Areas\AuthUsers`). Dev port 9011.

Conventions used by every endpoint below:

- Ids: `users.id`, `groups.id`, `households.id`, `recipes.id`, `users_to_recipes.id` are CHAR(32) hex in SQLite and returned dashed (`Guid::fromDb`). `long_live_tokens.id`, `password_reset_tokens.id`, `invite_tokens.id` are INTEGER and returned as JSON numbers.
- JSON keys follow the Pydantic alias (`MealieModel` → camelCase); plain `BaseModel` schemas (`UserRatings`, `ValidationResponse`, `ErrorResponse`, `SuccessResponse`, `MealieAuthToken`) keep snake_case.
- Dates: `Dates::out` (`…Z`).
- Validation errors: dev-mode 422 body `{"status_code":422,"message":…,"data":null}`. The message is rebuilt in Python's format (`N validation error(s): {…}  File "<worktree>/mealie/routes/…", line L, in func   METHOD /api/path`) for the error types these endpoints can produce (missing, model_attributes_type, string_type, bool_type/bool_parsing, float_type/float_parsing, int_parsing, uuid_parsing, uuid_version, string_too_short, enum, value_error).
- "user" = `mealie:user` middleware (`get_current_user`, mealie/core/dependencies/dependencies.py:102); routers built with `UserAPIRouter` (mealie/routes/_base/routers.py) add it to every route. "public" = no auth.
- Translations (`self.t`, `get_locale_provider`, mealie/lang/providers.py:44): read from `mealie/lang/messages/<Accept-Language>.json`, whole-file fallback to `en-US.json`, key returned when missing.

## auth (`mealie/routes/auth/auth.py`, prefix `/api/auth`)

| Method + path | Python | Schema | Who | Notes / not implemented |
|---|---|---|---|---|
| POST /api/auth/token | auth.py:get_token (line 134) | form `CredentialsRequestForm` (mealie/schema/user/auth.py); response `MealieAuthToken` (auth.py:119) `access_token`,`token_type`,`expires_in` | public | Credentials provider only (mealie/core/security/providers/credentials_provider.py). Username then email, case-insensitive. 401 `{"detail":"Unauthorized"}`, 423 `User is locked out`, login_attemps/locked_at bookkeeping, `Set-Cookie mealie.access_token`. JWT claims `sub, rme, iss, iat, exp`, TOKEN_TIME hours. **Not:** LDAP provider (LDAP_AUTH_ENABLED), X-Forwarded-For logging. |
| POST /api/auth/refresh | auth.py:refresh_token (line 301) | `MealieAuthToken` | user (UserAPIRouter → get_current_user) | 400 `API tokens cannot be exchanged for a session token` when `long_token` claim; carries `rme`. |
| POST /api/auth/logout | auth.py:logout (line 332) | `{"message": t("notifications.logged-out")}` | user | Clears cookie (Max-Age=0). |

## users (`mealie/routes/users/*`, prefix `/api/users`)

Registration order follows `mealie/routes/users/__init__.py`: registration, crud, forgot_password, images, api_tokens, ratings. Static paths (`/self…`, `/password`, `/api-tokens`, `/register`, `/reset-password`) are registered before `{id}` paths.

| Method + path | Python | Schema | Ids | Who / permission | Notes |
|---|---|---|---|---|---|
| POST /api/users/register | registration.py:RegistrationController.register_new_user (line 20); mealie/services/user_services/registration_service.py | body `CreateUserRegistration` (mealie/schema/user/registration.py); 201 `UserOut` | user id new CHAR(32) | public. 403 `User Registration is Disabled` when `not ALLOW_SIGNUP and groupToken is None or groupToken == ""` (registration.py:24) | 409 username/email conflict, 400 invalid group token, invite-token use count. **Not:** creating a new group (only reachable when ALLOW_SIGNUP=true; returns 501 in PHP), seeding foods/units, event-bus `user_signup` notification. |
| GET /api/users/self | crud.py:get_logged_in_user (line 19) | `UserOut` (mealie/schema/user/user.py:170) incl. `tokens` (`LongLiveTokenOut`) | dashed | user | |
| GET /api/users/self/ratings | crud.py:get_logged_in_user_ratings (line 23) | `UserRatings[UserRatingSummary]` | dashed | user | Rows of `users_to_recipes` for caller, table order (repository_users.py:82). |
| GET /api/users/self/ratings/{recipe_id} | crud.py:get_logged_in_user_rating_for_recipe (line 27) | `UserRatingSummary` | path UUID4 → 422 | user | 404 ErrorResponse `User has not rated this recipe`. |
| GET /api/users/self/favorites | crud.py:get_logged_in_user_favorites (line 38) | `UserRatings[UserRatingSummary]` | | user | is_favorite only. |
| PUT /api/users/password | crud.py:update_password (line 42) | body `ChangePassword`; `SuccessResponse` | | user | LDAP 400, wrong current 400 (ErrorResponse, translated), bcrypt `$2b$` cost 12, sets `tokens_valid_after` (users.py:208). **Not:** IS_DEMO default-user guard. |
| PUT /api/users/{item_id} | crud.py:update_user (line 65) | body `UserBase`; `SuccessResponse` | path UUID4 | user + `assert_user_change_allowed` (mealie/routes/users/_helpers.py:36): non-admin may only edit self without changing permissions/group/household; admin only self without changing permissions | Mirrors `User.update` (users.py:183): username/fullName/email/authMethod/advanced/showAnnouncements/lastReadAnnouncement, group+household by name, permissions via `_set_permissions`. Missing group → 400 `Failed to update user`. **Not:** IS_DEMO guard. |
| POST /api/users/reset-password | forgot_password.py:reset_password (line 24); password_reset_service.py:51 | body `ResetPassword` (mealie/schema/user/user_passwords.py) | token string | public | 400 `Invalid token`; on success updates password, `tokens_valid_after`, deletes token, returns `null`. |
| POST /api/users/api-tokens | api_tokens.py:create_api_token (line 21) | body `LongLiveTokenIn`; 201 `LongLiveTokenCreateResponse` | INTEGER id | user | JWT `long_token, id, name, integration_id, iss, iat, exp` (+1825 days). |
| DELETE /api/users/api-tokens/{token_id} | api_tokens.py:delete_api_token (line 49) | `DeleteTokenResponse` `{tokenDelete}` | path int | user; token looked up in caller's group (group repo, repository_factory.py:257) → 404 string detail; owner check `token.user_id == self.user.id` (api_tokens.py:59) → 403 | |
| GET /api/users/{id}/ratings | ratings.py:get_ratings (line 44) | `UserRatings[UserRatingOut]` | path UUID4 | user + `assert_user_change_allowed(id, user, user)` (ratings.py:47) → only self | |
| GET /api/users/{id}/favorites | ratings.py:get_favorites (line 50) | `UserRatings[UserRatingOut]` | path UUID4 | same | |
| POST /api/users/{id}/ratings/{slug} | ratings.py:set_rating (line 56) | body `UserRatingUpdate`; returns `null` | path UUID4; slug = recipe slug or UUID in caller's group | same; recipe 404 ErrorResponse `Not found.` | Creates/updates `users_to_recipes`, then recomputes `recipes.rating` = AVG(rating>0) (user_to_recipe.py:36, recipe.py:288). |
| POST /api/users/{id}/favorites/{slug} | ratings.py:add_favorite (line 80) | `null` | same | same | `set_rating(isFavorite=true)` |
| DELETE /api/users/{id}/favorites/{slug} | ratings.py:remove_favorite (line 85) | `null` | same | same | `set_rating(isFavorite=false)` (creates a row if none, as Python does) |

## app (`mealie/routes/app/app_about.py`, prefix `/api/app/about`)

| Method + path | Python | Schema | Who | Notes |
|---|---|---|---|---|
| GET /api/app/about | app_about.py:get_app_info | `AppInfo` (mealie/schema/admin/about.py) | public | Settings from env with Python defaults (ALLOW_SIGNUP, ALLOW_PASSWORD_LOGIN, IS_DEMO, TOKEN_TIME, DEFAULT_GROUP/HOUSEHOLD, OIDC_*, ALLOWED_IFRAME_HOSTS); `version` = "develop" (mealie/__init__.py). Default group/household slug only when not private. |
| GET /api/app/about/startup-info | app_about.py:get_startup_info | `AppStartupInfo` | public | `isFirstLogin` = a user with `changeme@example.com` exists. |
| GET /api/app/about/theme | app_about.py:get_app_theme | `AppTheme` | public | `THEME_*` env, `Cache-Control: public, max-age=604800`. |

## validators (`mealie/routes/validators/validators.py`, prefix `/api/validators`)

All public, response `ValidationResponse` `{"valid": bool}` (mealie/schema/response/validation.py).

| Method + path | Python | Notes |
|---|---|---|
| GET /api/validators/user/name?name= | validate_user (line 14) | case-insensitive username |
| GET /api/validators/user/email?email= | validate_user_email (line 22) | case-insensitive email |
| GET /api/validators/group?name= | validate_group (line 30) | exact group name |
| GET /api/validators/household?name= | validate_household (line 38) | Python calls `households.get_by_name` on a repo built with `group_id=None`, which raises `Exception("group_id not set")` (repository_household.py:70) → always 500 `Internal Server Error` (text/plain) after query validation. PHP reproduces that. |
| GET /api/validators/recipe?group_id=&name= | validate_recipe (line 46) | `group_id` UUID (any version); slug = python-slugify(name) approximation; `recipes` by (group_id, slug). |

## Not implemented

| Python route | Reason |
|---|---|
| GET /api/auth/oauth | OIDC flow against an outside provider (out of scope). |
| GET /api/auth/oauth/callback | OIDC (out of scope). |
| GET /api/auth/oauth/native/config | OIDC (out of scope). |
| POST /api/auth/oauth/native/token | OIDC (out of scope). |
| POST /api/users/forgot-password | Sends email (SMTP, out of scope); for an existing user the request cannot be answered without it. |
| POST /api/users/{id}/image | Needs Pillow WebP conversion (`img.PillowMinifier.to_webp`); not reproduced. |

Partially: register (new-group path), token (LDAP), password/update (IS_DEMO) as listed above. `auth_cache.py` defines no routes.

Count: 32 Python routes; 26 registered.

## Helpers duplicated from / missing in shared layer

- `App\Areas\AuthUsers\Support\Pyd` — FastAPI/Pydantic dev-mode 422 message builder (Python repr of inputs, error types, `File …, line …, in …   METHOD /path` suffix) and lax type checks. Shared `Errors::validation` only takes a free-form message, and `Guid::requireUuid4` produces `UUID version 4 expected at path`, which does not match Python's text.
- `App\Areas\AuthUsers\Support\Uuid` — Python `uuid.UUID()` / pydantic-core (uuid-rs) parsing incl. braced/urn forms and uuid-rs error strings (shared `Guid` accepts braces but not `urn:uuid:` and has no error text).
- `App\Areas\AuthUsers\Support\Settings` — Mealie `AppSettings` values read from env with Python defaults (shared `config/mealie.php` only has production/data_dir/secret).
- `App\Areas\AuthUsers\Support\Translator` — `mealie/lang` JSON lookup.
- `App\Areas\AuthUsers\Support\Users` — `UserOut` serialiser, bcrypt helpers.
- Shared `MealieAuth` returns `Could not validate credentials` for an unknown long-lived token; Python's `validate_long_live_token` returns 401 `{"detail":"Unauthorized"}` (dependencies.py:175). Not changed (shared layer).
