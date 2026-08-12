# Migration Guide

This guide is a reference for developers maintaining custom integrations with Mealie. While we aim to keep breaking changes to a minimum, major versions are likely to contain at least *some* breaking changes. To clarify: *most users do not need to worry about this, this is **only** for those maintaining integrations and/or leveraging the API*.

While this guide aims to simplify the migration process for developers, it's not necessarily a comprehensive list of breaking changes. Starting with v2, a comprehensive list of breaking changes are highlighted in the release notes.

## Deprecations

These still work, but are no longer the supported way of doing things, and may be removed in a future major version.

### `/recipes/create/image` → `/recipes/create/ai` (:octicons-tag-24: v3.23.0)

AI recipe creation is now a single endpoint that takes content and images together, rather than one endpoint per input type.

`/recipes/create/image` continues to work and is unchanged from a caller's perspective, but it is hidden from the OpenAPI schema, so it no longer appears in the API docs or in generated clients. It is now a thin wrapper around `/recipes/create/ai`. One behavioral difference: it now publishes a recipe-created notification, like every other creation endpoint, where before it published the event without a message.

`/recipes/create/ai` takes `multipart/form-data`, so it can accept images alongside everything else:

| Field | Notes |
| --- | --- |
| `content` | Raw HTML, a schema.org Recipe JSON string, or plain text |
| `url` | Fetched (or, for a video, transcribed), and saved as the recipe's source |
| `images` | Zero or more image files. The first becomes the recipe's image |
| `translateLanguage` | Optional language to translate the recipe into |
| `createNewOrganizers` | Whether to create tags, categories, and tools that don't already exist |

At least one of `content`, `url`, or `images` is required. Every field you send is used: passing a `url` and `content` together compiles both and merges them, rather than one replacing the other. There is also a `/recipes/create/ai/stream` variant that reports progress over SSE, which is what the Mealie frontend uses.

Note that `/recipes/create/html-or-json` is **not** deprecated. It remains the way to import raw data without involving AI.

### Custom prompt files (:octicons-tag-24: v3.23.0)

This only affects you if you've set `OPENAI_CUSTOM_PROMPT_DIR` and overridden the recipe prompts.

AI recipe creation is now a workflow of separate steps, each with its own prompt, so the two prompts that used to drive it have been replaced:

| Removed | Replaced by |
| --- | --- |
| `recipes/scrape-recipe.txt` | `recipes/compile-source.txt` and `recipes/build-recipe.txt` |
| `recipes/parse-recipe-image.txt` | `recipes/compile-source.txt` and `recipes/build-recipe.txt` |
| — | `recipes/resolve-organizers.txt` (new) |

`compile-source.txt` transcribes whatever the user supplied, and `build-recipe.txt` turns that transcription into recipe data. Overrides of the removed files are ignored. `recipes/parse-recipe-video.txt` and `recipes/parse-recipe-ingredients.txt` are unchanged.

## V1 → V2

The biggest change between V1 and V2 is the introduction of Households. For more information on how households work in relation to groups/users, check out the [Groups and Households](../../documentation/getting-started/features.md#groups-and-households) section in the Features guide.

### `updateAt` is now `updatedAt`

We have renamed the `updateAt` field to `updatedAt`. While the API will still accept `updateAt` as an alias, the API will return it as `updatedAt`. The field's behavior has otherwise been unchanged.

### Backend Endpoint Changes

These endpoints have moved, but are otherwise unchanged:

- `/recipes/create-url` -> `/recipes/create/url`
- `/recipes/create-url/bulk` -> `/recipes/create/url/bulk`
- `/recipes/create-from-zip` -> `/recipes/create/zip`
- `/recipes/create-from-image` -> `/recipes/create/image`
- `/groups/webhooks` -> `/households/webhooks`
- `/groups/shopping/items` -> `/households/shopping/items`
- `/groups/shopping/lists` -> `/households/shopping/lists`
- `/groups/mealplans` -> `/households/mealplans`
- `/groups/mealplans/rules` -> `/households/mealplans/rules`
- `/groups/invitations` -> `/households/invitations`
- `/groups/recipe-actions` -> `/households/recipe-actions`
- `/groups/events/notifications` -> `/households/events/notifications`
- `/groups/cookbooks` -> `/households/cookbooks`
- `/explore/foods/{group_slug}` -> `/explore/groups/{group_slug}/foods`
- `/explore/organizers/{group_slug}/categories` -> `/explore/groups/{group_slug}/categories`
- `/explore/organizers/{group_slug}/tags` -> `/explore/groups/{group_slug}/tags`
- `/explore/organizers/{group_slug}/tools` -> `/explore/groups/{group_slug}/tools`
- `/explore/cookbooks/{group_slug}` -> `/explore/groups/{group_slug}/cookbooks`
- `/explore/recipes/{group_slug}` -> `/explore/groups/{group_slug}/recipes`

`/groups/members` previously returned a `UserOut` object, but now returns a `UserSummary`. Should you need the full user information (username, email, etc.), rather than just the summary, see `/households/members` instead for the household members.
`/groups/members` previously returned a list of users, but now returns paginated users (similar to all other list endpoints).

These endpoints have been completely removed:

- `/admin/analytics` (no longer used)
- `/groups/permissions` (see household permissions)
- `/groups/statistics` (see household statistics)
- `/groups/categories` (see organizer endpoints)
- `/recipes/summary/untagged` (no longer used)
- `/recipes/summary/uncategorized` (no longer used)
- `/users/group-users` (see `/groups/members` and `/households/members`)

### Frontend Links

These frontend pages have moved:

- `/group/mealplan/...` -> `/household/mealplan/...`
- `/group/members` -> `/household/members`
- `/group/notifiers` -> `/household/notifiers`
- `/group/webhooks` -> `/household/webhooks`
