# Shared API check. Python on port 9000 is the oracle.
# Each member runs this file unchanged and only changes {{candidate}}.
# Body bytes are not compared. Asserts are status, plus a few contract fields.

GET http://127.0.0.1:9000/api/app/about
HTTP *
[Captures]
about_status: status

GET {{candidate}}/api/app/about
HTTP *
[Asserts]
status == {{about_status}}

GET http://127.0.0.1:9000/api/app/about/startup-info
HTTP *
[Captures]
startup_status: status

GET {{candidate}}/api/app/about/startup-info
HTTP *
[Asserts]
status == {{startup_status}}

GET http://127.0.0.1:9000/api/app/about/theme
HTTP *
[Captures]
theme_status: status

GET {{candidate}}/api/app/about/theme
HTTP *
[Asserts]
status == {{theme_status}}

GET http://127.0.0.1:9000/api/validators/user/name?name=nobody-accuracy-check
HTTP *
[Captures]
validator_status: status

GET {{candidate}}/api/validators/user/name?name=nobody-accuracy-check
HTTP *
[Asserts]
status == {{validator_status}}

GET http://127.0.0.1:9000/api/auth/oauth
HTTP *
[Captures]
oauth_status: status

GET {{candidate}}/api/auth/oauth
HTTP *
[Asserts]
status == {{oauth_status}}

GET http://127.0.0.1:9000/api/users/self
Authorization: Bearer {{token}}
HTTP *
[Captures]
self_status: status

GET {{candidate}}/api/users/self
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{self_status}}
jsonpath "$.authMethod" == "Mealie"

GET http://127.0.0.1:9000/api/users/self/ratings
Authorization: Bearer {{token}}
HTTP *
[Captures]
ratings_status: status

GET {{candidate}}/api/users/self/ratings
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{ratings_status}}

GET http://127.0.0.1:9000/api/users/self/favorites
Authorization: Bearer {{token}}
HTTP *
[Captures]
favorites_status: status

GET {{candidate}}/api/users/self/favorites
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{favorites_status}}

GET http://127.0.0.1:9000/api/users/api-tokens
Authorization: Bearer {{token}}
HTTP *
[Captures]
tokens_status: status

GET {{candidate}}/api/users/api-tokens
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{tokens_status}}

GET http://127.0.0.1:9000/api/groups/self
Authorization: Bearer {{token}}
HTTP *
[Captures]
group_status: status

GET {{candidate}}/api/groups/self
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{group_status}}

GET http://127.0.0.1:9000/api/groups/preferences
Authorization: Bearer {{token}}
HTTP *
[Captures]
group_prefs_status: status

GET {{candidate}}/api/groups/preferences
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{group_prefs_status}}

GET http://127.0.0.1:9000/api/groups/members?page=1&perPage=10
Authorization: Bearer {{token}}
HTTP *
[Captures]
group_members_status: status

GET {{candidate}}/api/groups/members?page=1&perPage=10
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{group_members_status}}
jsonpath "$.per_page" exists
jsonpath "$.total_pages" exists

GET http://127.0.0.1:9000/api/groups/storage
Authorization: Bearer {{token}}
HTTP *
[Captures]
storage_status: status

GET {{candidate}}/api/groups/storage
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{storage_status}}

GET http://127.0.0.1:9000/api/groups/households?page=1&perPage=10
Authorization: Bearer {{token}}
HTTP *
[Captures]
group_households_status: status

GET {{candidate}}/api/groups/households?page=1&perPage=10
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{group_households_status}}
jsonpath "$.per_page" exists
jsonpath "$.total_pages" exists

GET http://127.0.0.1:9000/api/groups/reports
Authorization: Bearer {{token}}
HTTP *
[Captures]
reports_status: status

GET {{candidate}}/api/groups/reports
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{reports_status}}

GET http://127.0.0.1:9000/api/groups/ai-providers/settings
Authorization: Bearer {{token}}
HTTP *
[Captures]
ai_settings_status: status

GET {{candidate}}/api/groups/ai-providers/settings
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{ai_settings_status}}

GET http://127.0.0.1:9000/api/households/self
Authorization: Bearer {{token}}
HTTP *
[Captures]
household_status: status

GET {{candidate}}/api/households/self
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{household_status}}

GET http://127.0.0.1:9000/api/households/preferences
Authorization: Bearer {{token}}
HTTP *
[Captures]
household_prefs_status: status

GET {{candidate}}/api/households/preferences
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{household_prefs_status}}

GET http://127.0.0.1:9000/api/households/members?page=1&perPage=10
Authorization: Bearer {{token}}
HTTP *
[Captures]
household_members_status: status

GET {{candidate}}/api/households/members?page=1&perPage=10
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{household_members_status}}

GET http://127.0.0.1:9000/api/households/statistics
Authorization: Bearer {{token}}
HTTP *
[Captures]
stats_status: status

GET {{candidate}}/api/households/statistics
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{stats_status}}

GET http://127.0.0.1:9000/api/households/cookbooks?page=1&perPage=10
Authorization: Bearer {{token}}
HTTP *
[Captures]
cookbooks_status: status

GET {{candidate}}/api/households/cookbooks?page=1&perPage=10
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{cookbooks_status}}
jsonpath "$.per_page" exists
jsonpath "$.total_pages" exists

GET http://127.0.0.1:9000/api/households/mealplans/today
Authorization: Bearer {{token}}
HTTP *
[Captures]
today_status: status

GET {{candidate}}/api/households/mealplans/today
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{today_status}}

GET http://127.0.0.1:9000/api/households/mealplans?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Captures]
mealplans_status: status

GET {{candidate}}/api/households/mealplans?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{mealplans_status}}
jsonpath "$.per_page" exists
jsonpath "$.total_pages" exists

GET http://127.0.0.1:9000/api/households/mealplans/rules?page=1&perPage=10
Authorization: Bearer {{token}}
HTTP *
[Captures]
rules_status: status

GET {{candidate}}/api/households/mealplans/rules?page=1&perPage=10
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{rules_status}}
jsonpath "$.per_page" exists
jsonpath "$.total_pages" exists

GET http://127.0.0.1:9000/api/households/shopping/lists?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Captures]
lists_status: status

GET {{candidate}}/api/households/shopping/lists?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{lists_status}}
jsonpath "$.per_page" exists
jsonpath "$.total_pages" exists

GET http://127.0.0.1:9000/api/households/shopping/items?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Captures]
items_status: status

GET {{candidate}}/api/households/shopping/items?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{items_status}}
jsonpath "$.per_page" exists
jsonpath "$.total_pages" exists

GET http://127.0.0.1:9000/api/households/webhooks?page=1&perPage=10
Authorization: Bearer {{token}}
HTTP *
[Captures]
webhooks_status: status

GET {{candidate}}/api/households/webhooks?page=1&perPage=10
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{webhooks_status}}
jsonpath "$.per_page" exists
jsonpath "$.total_pages" exists

GET http://127.0.0.1:9000/api/households/invitations
Authorization: Bearer {{token}}
HTTP *
[Captures]
invitations_status: status

GET {{candidate}}/api/households/invitations
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{invitations_status}}

GET http://127.0.0.1:9000/api/households/events/notifications?page=1&perPage=10
Authorization: Bearer {{token}}
HTTP *
[Captures]
notifications_status: status

GET {{candidate}}/api/households/events/notifications?page=1&perPage=10
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{notifications_status}}
jsonpath "$.per_page" exists
jsonpath "$.total_pages" exists

GET http://127.0.0.1:9000/api/households/recipe-actions?page=1&perPage=10
Authorization: Bearer {{token}}
HTTP *
[Captures]
actions_status: status

GET {{candidate}}/api/households/recipe-actions?page=1&perPage=10
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{actions_status}}
jsonpath "$.per_page" exists
jsonpath "$.total_pages" exists

GET http://127.0.0.1:9000/api/recipes?page=1&perPage=3
Authorization: Bearer {{token}}
HTTP *
[Captures]
recipes_status: status

GET {{candidate}}/api/recipes?page=1&perPage=3
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{recipes_status}}
jsonpath "$.per_page" exists
jsonpath "$.total_pages" exists

GET http://127.0.0.1:9000/api/recipes/suggestions?limit=3
Authorization: Bearer {{token}}
HTTP *
[Captures]
suggestions_status: status

GET {{candidate}}/api/recipes/suggestions?limit=3
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{suggestions_status}}

GET http://127.0.0.1:9000/api/recipes/timeline/events?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Captures]
timeline_status: status

GET {{candidate}}/api/recipes/timeline/events?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{timeline_status}}
jsonpath "$.per_page" exists
jsonpath "$.total_pages" exists

GET http://127.0.0.1:9000/api/organizers/categories?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Captures]
categories_status: status

GET {{candidate}}/api/organizers/categories?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{categories_status}}
jsonpath "$.per_page" exists
jsonpath "$.total_pages" exists

GET http://127.0.0.1:9000/api/organizers/tags?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Captures]
tags_status: status

GET {{candidate}}/api/organizers/tags?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{tags_status}}
jsonpath "$.per_page" exists
jsonpath "$.total_pages" exists

GET http://127.0.0.1:9000/api/organizers/tools?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Captures]
tools_status: status

GET {{candidate}}/api/organizers/tools?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{tools_status}}
jsonpath "$.per_page" exists
jsonpath "$.total_pages" exists

GET http://127.0.0.1:9000/api/foods?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Captures]
foods_status: status

GET {{candidate}}/api/foods?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{foods_status}}
jsonpath "$.per_page" exists
jsonpath "$.total_pages" exists

GET http://127.0.0.1:9000/api/units?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Captures]
units_status: status

GET {{candidate}}/api/units?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{units_status}}
jsonpath "$.per_page" exists
jsonpath "$.total_pages" exists

GET http://127.0.0.1:9000/api/groups/labels?page=1&perPage=10
Authorization: Bearer {{token}}
HTTP *
[Captures]
labels_status: status

GET {{candidate}}/api/groups/labels?page=1&perPage=10
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{labels_status}}
jsonpath "$.per_page" exists
jsonpath "$.total_pages" exists

GET http://127.0.0.1:9000/api/comments?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Captures]
comments_status: status

GET {{candidate}}/api/comments?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{comments_status}}
jsonpath "$.per_page" exists
jsonpath "$.total_pages" exists

GET http://127.0.0.1:9000/api/shared/recipes?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Captures]
shared_status: status

GET {{candidate}}/api/shared/recipes?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{shared_status}}
jsonpath "$.items" not exists
