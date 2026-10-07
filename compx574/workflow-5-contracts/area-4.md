# Area 4 contract — groups, admin, explore

PHP: routes in `php-w5/routes/groups-admin.php`, classes in `php-w5/app/Areas/GroupsAdmin/`. Dev port 9014.

Conventions used by every endpoint below (not repeated per row):

- **Ids**: every `id`/`*_id` column of the tables touched here is `CHAR(32)` lowercase hex in SQLite and is returned dashed (`Guid::fromDb`). Exceptions: `long_live_tokens.id`, `password_reset_tokens.id`, `ai_provider_headers.id`, `ai_provider_params.id`, `ingredient_food_extras.id` are INTEGER and are never exposed as ids. Slugs (`groups.slug`, `households.slug`, tags/categories/tools `slug`) are plain strings.
- **Path params typed `UUID4`** in Python → `Guid::requireUuid4` (422 on malformed or non-v4). `str` params are not validated.
- **JSON keys**: `MealieModel` → camelCase (alias generator); `PaginationBase`, `SuccessResponse`, `ErrorResponse`, `BackupFile`/`AllBackups` → snake_case as declared.
- **Datetimes**: `Dates::out` (naive UTC + `Z`).
- **Auth layers**: `get_current_user` = `mealie/core/dependencies/dependencies.py:102`; `get_admin_user` = `dependencies.py:153` (403 `{"detail":"Forbidden"}`); `get_public_group` = `dependencies.py:66` (404 `"group not found"` when missing or `preferences.private_group`). `BaseUserController.user` = `mealie/routes/_base/base_controllers.py:139`; `BaseAdminController.user` = `base_controllers.py:182` (+ `AdminAPIRouter` dependency, `mealie/routes/_base/routers.py:17`). `checks.can_manage()` = `mealie/routes/_base/checks.py:28` (403 `{"detail":"Forbidden"}`), raised inside the handler, i.e. **after** body/path validation.
- **Pagination**: `RepositoryGeneric.page_all` (`mealie/repos/repository_generic.py:321`): default order `created_at desc` unless `orderBy` or `search` is given; `perPage=-1` = all; `page=-1` = last; `orderBy` accepts `a,b:asc`; tokenized `LIKE` search on the schema's `_searchable_properties`. `next`/`previous` are built from the router-local path (e.g. admin users → `/users?...`). Implemented in an area-local pager (see last section). `queryFilter`, `orderBy` on related fields and `orderBy=random` are not implemented (rule "不在范围内").

## Groups (`mealie/routes/groups/`)

| Method + path | Python source | Schema(s) | Who may call | Not implemented |
|---|---|---|---|---|
| GET /api/groups/self | controller_group_self_service.py:get_logged_in_user_group | user/user.py GroupSummary (+ group/group_preferences.py ReadGroupPreferences, group/ai_providers.py AIProviderSettingsOut) | any user (UserAPIRouter + get_current_user) | — |
| GET /api/groups/members | controller_group_self_service.py:get_group_members | PaginationBase[user/user.py UserSummary] | any user; repo scoped to caller's group | queryFilter |
| GET /api/groups/members/{username_or_id} | controller_group_self_service.py:get_group_member | UserSummary | any user; group-scoped lookup by id if the string parses as a UUID, else by username; 404 `"User Not Found"` | — |
| GET /api/groups/preferences | controller_group_self_service.py:get_group_preferences | ReadGroupPreferences | any user | — |
| PUT /api/groups/preferences | controller_group_self_service.py:update_group_preferences | in: UpdateGroupPreferences; out: ReadGroupPreferences | user with `can_manage` (checks.py:28, handler line 59) | — |
| GET /api/groups/storage | controller_group_self_service.py:get_storage | group/group_statistics.py GroupStorage | any user | — (sizes depend on the filesystem the server sees) |
| GET /api/groups/households | controller_group_households.py:get_all_households | PaginationBase[household/household.py HouseholdSummary] | any user; group-scoped | queryFilter |
| GET /api/groups/households/{household_slug} | controller_group_households.py:get_one_household | HouseholdSummary | any user; by id if UUID else slug, group-scoped; 404 `"Household not found"` | — |
| GET /api/groups/labels | controller_labels.py:get_all | labels/multi_purpose_label.py MultiPurposeLabelSummary (pagination) | any user (BaseCrudController → get_current_user) | queryFilter |
| POST /api/groups/labels | controller_labels.py:create_one; services/group_services/labels_service.py:create_one | in: MultiPurposeLabelCreate; out: MultiPurposeLabelOut | any user | event bus notification not sent |
| GET /api/groups/labels/{item_id} | controller_labels.py:get_one | MultiPurposeLabelOut | any user; group-scoped; 404 ErrorResponse "Not found." | — |
| PUT /api/groups/labels/{item_id} | controller_labels.py:update_one | in: MultiPurposeLabelUpdate (requires groupId, id); out: MultiPurposeLabelOut | any user | event bus |
| DELETE /api/groups/labels/{item_id} | controller_labels.py:delete_one | MultiPurposeLabelOut | any user | event bus |
| GET /api/groups/reports | controller_group_reports.py:get_all | list[reports/reports.py ReportSummary]; `report_type` enum query | any user (BaseUserController) | — |
| GET /api/groups/reports/{item_id} | controller_group_reports.py:get_one | ReportOut (with entries) | any user, group-scoped | — |
| DELETE /api/groups/reports/{item_id} | controller_group_reports.py:delete_one | SuccessResponse "Report deleted." / 500 ErrorResponse | any user, group-scoped | — |
| GET /api/groups/ai-providers/settings | controller_group_ai_providers.py:get_ai_provider_settings | AIProviderSettingsOut | `can_manage` (line 29) | — |
| PUT /api/groups/ai-providers/settings | controller_group_ai_providers.py:update_ai_provider_settings | in: AIProviderSettingsUpdate; out: AIProviderSettingsOut | `can_manage` (line 35) | — |
| POST /api/groups/ai-providers/providers | controller_group_ai_providers.py:create_ai_provider; repos/repository_ai_provider.py:create | in: AIProviderCreate; out: AIProviderOut (apiKey excluded) | `can_manage` (line 48) | — |
| GET /api/groups/ai-providers/providers/{provider_id} | controller_group_ai_providers.py:get_ai_provider | AIProviderOut | `can_manage` (line 102) | — |
| PUT /api/groups/ai-providers/providers/{provider_id} | controller_group_ai_providers.py:update_ai_provider; repository_ai_provider.py:update | in: AIProviderUpdate; out: AIProviderOut | `can_manage` (line 108) | — |
| DELETE /api/groups/ai-providers/providers/{provider_id} | controller_group_ai_providers.py:delete_ai_provider; repository_ai_provider.py:delete | AIProviderOut | `can_manage` (line 114) | — |

## Admin (`mealie/routes/admin/`, all behind AdminAPIRouter + get_admin_user; repos unscoped)

| Method + path | Python source | Schema(s) | Who may call | Not implemented |
|---|---|---|---|---|
| GET /api/admin/about/statistics | admin_about.py:get_app_statistics | admin/about.py AppStatistics | admin | — |
| GET /api/admin/about/check | admin_about.py:check_app_config | admin/about.py CheckAppConfig | admin | settings read from the PHP process env with the Python names/defaults (SMTP_*, LDAP_*, OIDC_*, BASE_URL); `isUpToDate` only answered locally because APP_VERSION is `develop` |
| GET /api/admin/users | admin_management_users.py:get_all | user/user.py UserOut (UserPagination) | admin | queryFilter |
| POST /api/admin/users | admin_management_users.py:create_one; repos/repository_users.py:create; db/models/users/users.py User.__init__ | in: UserIn; out: UserOut, 201 | admin | random profile image copy is done from `mealie/assets/users` |
| POST /api/admin/users/unlock | admin_management_users.py:unlock_users; services/user_services/user_service.py:reset_locked_users | user/auth.py UnlockResults | admin | — |
| GET /api/admin/users/{item_id} | admin_management_users.py:get_one | UserOut | admin | — |
| PUT /api/admin/users/{item_id} | admin_management_users.py:update_one; User.update | in/out: UserOut | admin; 403 ErrorResponse "you cannot demote yourself" | — |
| DELETE /api/admin/users/{item_id} | admin_management_users.py:delete_one; repository_users.py:delete | UserOut | admin | — |
| POST /api/admin/users/password-reset-token | admin_management_users.py:generate_token; services/user_services/password_reset_service.py:generate_reset_token | in: user/user_passwords.py ForgotPassword; out: PasswordResetToken, 201 | admin | — |
| GET /api/admin/households | admin_management_households.py:get_all | household/household.py HouseholdInDB (HouseholdPagination) | admin | queryFilter |
| POST /api/admin/households | admin_management_households.py:create_one; services/household_services/household_service.py:create_household | in: HouseholdCreate; out: HouseholdInDB, 201 | admin | — |
| GET /api/admin/households/{item_id} | admin_management_households.py:get_one | HouseholdInDB | admin | — |
| PUT /api/admin/households/{item_id} | admin_management_households.py:update_one | in: UpdateHouseholdAdmin; out: HouseholdInDB | admin | — |
| DELETE /api/admin/households/{item_id} | admin_management_households.py:delete_one | HouseholdInDB; 400 if users | admin | — |
| GET /api/admin/groups | admin_management_groups.py:get_all | user/user.py GroupInDB (GroupPagination) | admin | queryFilter |
| POST /api/admin/groups | admin_management_groups.py:create_one; services/group_services/group_service.py:create_group | in: GroupBase; out: GroupInDB, 201 | admin | — |
| GET /api/admin/groups/{item_id} | admin_management_groups.py:get_one | GroupInDB | admin | — |
| PUT /api/admin/groups/{item_id} | admin_management_groups.py:update_one | in: group/group.py GroupAdminUpdate; out: GroupInDB | admin | — |
| DELETE /api/admin/groups/{item_id} | admin_management_groups.py:delete_one | GroupInDB; 400 if users | admin | — |
| POST /api/admin/groups/{group_id}/ai-providers/providers | admin_management_ai_providers.py:create_ai_provider | AIProviderCreate → AIProviderOut | admin | — |
| GET /api/admin/groups/{group_id}/ai-providers/providers/{provider_id} | admin_management_ai_providers.py:get_ai_provider | AIProviderOut | admin | — |
| PUT /api/admin/groups/{group_id}/ai-providers/providers/{provider_id} | admin_management_ai_providers.py:update_ai_provider | AIProviderUpdate → AIProviderOut | admin | — |
| DELETE /api/admin/groups/{group_id}/ai-providers/providers/{provider_id} | admin_management_ai_providers.py:delete_ai_provider | AIProviderOut | admin | — |
| GET /api/admin/email | admin_email.py:check_email_config | admin/email.py EmailReady | admin | SMTP settings from PHP env (same names as Python) |
| GET /api/admin/backups | admin_backups.py:get_all | admin/backup.py AllBackups (snake_case) | admin | — |
| GET /api/admin/backups/{file_name} | admin_backups.py:get_one | response/responses.py FileTokenResponse | admin | token embeds the path as the PHP process sees it |
| DELETE /api/admin/backups/{file_name} | admin_backups.py:delete_one | SuccessResponse | admin | — |
| GET /api/admin/maintenance | admin_maintenance.py:get_maintenance_summary | admin/maintenance.py MaintenanceSummary | admin | — |
| GET /api/admin/maintenance/storage | admin_maintenance.py:get_storage_details | MaintenanceStorageDetails | admin | — |
| POST /api/admin/maintenance/clean/images | admin_maintenance.py:clean_images | SuccessResponse | admin | — |
| POST /api/admin/maintenance/clean/temp | admin_maintenance.py:clean_temp | SuccessResponse | admin | — |
| POST /api/admin/maintenance/clean/recipe-folders | admin_maintenance.py:clean_recipe_folders | SuccessResponse | admin | — |

## Explore (`mealie/routes/explore/`, public; all behind get_public_group, prefix `/explore/groups/{group_slug}`)

| Method + path | Python source | Schema(s) | Who may call | Not implemented |
|---|---|---|---|---|
| GET /api/explore/groups/{group_slug}/foods | controller_public_foods.py:get_all | recipe/recipe_ingredient.py IngredientFood (pagination) | anyone; group public | queryFilter; search uses an ASCII transliteration for unidecode |
| GET /api/explore/groups/{group_slug}/foods/{item_id} | controller_public_foods.py:get_one | IngredientFood; 404 "food not found" | anyone | — |
| GET /api/explore/groups/{group_slug}/households | controller_public_households.py:get_all | HouseholdSummary (pagination), only `private_household = FALSE` | anyone | user queryFilter (the fixed public filter is applied in SQL) |
| GET /api/explore/groups/{group_slug}/households/{household_slug} | controller_public_households.py:get_household; base_controllers.py:102 get_public_household | HouseholdSummary; 404 "household not found" | anyone | — |
| GET /api/explore/groups/{group_slug}/organizers/categories | controller_public_organizers.py:PublicCategoriesController.get_all | recipe/recipe.py RecipeCategory (pagination; Python builds next/previous from the *tags* router — kept) | anyone | queryFilter |
| GET /api/explore/groups/{group_slug}/organizers/categories/{item_id} | ...PublicCategoriesController.get_one | recipe/recipe_category.py CategoryOut; 404 "category not found" | anyone | — |
| GET /api/explore/groups/{group_slug}/organizers/tags | ...PublicTagsController.get_all | RecipeTag (pagination) | anyone | queryFilter |
| GET /api/explore/groups/{group_slug}/organizers/tags/{item_id} | ...PublicTagsController.get_one | recipe_category.py TagOut; 404 "tag not found" | anyone | — |
| GET /api/explore/groups/{group_slug}/organizers/tools | ...PublicToolsController.get_all | RecipeTool (pagination) | anyone | queryFilter |
| GET /api/explore/groups/{group_slug}/organizers/tools/{item_id} | ...PublicToolsController.get_one | recipe/recipe_tool.py RecipeToolOut; 404 "tool not found" | anyone | — |

## Not implemented (not registered)

| Method + path | Reason |
|---|---|
| POST /api/groups/ai-providers/providers/test | calls an AI provider (OpenAIService) — out of scope |
| POST /api/groups/ai-providers/providers/{provider_id}/test | calls an AI provider — out of scope |
| POST /api/groups/migrations | data migrations from other apps (`services/migrations`) — out of scope |
| POST /api/groups/seeders/foods | not done this round: seeding loads locale resource files through `SeederService`; left unregistered rather than partially ported |
| POST /api/groups/seeders/units | same as above |
| GET /api/admin/about | needs GitHub latest release (outside service) and the `recipe_scrapers` package version (Python-only) |
| POST /api/admin/email | sends email (SMTP) — out of scope |
| POST /api/admin/backups | creating backups — out of scope |
| POST /api/admin/backups/upload | uploading backups — out of scope |
| POST /api/admin/backups/{file_name}/restore | restoring backups — out of scope |
| POST /api/admin/debug/openai/{provider_id} | calls an AI provider — out of scope |
| GET /api/explore/groups/{group_slug}/cookbooks | `ReadCookBook.queryFilter` is produced by the queryFilter parser (`QueryFilterBuilder.as_json_model`) — out of scope |
| GET /api/explore/groups/{group_slug}/cookbooks/{item_id} | same |
| GET /api/explore/groups/{group_slug}/recipes | cookbook filtering needs the queryFilter language; full `RecipeSummary` search (normalized multi-field) not ported |
| GET /api/explore/groups/{group_slug}/recipes/suggestions | suggestion algorithm (`_recipe_suggestions.py`) with queryFilter — not ported |
| GET /api/explore/groups/{group_slug}/recipes/{recipe_slug} | full `Recipe` schema (ingredients, instructions, nutrition, assets, comments …) belongs to area 2's serializers; not duplicated |

Count: Python routes in area 80 (groups 27, admin 38, explore 15); implemented 64 (groups 22, admin 32, explore 10); not registered 16.

## Helpers duplicated from / missing in shared layer

- `GroupsAdmin\Support\Pager` — a fuller port of `RepositoryGeneric.page_all` than `App\Support\Pagination`: default `created_at desc` only when no `orderBy` and no search; `orderBy` lists with `col:dir`; `orderByNullPosition`; 400 on unknown columns; `perPage=-1`/`page=-1`; 422 on non-integer `page`/`perPage` and bad `orderDirection`; `next`/`previous` built from the *requested* `perPage` (Python dumps the original query); tokenized search callback.
- `GroupsAdmin\Support\Validator` — field-level body validation (required, str/bool/int/UUID coercion, enum) producing the dev-mode 422 shape via `Errors::validation`. The shared layer only has `Json::body` (object check).
- `GroupsAdmin\Support\Fs` — `pretty_size`/`get_dir_size` ports (`mealie/pkgs/stats/fs_stats.py`) and Python float formatting.
- `GroupsAdmin\Support\Slug` — `python-slugify` subset (ASCII transliteration, lowercase, non-alnum → `-`).
- Error message text for 422 cannot match Python exactly (Python includes a source file/line); status and envelope match.
