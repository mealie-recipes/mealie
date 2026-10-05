# Shared API check. Python on port 9000 is the oracle.
# Each member runs this file unchanged and only changes {{candidate}}.
# Body bytes are not compared. Asserts are status, plus a few contract fields.
# GET requests use rows that exist in dev/data/mealie.db when one is available.
# Other methods send a rejected body or a zero id, so the shared database is left as it is.
# Eight calls are marked skip: they have no rejectable body and would back up, clean, purge, fire webhooks, or call the AI provider.

GET http://127.0.0.1:9000/api/admin/about
Authorization: Bearer {{token}}
HTTP *
[Captures]
s1: status

GET {{candidate}}/api/admin/about
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s1}}

GET http://127.0.0.1:9000/api/admin/about/check
Authorization: Bearer {{token}}
HTTP *
[Captures]
s2: status

GET {{candidate}}/api/admin/about/check
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s2}}

GET http://127.0.0.1:9000/api/admin/about/statistics
Authorization: Bearer {{token}}
HTTP *
[Captures]
s3: status

GET {{candidate}}/api/admin/about/statistics
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s3}}

GET http://127.0.0.1:9000/api/admin/backups
Authorization: Bearer {{token}}
HTTP *
[Captures]
s4: status

GET {{candidate}}/api/admin/backups
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s4}}

# Not executed: this call changes stored data or fires webhooks, and nothing in the request can make the handler reject it first.
POST http://127.0.0.1:9000/api/admin/backups
Authorization: Bearer {{token}}
[Options]
skip: true
HTTP *

POST {{candidate}}/api/admin/backups
Authorization: Bearer {{token}}
[Options]
skip: true
HTTP *

POST http://127.0.0.1:9000/api/admin/backups/upload
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s6: status

POST {{candidate}}/api/admin/backups/upload
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s6}}

GET http://127.0.0.1:9000/api/admin/backups/parity-missing.bin
Authorization: Bearer {{token}}
HTTP *
[Captures]
s7: status

GET {{candidate}}/api/admin/backups/parity-missing.bin
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s7}}

DELETE http://127.0.0.1:9000/api/admin/backups/parity-missing.bin
Authorization: Bearer {{token}}
HTTP *
[Captures]
s8: status

DELETE {{candidate}}/api/admin/backups/parity-missing.bin
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s8}}

POST http://127.0.0.1:9000/api/admin/backups/parity-missing.bin/restore
Authorization: Bearer {{token}}
HTTP *
[Captures]
s9: status

POST {{candidate}}/api/admin/backups/parity-missing.bin/restore
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s9}}

POST http://127.0.0.1:9000/api/admin/debug/openai/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s10: status

POST {{candidate}}/api/admin/debug/openai/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s10}}

GET http://127.0.0.1:9000/api/admin/email
Authorization: Bearer {{token}}
HTTP *
[Captures]
s11: status

GET {{candidate}}/api/admin/email
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s11}}

POST http://127.0.0.1:9000/api/admin/email
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s12: status

POST {{candidate}}/api/admin/email
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s12}}

GET http://127.0.0.1:9000/api/admin/groups?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Captures]
s13: status

GET {{candidate}}/api/admin/groups?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s13}}

POST http://127.0.0.1:9000/api/admin/groups
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s14: status

POST {{candidate}}/api/admin/groups
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s14}}

POST http://127.0.0.1:9000/api/admin/groups/00000000-0000-0000-0000-000000000000/ai-providers/providers
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s15: status

POST {{candidate}}/api/admin/groups/00000000-0000-0000-0000-000000000000/ai-providers/providers
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s15}}

GET http://127.0.0.1:9000/api/admin/groups/dcf19c89-e7aa-470c-9707-deaf30cb5c45/ai-providers/providers/533d1eb0-b65e-4e1d-a33d-b705bb5fe548
Authorization: Bearer {{token}}
HTTP *
[Captures]
s16: status

GET {{candidate}}/api/admin/groups/dcf19c89-e7aa-470c-9707-deaf30cb5c45/ai-providers/providers/533d1eb0-b65e-4e1d-a33d-b705bb5fe548
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s16}}

PUT http://127.0.0.1:9000/api/admin/groups/00000000-0000-0000-0000-000000000000/ai-providers/providers/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s17: status

PUT {{candidate}}/api/admin/groups/00000000-0000-0000-0000-000000000000/ai-providers/providers/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s17}}

DELETE http://127.0.0.1:9000/api/admin/groups/00000000-0000-0000-0000-000000000000/ai-providers/providers/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Captures]
s18: status

DELETE {{candidate}}/api/admin/groups/00000000-0000-0000-0000-000000000000/ai-providers/providers/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s18}}

GET http://127.0.0.1:9000/api/admin/groups/dcf19c89-e7aa-470c-9707-deaf30cb5c45
Authorization: Bearer {{token}}
HTTP *
[Captures]
s19: status

GET {{candidate}}/api/admin/groups/dcf19c89-e7aa-470c-9707-deaf30cb5c45
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s19}}

PUT http://127.0.0.1:9000/api/admin/groups/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s20: status

PUT {{candidate}}/api/admin/groups/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s20}}

DELETE http://127.0.0.1:9000/api/admin/groups/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Captures]
s21: status

DELETE {{candidate}}/api/admin/groups/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s21}}

GET http://127.0.0.1:9000/api/admin/households?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Captures]
s22: status

GET {{candidate}}/api/admin/households?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s22}}

POST http://127.0.0.1:9000/api/admin/households
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s23: status

POST {{candidate}}/api/admin/households
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s23}}

GET http://127.0.0.1:9000/api/admin/households/d943679f-32ca-4a27-852a-08e83537b727
Authorization: Bearer {{token}}
HTTP *
[Captures]
s24: status

GET {{candidate}}/api/admin/households/d943679f-32ca-4a27-852a-08e83537b727
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s24}}

PUT http://127.0.0.1:9000/api/admin/households/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s25: status

PUT {{candidate}}/api/admin/households/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s25}}

DELETE http://127.0.0.1:9000/api/admin/households/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Captures]
s26: status

DELETE {{candidate}}/api/admin/households/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s26}}

GET http://127.0.0.1:9000/api/admin/maintenance
Authorization: Bearer {{token}}
HTTP *
[Captures]
s27: status

GET {{candidate}}/api/admin/maintenance
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s27}}

# Not executed: this call changes stored data or fires webhooks, and nothing in the request can make the handler reject it first.
POST http://127.0.0.1:9000/api/admin/maintenance/clean/images
Authorization: Bearer {{token}}
[Options]
skip: true
HTTP *

POST {{candidate}}/api/admin/maintenance/clean/images
Authorization: Bearer {{token}}
[Options]
skip: true
HTTP *

# Not executed: this call changes stored data or fires webhooks, and nothing in the request can make the handler reject it first.
POST http://127.0.0.1:9000/api/admin/maintenance/clean/recipe-folders
Authorization: Bearer {{token}}
[Options]
skip: true
HTTP *

POST {{candidate}}/api/admin/maintenance/clean/recipe-folders
Authorization: Bearer {{token}}
[Options]
skip: true
HTTP *

# Not executed: this call changes stored data or fires webhooks, and nothing in the request can make the handler reject it first.
POST http://127.0.0.1:9000/api/admin/maintenance/clean/temp
Authorization: Bearer {{token}}
[Options]
skip: true
HTTP *

POST {{candidate}}/api/admin/maintenance/clean/temp
Authorization: Bearer {{token}}
[Options]
skip: true
HTTP *

GET http://127.0.0.1:9000/api/admin/maintenance/storage
Authorization: Bearer {{token}}
HTTP *
[Captures]
s31: status

GET {{candidate}}/api/admin/maintenance/storage
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s31}}

GET http://127.0.0.1:9000/api/admin/users?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Captures]
s32: status

GET {{candidate}}/api/admin/users?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s32}}

POST http://127.0.0.1:9000/api/admin/users
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s33: status

POST {{candidate}}/api/admin/users
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s33}}

POST http://127.0.0.1:9000/api/admin/users/password-reset-token
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s34: status

POST {{candidate}}/api/admin/users/password-reset-token
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s34}}

POST http://127.0.0.1:9000/api/admin/users/unlock
Authorization: Bearer {{token}}
HTTP *
[Captures]
s35: status

POST {{candidate}}/api/admin/users/unlock
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s35}}

GET http://127.0.0.1:9000/api/admin/users/506612c6-6f04-44e3-8e63-1850f7bd65fd
Authorization: Bearer {{token}}
HTTP *
[Captures]
s36: status

GET {{candidate}}/api/admin/users/506612c6-6f04-44e3-8e63-1850f7bd65fd
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s36}}

PUT http://127.0.0.1:9000/api/admin/users/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s37: status

PUT {{candidate}}/api/admin/users/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s37}}

DELETE http://127.0.0.1:9000/api/admin/users/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Captures]
s38: status

DELETE {{candidate}}/api/admin/users/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s38}}

GET http://127.0.0.1:9000/api/app/about
HTTP *
[Captures]
s39: status

GET {{candidate}}/api/app/about
HTTP *
[Asserts]
status == {{s39}}

GET http://127.0.0.1:9000/api/app/about/startup-info
HTTP *
[Captures]
s40: status

GET {{candidate}}/api/app/about/startup-info
HTTP *
[Asserts]
status == {{s40}}

GET http://127.0.0.1:9000/api/app/about/theme
HTTP *
[Captures]
s41: status

GET {{candidate}}/api/app/about/theme
HTTP *
[Asserts]
status == {{s41}}

POST http://127.0.0.1:9000/api/auth/logout
Authorization: Bearer {{token}}
HTTP *
[Captures]
s42: status

POST {{candidate}}/api/auth/logout
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s42}}

GET http://127.0.0.1:9000/api/auth/oauth
HTTP *
[Captures]
s43: status

GET {{candidate}}/api/auth/oauth
HTTP *
[Asserts]
status == {{s43}}

GET http://127.0.0.1:9000/api/auth/oauth/callback
HTTP *
[Captures]
s44: status

GET {{candidate}}/api/auth/oauth/callback
HTTP *
[Asserts]
status == {{s44}}

GET http://127.0.0.1:9000/api/auth/oauth/native/config
HTTP *
[Captures]
s45: status

GET {{candidate}}/api/auth/oauth/native/config
HTTP *
[Asserts]
status == {{s45}}

POST http://127.0.0.1:9000/api/auth/oauth/native/token
Content-Type: application/json
0
HTTP *
[Captures]
s46: status

POST {{candidate}}/api/auth/oauth/native/token
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s46}}

POST http://127.0.0.1:9000/api/auth/refresh
Authorization: Bearer {{token}}
HTTP *
[Captures]
s47: status

POST {{candidate}}/api/auth/refresh
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s47}}

POST http://127.0.0.1:9000/api/auth/token
Content-Type: application/x-www-form-urlencoded
x=1
HTTP *
[Captures]
s48: status

POST {{candidate}}/api/auth/token
Content-Type: application/x-www-form-urlencoded
x=1
HTTP *
[Asserts]
status == {{s48}}

GET http://127.0.0.1:9000/api/comments?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Captures]
s49: status

GET {{candidate}}/api/comments?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s49}}
jsonpath "$.per_page" exists
jsonpath "$.total_pages" exists

POST http://127.0.0.1:9000/api/comments
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s50: status

POST {{candidate}}/api/comments
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s50}}

GET http://127.0.0.1:9000/api/comments/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Captures]
s51: status

GET {{candidate}}/api/comments/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s51}}

PUT http://127.0.0.1:9000/api/comments/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s52: status

PUT {{candidate}}/api/comments/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s52}}

DELETE http://127.0.0.1:9000/api/comments/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Captures]
s53: status

DELETE {{candidate}}/api/comments/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s53}}

GET http://127.0.0.1:9000/api/explore/groups/home/cookbooks?page=1&perPage=5
HTTP *
[Captures]
s54: status

GET {{candidate}}/api/explore/groups/home/cookbooks?page=1&perPage=5
HTTP *
[Asserts]
status == {{s54}}

GET http://127.0.0.1:9000/api/explore/groups/home/cookbooks/00000000-0000-0000-0000-000000000000
HTTP *
[Captures]
s55: status

GET {{candidate}}/api/explore/groups/home/cookbooks/00000000-0000-0000-0000-000000000000
HTTP *
[Asserts]
status == {{s55}}

GET http://127.0.0.1:9000/api/explore/groups/home/foods?page=1&perPage=5
HTTP *
[Captures]
s56: status

GET {{candidate}}/api/explore/groups/home/foods?page=1&perPage=5
HTTP *
[Asserts]
status == {{s56}}

GET http://127.0.0.1:9000/api/explore/groups/home/foods/cdbee04f-65ee-477e-bc0b-54a307619251
HTTP *
[Captures]
s57: status

GET {{candidate}}/api/explore/groups/home/foods/cdbee04f-65ee-477e-bc0b-54a307619251
HTTP *
[Asserts]
status == {{s57}}

GET http://127.0.0.1:9000/api/explore/groups/home/households?page=1&perPage=5
HTTP *
[Captures]
s58: status

GET {{candidate}}/api/explore/groups/home/households?page=1&perPage=5
HTTP *
[Asserts]
status == {{s58}}

GET http://127.0.0.1:9000/api/explore/groups/home/households/family
HTTP *
[Captures]
s59: status

GET {{candidate}}/api/explore/groups/home/households/family
HTTP *
[Asserts]
status == {{s59}}

GET http://127.0.0.1:9000/api/explore/groups/home/organizers/categories?page=1&perPage=5
HTTP *
[Captures]
s60: status

GET {{candidate}}/api/explore/groups/home/organizers/categories?page=1&perPage=5
HTTP *
[Asserts]
status == {{s60}}

GET http://127.0.0.1:9000/api/explore/groups/home/organizers/categories/d96b11f9-8382-4e7d-9494-d10bff0c1af3
HTTP *
[Captures]
s61: status

GET {{candidate}}/api/explore/groups/home/organizers/categories/d96b11f9-8382-4e7d-9494-d10bff0c1af3
HTTP *
[Asserts]
status == {{s61}}

GET http://127.0.0.1:9000/api/explore/groups/home/organizers/tags?page=1&perPage=5
HTTP *
[Captures]
s62: status

GET {{candidate}}/api/explore/groups/home/organizers/tags?page=1&perPage=5
HTTP *
[Asserts]
status == {{s62}}

GET http://127.0.0.1:9000/api/explore/groups/home/organizers/tags/2e738ff9-17f0-45b9-8821-eeb9996a83dd
HTTP *
[Captures]
s63: status

GET {{candidate}}/api/explore/groups/home/organizers/tags/2e738ff9-17f0-45b9-8821-eeb9996a83dd
HTTP *
[Asserts]
status == {{s63}}

GET http://127.0.0.1:9000/api/explore/groups/home/organizers/tools?page=1&perPage=5
HTTP *
[Captures]
s64: status

GET {{candidate}}/api/explore/groups/home/organizers/tools?page=1&perPage=5
HTTP *
[Asserts]
status == {{s64}}

GET http://127.0.0.1:9000/api/explore/groups/home/organizers/tools/00000000-0000-0000-0000-000000000000
HTTP *
[Captures]
s65: status

GET {{candidate}}/api/explore/groups/home/organizers/tools/00000000-0000-0000-0000-000000000000
HTTP *
[Asserts]
status == {{s65}}

GET http://127.0.0.1:9000/api/explore/groups/home/recipes?page=1&perPage=5
HTTP *
[Captures]
s66: status

GET {{candidate}}/api/explore/groups/home/recipes?page=1&perPage=5
HTTP *
[Asserts]
status == {{s66}}

GET http://127.0.0.1:9000/api/explore/groups/home/recipes/suggestions?limit=3
HTTP *
[Captures]
s67: status

GET {{candidate}}/api/explore/groups/home/recipes/suggestions?limit=3
HTTP *
[Asserts]
status == {{s67}}

GET http://127.0.0.1:9000/api/explore/groups/home/recipes/red-curry-chicken-and-rice-bowls
HTTP *
[Captures]
s68: status

GET {{candidate}}/api/explore/groups/home/recipes/red-curry-chicken-and-rice-bowls
HTTP *
[Asserts]
status == {{s68}}

GET http://127.0.0.1:9000/api/foods?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Captures]
s69: status

GET {{candidate}}/api/foods?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s69}}
jsonpath "$.per_page" exists
jsonpath "$.total_pages" exists

POST http://127.0.0.1:9000/api/foods
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s70: status

POST {{candidate}}/api/foods
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s70}}

PUT http://127.0.0.1:9000/api/foods/merge
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s71: status

PUT {{candidate}}/api/foods/merge
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s71}}

GET http://127.0.0.1:9000/api/foods/cdbee04f-65ee-477e-bc0b-54a307619251
Authorization: Bearer {{token}}
HTTP *
[Captures]
s72: status

GET {{candidate}}/api/foods/cdbee04f-65ee-477e-bc0b-54a307619251
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s72}}

PUT http://127.0.0.1:9000/api/foods/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s73: status

PUT {{candidate}}/api/foods/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s73}}

DELETE http://127.0.0.1:9000/api/foods/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Captures]
s74: status

DELETE {{candidate}}/api/foods/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s74}}

POST http://127.0.0.1:9000/api/groups/ai-providers/providers
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s75: status

POST {{candidate}}/api/groups/ai-providers/providers
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s75}}

POST http://127.0.0.1:9000/api/groups/ai-providers/providers/test
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s76: status

POST {{candidate}}/api/groups/ai-providers/providers/test
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s76}}

GET http://127.0.0.1:9000/api/groups/ai-providers/providers/533d1eb0-b65e-4e1d-a33d-b705bb5fe548
Authorization: Bearer {{token}}
HTTP *
[Captures]
s77: status

GET {{candidate}}/api/groups/ai-providers/providers/533d1eb0-b65e-4e1d-a33d-b705bb5fe548
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s77}}

PUT http://127.0.0.1:9000/api/groups/ai-providers/providers/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s78: status

PUT {{candidate}}/api/groups/ai-providers/providers/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s78}}

DELETE http://127.0.0.1:9000/api/groups/ai-providers/providers/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Captures]
s79: status

DELETE {{candidate}}/api/groups/ai-providers/providers/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s79}}

POST http://127.0.0.1:9000/api/groups/ai-providers/providers/00000000-0000-0000-0000-000000000000/test
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s80: status

POST {{candidate}}/api/groups/ai-providers/providers/00000000-0000-0000-0000-000000000000/test
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s80}}

GET http://127.0.0.1:9000/api/groups/ai-providers/settings
Authorization: Bearer {{token}}
HTTP *
[Captures]
s81: status

GET {{candidate}}/api/groups/ai-providers/settings
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s81}}

PUT http://127.0.0.1:9000/api/groups/ai-providers/settings
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s82: status

PUT {{candidate}}/api/groups/ai-providers/settings
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s82}}

GET http://127.0.0.1:9000/api/groups/households?page=1&perPage=10
Authorization: Bearer {{token}}
HTTP *
[Captures]
s83: status

GET {{candidate}}/api/groups/households?page=1&perPage=10
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s83}}
jsonpath "$.per_page" exists
jsonpath "$.total_pages" exists

GET http://127.0.0.1:9000/api/groups/households/family
Authorization: Bearer {{token}}
HTTP *
[Captures]
s84: status

GET {{candidate}}/api/groups/households/family
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s84}}

GET http://127.0.0.1:9000/api/groups/labels?page=1&perPage=10
Authorization: Bearer {{token}}
HTTP *
[Captures]
s85: status

GET {{candidate}}/api/groups/labels?page=1&perPage=10
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s85}}
jsonpath "$.per_page" exists
jsonpath "$.total_pages" exists

POST http://127.0.0.1:9000/api/groups/labels
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s86: status

POST {{candidate}}/api/groups/labels
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s86}}

GET http://127.0.0.1:9000/api/groups/labels/eed2f593-013a-441c-86cc-854a4ccb7477
Authorization: Bearer {{token}}
HTTP *
[Captures]
s87: status

GET {{candidate}}/api/groups/labels/eed2f593-013a-441c-86cc-854a4ccb7477
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s87}}

PUT http://127.0.0.1:9000/api/groups/labels/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s88: status

PUT {{candidate}}/api/groups/labels/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s88}}

DELETE http://127.0.0.1:9000/api/groups/labels/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Captures]
s89: status

DELETE {{candidate}}/api/groups/labels/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s89}}

GET http://127.0.0.1:9000/api/groups/members?page=1&perPage=10
Authorization: Bearer {{token}}
HTTP *
[Captures]
s90: status

GET {{candidate}}/api/groups/members?page=1&perPage=10
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s90}}
jsonpath "$.per_page" exists
jsonpath "$.total_pages" exists

GET http://127.0.0.1:9000/api/groups/members/bob
Authorization: Bearer {{token}}
HTTP *
[Captures]
s91: status

GET {{candidate}}/api/groups/members/bob
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s91}}

POST http://127.0.0.1:9000/api/groups/migrations
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s92: status

POST {{candidate}}/api/groups/migrations
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s92}}

GET http://127.0.0.1:9000/api/groups/preferences
Authorization: Bearer {{token}}
HTTP *
[Captures]
s93: status

GET {{candidate}}/api/groups/preferences
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s93}}

PUT http://127.0.0.1:9000/api/groups/preferences
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s94: status

PUT {{candidate}}/api/groups/preferences
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s94}}

GET http://127.0.0.1:9000/api/groups/reports
Authorization: Bearer {{token}}
HTTP *
[Captures]
s95: status

GET {{candidate}}/api/groups/reports
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s95}}

GET http://127.0.0.1:9000/api/groups/reports/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Captures]
s96: status

GET {{candidate}}/api/groups/reports/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s96}}

DELETE http://127.0.0.1:9000/api/groups/reports/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Captures]
s97: status

DELETE {{candidate}}/api/groups/reports/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s97}}

POST http://127.0.0.1:9000/api/groups/seeders/foods
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s98: status

POST {{candidate}}/api/groups/seeders/foods
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s98}}

POST http://127.0.0.1:9000/api/groups/seeders/units
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s99: status

POST {{candidate}}/api/groups/seeders/units
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s99}}

GET http://127.0.0.1:9000/api/groups/self
Authorization: Bearer {{token}}
HTTP *
[Captures]
s100: status

GET {{candidate}}/api/groups/self
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s100}}

GET http://127.0.0.1:9000/api/groups/storage
Authorization: Bearer {{token}}
HTTP *
[Captures]
s101: status

GET {{candidate}}/api/groups/storage
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s101}}

GET http://127.0.0.1:9000/api/households/cookbooks?page=1&perPage=10
Authorization: Bearer {{token}}
HTTP *
[Captures]
s102: status

GET {{candidate}}/api/households/cookbooks?page=1&perPage=10
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s102}}
jsonpath "$.per_page" exists
jsonpath "$.total_pages" exists

POST http://127.0.0.1:9000/api/households/cookbooks
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s103: status

POST {{candidate}}/api/households/cookbooks
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s103}}

PUT http://127.0.0.1:9000/api/households/cookbooks
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s104: status

PUT {{candidate}}/api/households/cookbooks
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s104}}

GET http://127.0.0.1:9000/api/households/cookbooks/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Captures]
s105: status

GET {{candidate}}/api/households/cookbooks/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s105}}

PUT http://127.0.0.1:9000/api/households/cookbooks/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s106: status

PUT {{candidate}}/api/households/cookbooks/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s106}}

DELETE http://127.0.0.1:9000/api/households/cookbooks/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Captures]
s107: status

DELETE {{candidate}}/api/households/cookbooks/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s107}}

GET http://127.0.0.1:9000/api/households/events/notifications?page=1&perPage=10
Authorization: Bearer {{token}}
HTTP *
[Captures]
s108: status

GET {{candidate}}/api/households/events/notifications?page=1&perPage=10
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s108}}
jsonpath "$.per_page" exists
jsonpath "$.total_pages" exists

POST http://127.0.0.1:9000/api/households/events/notifications
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s109: status

POST {{candidate}}/api/households/events/notifications
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s109}}

GET http://127.0.0.1:9000/api/households/events/notifications/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Captures]
s110: status

GET {{candidate}}/api/households/events/notifications/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s110}}

PUT http://127.0.0.1:9000/api/households/events/notifications/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s111: status

PUT {{candidate}}/api/households/events/notifications/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s111}}

DELETE http://127.0.0.1:9000/api/households/events/notifications/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Captures]
s112: status

DELETE {{candidate}}/api/households/events/notifications/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s112}}

POST http://127.0.0.1:9000/api/households/events/notifications/00000000-0000-0000-0000-000000000000/test
Authorization: Bearer {{token}}
HTTP *
[Captures]
s113: status

POST {{candidate}}/api/households/events/notifications/00000000-0000-0000-0000-000000000000/test
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s113}}

GET http://127.0.0.1:9000/api/households/invitations
Authorization: Bearer {{token}}
HTTP *
[Captures]
s114: status

GET {{candidate}}/api/households/invitations
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s114}}

POST http://127.0.0.1:9000/api/households/invitations
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s115: status

POST {{candidate}}/api/households/invitations
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s115}}

POST http://127.0.0.1:9000/api/households/invitations/email
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s116: status

POST {{candidate}}/api/households/invitations/email
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s116}}

GET http://127.0.0.1:9000/api/households/mealplans?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Captures]
s117: status

GET {{candidate}}/api/households/mealplans?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s117}}
jsonpath "$.per_page" exists
jsonpath "$.total_pages" exists

POST http://127.0.0.1:9000/api/households/mealplans
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s118: status

POST {{candidate}}/api/households/mealplans
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s118}}

POST http://127.0.0.1:9000/api/households/mealplans/random
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s119: status

POST {{candidate}}/api/households/mealplans/random
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s119}}

GET http://127.0.0.1:9000/api/households/mealplans/rules?page=1&perPage=10
Authorization: Bearer {{token}}
HTTP *
[Captures]
s120: status

GET {{candidate}}/api/households/mealplans/rules?page=1&perPage=10
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s120}}
jsonpath "$.per_page" exists
jsonpath "$.total_pages" exists

POST http://127.0.0.1:9000/api/households/mealplans/rules
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s121: status

POST {{candidate}}/api/households/mealplans/rules
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s121}}

GET http://127.0.0.1:9000/api/households/mealplans/rules/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Captures]
s122: status

GET {{candidate}}/api/households/mealplans/rules/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s122}}

PUT http://127.0.0.1:9000/api/households/mealplans/rules/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s123: status

PUT {{candidate}}/api/households/mealplans/rules/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s123}}

DELETE http://127.0.0.1:9000/api/households/mealplans/rules/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Captures]
s124: status

DELETE {{candidate}}/api/households/mealplans/rules/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s124}}

GET http://127.0.0.1:9000/api/households/mealplans/today
Authorization: Bearer {{token}}
HTTP *
[Captures]
s125: status

GET {{candidate}}/api/households/mealplans/today
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s125}}

GET http://127.0.0.1:9000/api/households/mealplans/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Captures]
s126: status

GET {{candidate}}/api/households/mealplans/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s126}}

PUT http://127.0.0.1:9000/api/households/mealplans/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s127: status

PUT {{candidate}}/api/households/mealplans/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s127}}

DELETE http://127.0.0.1:9000/api/households/mealplans/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Captures]
s128: status

DELETE {{candidate}}/api/households/mealplans/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s128}}

GET http://127.0.0.1:9000/api/households/members?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Captures]
s129: status

GET {{candidate}}/api/households/members?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s129}}

PUT http://127.0.0.1:9000/api/households/permissions
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s130: status

PUT {{candidate}}/api/households/permissions
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s130}}

GET http://127.0.0.1:9000/api/households/preferences
Authorization: Bearer {{token}}
HTTP *
[Captures]
s131: status

GET {{candidate}}/api/households/preferences
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s131}}

PUT http://127.0.0.1:9000/api/households/preferences
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s132: status

PUT {{candidate}}/api/households/preferences
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s132}}

GET http://127.0.0.1:9000/api/households/recipe-actions?page=1&perPage=10
Authorization: Bearer {{token}}
HTTP *
[Captures]
s133: status

GET {{candidate}}/api/households/recipe-actions?page=1&perPage=10
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s133}}
jsonpath "$.per_page" exists
jsonpath "$.total_pages" exists

POST http://127.0.0.1:9000/api/households/recipe-actions
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s134: status

POST {{candidate}}/api/households/recipe-actions
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s134}}

GET http://127.0.0.1:9000/api/households/recipe-actions/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Captures]
s135: status

GET {{candidate}}/api/households/recipe-actions/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s135}}

PUT http://127.0.0.1:9000/api/households/recipe-actions/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s136: status

PUT {{candidate}}/api/households/recipe-actions/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s136}}

DELETE http://127.0.0.1:9000/api/households/recipe-actions/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Captures]
s137: status

DELETE {{candidate}}/api/households/recipe-actions/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s137}}

POST http://127.0.0.1:9000/api/households/recipe-actions/00000000-0000-0000-0000-000000000000/trigger/parity-missing
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s138: status

POST {{candidate}}/api/households/recipe-actions/00000000-0000-0000-0000-000000000000/trigger/parity-missing
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s138}}

GET http://127.0.0.1:9000/api/households/self
Authorization: Bearer {{token}}
HTTP *
[Captures]
s139: status

GET {{candidate}}/api/households/self
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s139}}

GET http://127.0.0.1:9000/api/households/self/recipes/red-curry-chicken-and-rice-bowls
Authorization: Bearer {{token}}
HTTP *
[Captures]
s140: status

GET {{candidate}}/api/households/self/recipes/red-curry-chicken-and-rice-bowls
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s140}}

GET http://127.0.0.1:9000/api/households/shopping/items?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Captures]
s141: status

GET {{candidate}}/api/households/shopping/items?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s141}}
jsonpath "$.per_page" exists
jsonpath "$.total_pages" exists

POST http://127.0.0.1:9000/api/households/shopping/items
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s142: status

POST {{candidate}}/api/households/shopping/items
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s142}}

PUT http://127.0.0.1:9000/api/households/shopping/items
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s143: status

PUT {{candidate}}/api/households/shopping/items
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s143}}

DELETE http://127.0.0.1:9000/api/households/shopping/items?ids=00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Captures]
s144: status

DELETE {{candidate}}/api/households/shopping/items?ids=00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s144}}

POST http://127.0.0.1:9000/api/households/shopping/items/create-bulk
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s145: status

POST {{candidate}}/api/households/shopping/items/create-bulk
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s145}}

GET http://127.0.0.1:9000/api/households/shopping/items/82a8d703-5887-4d1e-bd18-52d92f8bc801
Authorization: Bearer {{token}}
HTTP *
[Captures]
s146: status

GET {{candidate}}/api/households/shopping/items/82a8d703-5887-4d1e-bd18-52d92f8bc801
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s146}}

PUT http://127.0.0.1:9000/api/households/shopping/items/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s147: status

PUT {{candidate}}/api/households/shopping/items/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s147}}

DELETE http://127.0.0.1:9000/api/households/shopping/items/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Captures]
s148: status

DELETE {{candidate}}/api/households/shopping/items/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s148}}

GET http://127.0.0.1:9000/api/households/shopping/lists?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Captures]
s149: status

GET {{candidate}}/api/households/shopping/lists?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s149}}
jsonpath "$.per_page" exists
jsonpath "$.total_pages" exists

POST http://127.0.0.1:9000/api/households/shopping/lists
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s150: status

POST {{candidate}}/api/households/shopping/lists
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s150}}

GET http://127.0.0.1:9000/api/households/shopping/lists/084c27c6-1aaf-46a7-ae4c-1e3cf13a5eb1
Authorization: Bearer {{token}}
HTTP *
[Captures]
s151: status

GET {{candidate}}/api/households/shopping/lists/084c27c6-1aaf-46a7-ae4c-1e3cf13a5eb1
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s151}}

PUT http://127.0.0.1:9000/api/households/shopping/lists/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s152: status

PUT {{candidate}}/api/households/shopping/lists/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s152}}

DELETE http://127.0.0.1:9000/api/households/shopping/lists/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Captures]
s153: status

DELETE {{candidate}}/api/households/shopping/lists/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s153}}

PUT http://127.0.0.1:9000/api/households/shopping/lists/00000000-0000-0000-0000-000000000000/label-settings
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s154: status

PUT {{candidate}}/api/households/shopping/lists/00000000-0000-0000-0000-000000000000/label-settings
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s154}}

POST http://127.0.0.1:9000/api/households/shopping/lists/00000000-0000-0000-0000-000000000000/recipe
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s155: status

POST {{candidate}}/api/households/shopping/lists/00000000-0000-0000-0000-000000000000/recipe
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s155}}

POST http://127.0.0.1:9000/api/households/shopping/lists/00000000-0000-0000-0000-000000000000/recipe/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s156: status

POST {{candidate}}/api/households/shopping/lists/00000000-0000-0000-0000-000000000000/recipe/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s156}}

POST http://127.0.0.1:9000/api/households/shopping/lists/00000000-0000-0000-0000-000000000000/recipe/00000000-0000-0000-0000-000000000000/delete
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s157: status

POST {{candidate}}/api/households/shopping/lists/00000000-0000-0000-0000-000000000000/recipe/00000000-0000-0000-0000-000000000000/delete
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s157}}

GET http://127.0.0.1:9000/api/households/statistics
Authorization: Bearer {{token}}
HTTP *
[Captures]
s158: status

GET {{candidate}}/api/households/statistics
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s158}}

GET http://127.0.0.1:9000/api/households/webhooks?page=1&perPage=10
Authorization: Bearer {{token}}
HTTP *
[Captures]
s159: status

GET {{candidate}}/api/households/webhooks?page=1&perPage=10
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s159}}
jsonpath "$.per_page" exists
jsonpath "$.total_pages" exists

POST http://127.0.0.1:9000/api/households/webhooks
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s160: status

POST {{candidate}}/api/households/webhooks
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s160}}

# Not executed: this call changes stored data or fires webhooks, and nothing in the request can make the handler reject it first.
POST http://127.0.0.1:9000/api/households/webhooks/rerun
Authorization: Bearer {{token}}
[Options]
skip: true
HTTP *

POST {{candidate}}/api/households/webhooks/rerun
Authorization: Bearer {{token}}
[Options]
skip: true
HTTP *

GET http://127.0.0.1:9000/api/households/webhooks/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Captures]
s162: status

GET {{candidate}}/api/households/webhooks/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s162}}

PUT http://127.0.0.1:9000/api/households/webhooks/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s163: status

PUT {{candidate}}/api/households/webhooks/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s163}}

DELETE http://127.0.0.1:9000/api/households/webhooks/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Captures]
s164: status

DELETE {{candidate}}/api/households/webhooks/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s164}}

POST http://127.0.0.1:9000/api/households/webhooks/00000000-0000-0000-0000-000000000000/test
Authorization: Bearer {{token}}
HTTP *
[Captures]
s165: status

POST {{candidate}}/api/households/webhooks/00000000-0000-0000-0000-000000000000/test
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s165}}

GET http://127.0.0.1:9000/api/media/docker/validate.txt
HTTP *
[Captures]
s166: status

GET {{candidate}}/api/media/docker/validate.txt
HTTP *
[Asserts]
status == {{s166}}

GET http://127.0.0.1:9000/api/media/recipes/f0b87c45-57e3-4a65-88c2-2ca7155f0b99/assets/unnamed-png.png
HTTP *
[Captures]
s167: status

GET {{candidate}}/api/media/recipes/f0b87c45-57e3-4a65-88c2-2ca7155f0b99/assets/unnamed-png.png
HTTP *
[Asserts]
status == {{s167}}

GET http://127.0.0.1:9000/api/media/recipes/60c6f805-d096-408f-a419-2c45a7d4e1bc/images/timeline/a15474ad-df50-42ac-b662-67c327d99586/original.webp
HTTP *
[Captures]
s168: status

GET {{candidate}}/api/media/recipes/60c6f805-d096-408f-a419-2c45a7d4e1bc/images/timeline/a15474ad-df50-42ac-b662-67c327d99586/original.webp
HTTP *
[Asserts]
status == {{s168}}

GET http://127.0.0.1:9000/api/media/recipes/f0b87c45-57e3-4a65-88c2-2ca7155f0b99/images/original.webp
HTTP *
[Captures]
s169: status

GET {{candidate}}/api/media/recipes/f0b87c45-57e3-4a65-88c2-2ca7155f0b99/images/original.webp
HTTP *
[Asserts]
status == {{s169}}

GET http://127.0.0.1:9000/api/media/users/506612c6-6f04-44e3-8e63-1850f7bd65fd/parity-missing.bin
HTTP *
[Captures]
s170: status

GET {{candidate}}/api/media/users/506612c6-6f04-44e3-8e63-1850f7bd65fd/parity-missing.bin
HTTP *
[Asserts]
status == {{s170}}

GET http://127.0.0.1:9000/api/organizers/categories?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Captures]
s171: status

GET {{candidate}}/api/organizers/categories?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s171}}
jsonpath "$.per_page" exists
jsonpath "$.total_pages" exists

POST http://127.0.0.1:9000/api/organizers/categories
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s172: status

POST {{candidate}}/api/organizers/categories
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s172}}

GET http://127.0.0.1:9000/api/organizers/categories/empty
Authorization: Bearer {{token}}
HTTP *
[Captures]
s173: status

GET {{candidate}}/api/organizers/categories/empty
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s173}}

POST http://127.0.0.1:9000/api/organizers/categories/merge
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s174: status

POST {{candidate}}/api/organizers/categories/merge
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s174}}

GET http://127.0.0.1:9000/api/organizers/categories/slug/grain-bowl
Authorization: Bearer {{token}}
HTTP *
[Captures]
s175: status

GET {{candidate}}/api/organizers/categories/slug/grain-bowl
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s175}}

GET http://127.0.0.1:9000/api/organizers/categories/d96b11f9-8382-4e7d-9494-d10bff0c1af3
Authorization: Bearer {{token}}
HTTP *
[Captures]
s176: status

GET {{candidate}}/api/organizers/categories/d96b11f9-8382-4e7d-9494-d10bff0c1af3
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s176}}

PUT http://127.0.0.1:9000/api/organizers/categories/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s177: status

PUT {{candidate}}/api/organizers/categories/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s177}}

DELETE http://127.0.0.1:9000/api/organizers/categories/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Captures]
s178: status

DELETE {{candidate}}/api/organizers/categories/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s178}}

GET http://127.0.0.1:9000/api/organizers/tags?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Captures]
s179: status

GET {{candidate}}/api/organizers/tags?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s179}}
jsonpath "$.per_page" exists
jsonpath "$.total_pages" exists

POST http://127.0.0.1:9000/api/organizers/tags
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s180: status

POST {{candidate}}/api/organizers/tags
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s180}}

GET http://127.0.0.1:9000/api/organizers/tags/empty
Authorization: Bearer {{token}}
HTTP *
[Captures]
s181: status

GET {{candidate}}/api/organizers/tags/empty
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s181}}

POST http://127.0.0.1:9000/api/organizers/tags/merge
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s182: status

POST {{candidate}}/api/organizers/tags/merge
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s182}}

GET http://127.0.0.1:9000/api/organizers/tags/slug/chicken-breast
Authorization: Bearer {{token}}
HTTP *
[Captures]
s183: status

GET {{candidate}}/api/organizers/tags/slug/chicken-breast
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s183}}

GET http://127.0.0.1:9000/api/organizers/tags/2e738ff9-17f0-45b9-8821-eeb9996a83dd
Authorization: Bearer {{token}}
HTTP *
[Captures]
s184: status

GET {{candidate}}/api/organizers/tags/2e738ff9-17f0-45b9-8821-eeb9996a83dd
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s184}}

PUT http://127.0.0.1:9000/api/organizers/tags/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s185: status

PUT {{candidate}}/api/organizers/tags/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s185}}

DELETE http://127.0.0.1:9000/api/organizers/tags/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Captures]
s186: status

DELETE {{candidate}}/api/organizers/tags/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s186}}

GET http://127.0.0.1:9000/api/organizers/tools?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Captures]
s187: status

GET {{candidate}}/api/organizers/tools?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s187}}
jsonpath "$.per_page" exists
jsonpath "$.total_pages" exists

POST http://127.0.0.1:9000/api/organizers/tools
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s188: status

POST {{candidate}}/api/organizers/tools
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s188}}

GET http://127.0.0.1:9000/api/organizers/tools/slug/parity-missing
Authorization: Bearer {{token}}
HTTP *
[Captures]
s189: status

GET {{candidate}}/api/organizers/tools/slug/parity-missing
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s189}}

GET http://127.0.0.1:9000/api/organizers/tools/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Captures]
s190: status

GET {{candidate}}/api/organizers/tools/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s190}}

PUT http://127.0.0.1:9000/api/organizers/tools/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s191: status

PUT {{candidate}}/api/organizers/tools/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s191}}

DELETE http://127.0.0.1:9000/api/organizers/tools/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Captures]
s192: status

DELETE {{candidate}}/api/organizers/tools/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s192}}

POST http://127.0.0.1:9000/api/parser/ingredient
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s193: status

POST {{candidate}}/api/parser/ingredient
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s193}}

POST http://127.0.0.1:9000/api/parser/ingredients
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s194: status

POST {{candidate}}/api/parser/ingredients
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s194}}

GET http://127.0.0.1:9000/api/recipes?page=1&perPage=3
Authorization: Bearer {{token}}
HTTP *
[Captures]
s195: status

GET {{candidate}}/api/recipes?page=1&perPage=3
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s195}}
jsonpath "$.per_page" exists
jsonpath "$.total_pages" exists

POST http://127.0.0.1:9000/api/recipes
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s196: status

POST {{candidate}}/api/recipes
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s196}}

PUT http://127.0.0.1:9000/api/recipes
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s197: status

PUT {{candidate}}/api/recipes
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s197}}

PATCH http://127.0.0.1:9000/api/recipes
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s198: status

PATCH {{candidate}}/api/recipes
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s198}}

POST http://127.0.0.1:9000/api/recipes/bulk-actions/categorize
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s199: status

POST {{candidate}}/api/recipes/bulk-actions/categorize
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s199}}

POST http://127.0.0.1:9000/api/recipes/bulk-actions/delete
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s200: status

POST {{candidate}}/api/recipes/bulk-actions/delete
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s200}}

GET http://127.0.0.1:9000/api/recipes/bulk-actions/export
Authorization: Bearer {{token}}
HTTP *
[Captures]
s201: status

GET {{candidate}}/api/recipes/bulk-actions/export
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s201}}

POST http://127.0.0.1:9000/api/recipes/bulk-actions/export
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s202: status

POST {{candidate}}/api/recipes/bulk-actions/export
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s202}}

# Not executed: this call changes stored data or fires webhooks, and nothing in the request can make the handler reject it first.
DELETE http://127.0.0.1:9000/api/recipes/bulk-actions/export/purge
Authorization: Bearer {{token}}
[Options]
skip: true
HTTP *

DELETE {{candidate}}/api/recipes/bulk-actions/export/purge
Authorization: Bearer {{token}}
[Options]
skip: true
HTTP *

GET http://127.0.0.1:9000/api/recipes/bulk-actions/export/00000000-0000-0000-0000-000000000000/download
Authorization: Bearer {{token}}
HTTP *
[Captures]
s204: status

GET {{candidate}}/api/recipes/bulk-actions/export/00000000-0000-0000-0000-000000000000/download
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s204}}

POST http://127.0.0.1:9000/api/recipes/bulk-actions/settings
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s205: status

POST {{candidate}}/api/recipes/bulk-actions/settings
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s205}}

POST http://127.0.0.1:9000/api/recipes/bulk-actions/tag
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s206: status

POST {{candidate}}/api/recipes/bulk-actions/tag
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s206}}

# Not executed: every field is optional, so a request starts an AI recipe import.
POST http://127.0.0.1:9000/api/recipes/create/ai
Authorization: Bearer {{token}}
[Options]
skip: true
HTTP *

POST {{candidate}}/api/recipes/create/ai
Authorization: Bearer {{token}}
[Options]
skip: true
HTTP *

# Not executed: every field is optional, so a request starts an AI recipe import.
POST http://127.0.0.1:9000/api/recipes/create/ai/stream
Authorization: Bearer {{token}}
[Options]
skip: true
HTTP *

POST {{candidate}}/api/recipes/create/ai/stream
Authorization: Bearer {{token}}
[Options]
skip: true
HTTP *

POST http://127.0.0.1:9000/api/recipes/create/html-or-json
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s209: status

POST {{candidate}}/api/recipes/create/html-or-json
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s209}}

POST http://127.0.0.1:9000/api/recipes/create/html-or-json/stream
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s210: status

POST {{candidate}}/api/recipes/create/html-or-json/stream
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s210}}

POST http://127.0.0.1:9000/api/recipes/create/image
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s211: status

POST {{candidate}}/api/recipes/create/image
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s211}}

POST http://127.0.0.1:9000/api/recipes/create/url
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s212: status

POST {{candidate}}/api/recipes/create/url
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s212}}

POST http://127.0.0.1:9000/api/recipes/create/url/bulk
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s213: status

POST {{candidate}}/api/recipes/create/url/bulk
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s213}}

POST http://127.0.0.1:9000/api/recipes/create/url/stream
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s214: status

POST {{candidate}}/api/recipes/create/url/stream
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s214}}

POST http://127.0.0.1:9000/api/recipes/create/zip
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s215: status

POST {{candidate}}/api/recipes/create/zip
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s215}}

GET http://127.0.0.1:9000/api/recipes/exports
Authorization: Bearer {{token}}
HTTP *
[Captures]
s216: status

GET {{candidate}}/api/recipes/exports
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s216}}

GET http://127.0.0.1:9000/api/recipes/shared/00000000-0000-0000-0000-000000000000
HTTP *
[Captures]
s217: status

GET {{candidate}}/api/recipes/shared/00000000-0000-0000-0000-000000000000
HTTP *
[Asserts]
status == {{s217}}

GET http://127.0.0.1:9000/api/recipes/shared/00000000-0000-0000-0000-000000000000/zip
HTTP *
[Captures]
s218: status

GET {{candidate}}/api/recipes/shared/00000000-0000-0000-0000-000000000000/zip
HTTP *
[Asserts]
status == {{s218}}

GET http://127.0.0.1:9000/api/recipes/suggestions?limit=3
Authorization: Bearer {{token}}
HTTP *
[Captures]
s219: status

GET {{candidate}}/api/recipes/suggestions?limit=3
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s219}}

POST http://127.0.0.1:9000/api/recipes/test-scrape-url
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s220: status

POST {{candidate}}/api/recipes/test-scrape-url
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s220}}

GET http://127.0.0.1:9000/api/recipes/timeline/events?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Captures]
s221: status

GET {{candidate}}/api/recipes/timeline/events?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s221}}
jsonpath "$.per_page" exists
jsonpath "$.total_pages" exists

POST http://127.0.0.1:9000/api/recipes/timeline/events
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s222: status

POST {{candidate}}/api/recipes/timeline/events
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s222}}

GET http://127.0.0.1:9000/api/recipes/timeline/events/a15474ad-df50-42ac-b662-67c327d99586
Authorization: Bearer {{token}}
HTTP *
[Captures]
s223: status

GET {{candidate}}/api/recipes/timeline/events/a15474ad-df50-42ac-b662-67c327d99586
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s223}}

PUT http://127.0.0.1:9000/api/recipes/timeline/events/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s224: status

PUT {{candidate}}/api/recipes/timeline/events/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s224}}

DELETE http://127.0.0.1:9000/api/recipes/timeline/events/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Captures]
s225: status

DELETE {{candidate}}/api/recipes/timeline/events/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s225}}

PUT http://127.0.0.1:9000/api/recipes/timeline/events/00000000-0000-0000-0000-000000000000/image
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s226: status

PUT {{candidate}}/api/recipes/timeline/events/00000000-0000-0000-0000-000000000000/image
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s226}}

GET http://127.0.0.1:9000/api/recipes/red-curry-chicken-and-rice-bowls
Authorization: Bearer {{token}}
HTTP *
[Captures]
s227: status

GET {{candidate}}/api/recipes/red-curry-chicken-and-rice-bowls
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s227}}

PUT http://127.0.0.1:9000/api/recipes/parity-missing
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s228: status

PUT {{candidate}}/api/recipes/parity-missing
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s228}}

PATCH http://127.0.0.1:9000/api/recipes/parity-missing
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s229: status

PATCH {{candidate}}/api/recipes/parity-missing
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s229}}

DELETE http://127.0.0.1:9000/api/recipes/parity-missing
Authorization: Bearer {{token}}
HTTP *
[Captures]
s230: status

DELETE {{candidate}}/api/recipes/parity-missing
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s230}}

POST http://127.0.0.1:9000/api/recipes/parity-missing/assets
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s231: status

POST {{candidate}}/api/recipes/parity-missing/assets
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s231}}

POST http://127.0.0.1:9000/api/recipes/parity-missing/assets/url
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s232: status

POST {{candidate}}/api/recipes/parity-missing/assets/url
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s232}}

GET http://127.0.0.1:9000/api/recipes/red-curry-chicken-and-rice-bowls/comments
Authorization: Bearer {{token}}
HTTP *
[Captures]
s233: status

GET {{candidate}}/api/recipes/red-curry-chicken-and-rice-bowls/comments
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s233}}

POST http://127.0.0.1:9000/api/recipes/parity-missing/duplicate
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s234: status

POST {{candidate}}/api/recipes/parity-missing/duplicate
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s234}}

GET http://127.0.0.1:9000/api/recipes/red-curry-chicken-and-rice-bowls/exports
Authorization: Bearer {{token}}
HTTP *
[Captures]
s235: status

GET {{candidate}}/api/recipes/red-curry-chicken-and-rice-bowls/exports
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s235}}

POST http://127.0.0.1:9000/api/recipes/parity-missing/image
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s236: status

POST {{candidate}}/api/recipes/parity-missing/image
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s236}}

PUT http://127.0.0.1:9000/api/recipes/parity-missing/image
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s237: status

PUT {{candidate}}/api/recipes/parity-missing/image
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s237}}

DELETE http://127.0.0.1:9000/api/recipes/parity-missing/image
Authorization: Bearer {{token}}
HTTP *
[Captures]
s238: status

DELETE {{candidate}}/api/recipes/parity-missing/image
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s238}}

PATCH http://127.0.0.1:9000/api/recipes/parity-missing/last-made
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s239: status

PATCH {{candidate}}/api/recipes/parity-missing/last-made
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s239}}

GET http://127.0.0.1:9000/api/shared/recipes?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Captures]
s240: status

GET {{candidate}}/api/shared/recipes?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s240}}
jsonpath "$.items" not exists

POST http://127.0.0.1:9000/api/shared/recipes
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s241: status

POST {{candidate}}/api/shared/recipes
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s241}}

GET http://127.0.0.1:9000/api/shared/recipes/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Captures]
s242: status

GET {{candidate}}/api/shared/recipes/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s242}}

DELETE http://127.0.0.1:9000/api/shared/recipes/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Captures]
s243: status

DELETE {{candidate}}/api/shared/recipes/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s243}}

GET http://127.0.0.1:9000/api/units?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Captures]
s244: status

GET {{candidate}}/api/units?page=1&perPage=5
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s244}}
jsonpath "$.per_page" exists
jsonpath "$.total_pages" exists

POST http://127.0.0.1:9000/api/units
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s245: status

POST {{candidate}}/api/units
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s245}}

PUT http://127.0.0.1:9000/api/units/merge
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s246: status

PUT {{candidate}}/api/units/merge
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s246}}

GET http://127.0.0.1:9000/api/units/30349c46-b64d-4243-826c-dd849f441b6b
Authorization: Bearer {{token}}
HTTP *
[Captures]
s247: status

GET {{candidate}}/api/units/30349c46-b64d-4243-826c-dd849f441b6b
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s247}}

PUT http://127.0.0.1:9000/api/units/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s248: status

PUT {{candidate}}/api/units/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s248}}

DELETE http://127.0.0.1:9000/api/units/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Captures]
s249: status

DELETE {{candidate}}/api/units/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s249}}

GET http://127.0.0.1:9000/api/users/api-tokens
Authorization: Bearer {{token}}
HTTP *
[Captures]
s250: status

GET {{candidate}}/api/users/api-tokens
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s250}}

POST http://127.0.0.1:9000/api/users/api-tokens
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s251: status

POST {{candidate}}/api/users/api-tokens
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s251}}

DELETE http://127.0.0.1:9000/api/users/api-tokens/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Captures]
s252: status

DELETE {{candidate}}/api/users/api-tokens/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s252}}

POST http://127.0.0.1:9000/api/users/forgot-password
Content-Type: application/json
0
HTTP *
[Captures]
s253: status

POST {{candidate}}/api/users/forgot-password
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s253}}

PUT http://127.0.0.1:9000/api/users/password
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s254: status

PUT {{candidate}}/api/users/password
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s254}}

POST http://127.0.0.1:9000/api/users/register
Content-Type: application/json
0
HTTP *
[Captures]
s255: status

POST {{candidate}}/api/users/register
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s255}}

POST http://127.0.0.1:9000/api/users/reset-password
Content-Type: application/json
0
HTTP *
[Captures]
s256: status

POST {{candidate}}/api/users/reset-password
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s256}}

GET http://127.0.0.1:9000/api/users/self
Authorization: Bearer {{token}}
HTTP *
[Captures]
s257: status

GET {{candidate}}/api/users/self
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s257}}
jsonpath "$.authMethod" == "Mealie"

GET http://127.0.0.1:9000/api/users/self/favorites
Authorization: Bearer {{token}}
HTTP *
[Captures]
s258: status

GET {{candidate}}/api/users/self/favorites
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s258}}

GET http://127.0.0.1:9000/api/users/self/ratings
Authorization: Bearer {{token}}
HTTP *
[Captures]
s259: status

GET {{candidate}}/api/users/self/ratings
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s259}}

GET http://127.0.0.1:9000/api/users/self/ratings/60c6f805-d096-408f-a419-2c45a7d4e1bc
Authorization: Bearer {{token}}
HTTP *
[Captures]
s260: status

GET {{candidate}}/api/users/self/ratings/60c6f805-d096-408f-a419-2c45a7d4e1bc
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s260}}

GET http://127.0.0.1:9000/api/users/506612c6-6f04-44e3-8e63-1850f7bd65fd/favorites
Authorization: Bearer {{token}}
HTTP *
[Captures]
s261: status

GET {{candidate}}/api/users/506612c6-6f04-44e3-8e63-1850f7bd65fd/favorites
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s261}}

POST http://127.0.0.1:9000/api/users/00000000-0000-0000-0000-000000000000/favorites/parity-missing
Authorization: Bearer {{token}}
HTTP *
[Captures]
s262: status

POST {{candidate}}/api/users/00000000-0000-0000-0000-000000000000/favorites/parity-missing
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s262}}

DELETE http://127.0.0.1:9000/api/users/00000000-0000-0000-0000-000000000000/favorites/parity-missing
Authorization: Bearer {{token}}
HTTP *
[Captures]
s263: status

DELETE {{candidate}}/api/users/00000000-0000-0000-0000-000000000000/favorites/parity-missing
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s263}}

POST http://127.0.0.1:9000/api/users/00000000-0000-0000-0000-000000000000/image
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s264: status

POST {{candidate}}/api/users/00000000-0000-0000-0000-000000000000/image
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s264}}

GET http://127.0.0.1:9000/api/users/506612c6-6f04-44e3-8e63-1850f7bd65fd/ratings
Authorization: Bearer {{token}}
HTTP *
[Captures]
s265: status

GET {{candidate}}/api/users/506612c6-6f04-44e3-8e63-1850f7bd65fd/ratings
Authorization: Bearer {{token}}
HTTP *
[Asserts]
status == {{s265}}

POST http://127.0.0.1:9000/api/users/00000000-0000-0000-0000-000000000000/ratings/parity-missing
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s266: status

POST {{candidate}}/api/users/00000000-0000-0000-0000-000000000000/ratings/parity-missing
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s266}}

PUT http://127.0.0.1:9000/api/users/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Captures]
s267: status

PUT {{candidate}}/api/users/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{token}}
Content-Type: application/json
0
HTTP *
[Asserts]
status == {{s267}}

GET http://127.0.0.1:9000/api/utils/download
HTTP *
[Captures]
s268: status

GET {{candidate}}/api/utils/download
HTTP *
[Asserts]
status == {{s268}}

GET http://127.0.0.1:9000/api/validators/group?name=nobody-accuracy-check
HTTP *
[Captures]
s269: status

GET {{candidate}}/api/validators/group?name=nobody-accuracy-check
HTTP *
[Asserts]
status == {{s269}}

GET http://127.0.0.1:9000/api/validators/household?name=nobody-accuracy-check
HTTP *
[Captures]
s270: status

GET {{candidate}}/api/validators/household?name=nobody-accuracy-check
HTTP *
[Asserts]
status == {{s270}}

GET http://127.0.0.1:9000/api/validators/recipe?group_id=dcf19c89-e7aa-470c-9707-deaf30cb5c45&name=nobody-accuracy-check
HTTP *
[Captures]
s271: status

GET {{candidate}}/api/validators/recipe?group_id=dcf19c89-e7aa-470c-9707-deaf30cb5c45&name=nobody-accuracy-check
HTTP *
[Asserts]
status == {{s271}}

GET http://127.0.0.1:9000/api/validators/user/email?email=nobody-accuracy-check@example.com
HTTP *
[Captures]
s272: status

GET {{candidate}}/api/validators/user/email?email=nobody-accuracy-check@example.com
HTTP *
[Asserts]
status == {{s272}}

GET http://127.0.0.1:9000/api/validators/user/name?name=nobody-accuracy-check
HTTP *
[Captures]
s273: status

GET {{candidate}}/api/validators/user/name?name=nobody-accuracy-check
HTTP *
[Asserts]
status == {{s273}}
