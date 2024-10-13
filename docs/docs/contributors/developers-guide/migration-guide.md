# Migration Guide

This guide is a reference for developers maintaining custom integrations with Mealie. While we aim to keep breaking changes to a minimum, major versions are likely to contain at least *some* breaking changes. To clarify: *most users do not need to worry about this, this is **only** for those maintaining integrations and/or leveraging the API*.

While this guide aims to simplify the migration process for developers, it's not necessarily a comprehensive list of breaking changes. Starting with v2, a comprehensive list of breaking changes are highlighted in the release notes.

## V1 → V2

The biggest change between V1 and V2 is the introduction of Households. For more information on how households work in relation to groups/users, check out the [Groups and Households](./features.md#groups-and-households) section in the Features guide.

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
