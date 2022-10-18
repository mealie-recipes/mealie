# This Content is Auto Generated for Pytest


class AppRoutes:
    def __init__(self) -> None:
        self.prefix = "/api"

        self.admin_about = "/api/admin/about"
        self.admin_about_check = "/api/admin/about/check"
        self.admin_about_docker_validate = "/api/admin/about/docker/validate"
        self.admin_about_statistics = "/api/admin/about/statistics"
        self.admin_analytics = "/api/admin/analytics"
        self.admin_backups = "/api/admin/backups"
        self.admin_backups_upload = "/api/admin/backups/upload"
        self.admin_email = "/api/admin/email"
        self.admin_groups = "/api/admin/groups"
        self.admin_logs = "/api/admin/logs"
        self.admin_maintenance = "/api/admin/maintenance"
        self.admin_maintenance_clean_images = "/api/admin/maintenance/clean/images"
        self.admin_maintenance_clean_logs = "/api/admin/maintenance/clean/logs"
        self.admin_maintenance_clean_recipe_folders = "/api/admin/maintenance/clean/recipe-folders"
        self.admin_maintenance_clean_temp = "/api/admin/maintenance/clean/temp"
        self.admin_maintenance_logs = "/api/admin/maintenance/logs"
        self.admin_maintenance_storage = "/api/admin/maintenance/storage"
        self.admin_server_tasks = "/api/admin/server-tasks"
        self.admin_users = "/api/admin/users"
        self.admin_users_unlock = "/api/admin/users/unlock"
        self.app_about = "/api/app/about"
        self.auth_refresh = "/api/auth/refresh"
        self.auth_token = "/api/auth/token"
        self.comments = "/api/comments"
        self.foods = "/api/foods"
        self.foods_merge = "/api/foods/merge"
        self.groups_categories = "/api/groups/categories"
        self.groups_cookbooks = "/api/groups/cookbooks"
        self.groups_events_notifications = "/api/groups/events/notifications"
        self.groups_invitations = "/api/groups/invitations"
        self.groups_invitations_email = "/api/groups/invitations/email"
        self.groups_labels = "/api/groups/labels"
        self.groups_mealplans = "/api/groups/mealplans"
        self.groups_mealplans_random = "/api/groups/mealplans/random"
        self.groups_mealplans_rules = "/api/groups/mealplans/rules"
        self.groups_mealplans_today = "/api/groups/mealplans/today"
        self.groups_members = "/api/groups/members"
        self.groups_migrations = "/api/groups/migrations"
        self.groups_permissions = "/api/groups/permissions"
        self.groups_preferences = "/api/groups/preferences"
        self.groups_reports = "/api/groups/reports"
        self.groups_seeders_foods = "/api/groups/seeders/foods"
        self.groups_seeders_labels = "/api/groups/seeders/labels"
        self.groups_seeders_units = "/api/groups/seeders/units"
        self.groups_self = "/api/groups/self"
        self.groups_shopping_items = "/api/groups/shopping/items"
        self.groups_shopping_lists = "/api/groups/shopping/lists"
        self.groups_statistics = "/api/groups/statistics"
        self.groups_storage = "/api/groups/storage"
        self.groups_webhooks = "/api/groups/webhooks"
        self.groups_webhooks_rerun = "/api/groups/webhooks/rerun"
        self.media_docker_validate_txt = "/api/media/docker/validate.txt"
        self.ocr = "/api/ocr/"
        self.ocr_asset_to_tsv = "/api/ocr/asset-to-tsv"
        self.ocr_file_to_tsv = "/api/ocr/file-to-tsv"
        self.organizers_categories = "/api/organizers/categories"
        self.organizers_categories_empty = "/api/organizers/categories/empty"
        self.organizers_tags = "/api/organizers/tags"
        self.organizers_tags_empty = "/api/organizers/tags/empty"
        self.organizers_tools = "/api/organizers/tools"
        self.parser_ingredient = "/api/parser/ingredient"
        self.parser_ingredients = "/api/parser/ingredients"
        self.recipes = "/api/recipes"
        self.recipes_bulk_actions_categorize = "/api/recipes/bulk-actions/categorize"
        self.recipes_bulk_actions_delete = "/api/recipes/bulk-actions/delete"
        self.recipes_bulk_actions_export = "/api/recipes/bulk-actions/export"
        self.recipes_bulk_actions_export_download = "/api/recipes/bulk-actions/export/download"
        self.recipes_bulk_actions_export_purge = "/api/recipes/bulk-actions/export/purge"
        self.recipes_bulk_actions_settings = "/api/recipes/bulk-actions/settings"
        self.recipes_bulk_actions_tag = "/api/recipes/bulk-actions/tag"
        self.recipes_create_from_zip = "/api/recipes/create-from-zip"
        self.recipes_create_ocr = "/api/recipes/create-ocr"
        self.recipes_create_url = "/api/recipes/create-url"
        self.recipes_create_url_bulk = "/api/recipes/create-url/bulk"
        self.recipes_exports = "/api/recipes/exports"
        self.recipes_summary_uncategorized = "/api/recipes/summary/uncategorized"
        self.recipes_summary_untagged = "/api/recipes/summary/untagged"
        self.recipes_test_scrape_url = "/api/recipes/test-scrape-url"
        self.shared_recipes = "/api/shared/recipes"
        self.units = "/api/units"
        self.units_merge = "/api/units/merge"
        self.users = "/api/users"
        self.users_api_tokens = "/api/users/api-tokens"
        self.users_forgot_password = "/api/users/forgot-password"
        self.users_password = "/api/users/password"
        self.users_register = "/api/users/register"
        self.users_reset_password = "/api/users/reset-password"
        self.users_self = "/api/users/self"
        self.utils_download = "/api/utils/download"
        self.validators_group = "/api/validators/group"
        self.validators_recipe = "/api/validators/recipe"
        self.validators_user_email = "/api/validators/user/email"
        self.validators_user_name = "/api/validators/user/name"

    def admin_backups_file_name(self, file_name):
        """`/admin/backups/{file_name}`"""
        return f"{self.prefix}/admin/backups/{file_name}"

    def admin_backups_file_name_restore(self, file_name):
        """`/admin/backups/{file_name}/restore`"""
        return f"{self.prefix}/admin/backups/{file_name}/restore"

    def admin_groups_item_id(self, item_id):
        """`/admin/groups/{item_id}`"""
        return f"{self.prefix}/admin/groups/{item_id}"

    def admin_logs_num(self, num):
        """`/admin/logs/{num}`"""
        return f"{self.prefix}/admin/logs/{num}"

    def admin_users_item_id(self, item_id):
        """`/admin/users/{item_id}`"""
        return f"{self.prefix}/admin/users/{item_id}"

    def comments_item_id(self, item_id):
        """`/comments/{item_id}`"""
        return f"{self.prefix}/comments/{item_id}"

    def explore_recipes_group_id_recipe_slug(self, group_id, recipe_slug):
        """`/explore/recipes/{group_id}/{recipe_slug}`"""
        return f"{self.prefix}/explore/recipes/{group_id}/{recipe_slug}"

    def foods_item_id(self, item_id):
        """`/foods/{item_id}`"""
        return f"{self.prefix}/foods/{item_id}"

    def groups_cookbooks_item_id(self, item_id):
        """`/groups/cookbooks/{item_id}`"""
        return f"{self.prefix}/groups/cookbooks/{item_id}"

    def groups_events_notifications_item_id(self, item_id):
        """`/groups/events/notifications/{item_id}`"""
        return f"{self.prefix}/groups/events/notifications/{item_id}"

    def groups_events_notifications_item_id_test(self, item_id):
        """`/groups/events/notifications/{item_id}/test`"""
        return f"{self.prefix}/groups/events/notifications/{item_id}/test"

    def groups_labels_item_id(self, item_id):
        """`/groups/labels/{item_id}`"""
        return f"{self.prefix}/groups/labels/{item_id}"

    def groups_mealplans_item_id(self, item_id):
        """`/groups/mealplans/{item_id}`"""
        return f"{self.prefix}/groups/mealplans/{item_id}"

    def groups_mealplans_rules_item_id(self, item_id):
        """`/groups/mealplans/rules/{item_id}`"""
        return f"{self.prefix}/groups/mealplans/rules/{item_id}"

    def groups_reports_item_id(self, item_id):
        """`/groups/reports/{item_id}`"""
        return f"{self.prefix}/groups/reports/{item_id}"

    def groups_shopping_items_item_id(self, item_id):
        """`/groups/shopping/items/{item_id}`"""
        return f"{self.prefix}/groups/shopping/items/{item_id}"

    def groups_shopping_lists_item_id(self, item_id):
        """`/groups/shopping/lists/{item_id}`"""
        return f"{self.prefix}/groups/shopping/lists/{item_id}"

    def groups_shopping_lists_item_id_recipe_recipe_id(self, item_id, recipe_id):
        """`/groups/shopping/lists/{item_id}/recipe/{recipe_id}`"""
        return f"{self.prefix}/groups/shopping/lists/{item_id}/recipe/{recipe_id}"

    def groups_webhooks_item_id(self, item_id):
        """`/groups/webhooks/{item_id}`"""
        return f"{self.prefix}/groups/webhooks/{item_id}"

    def media_recipes_recipe_id_assets_file_name(self, recipe_id, file_name):
        """`/media/recipes/{recipe_id}/assets/{file_name}`"""
        return f"{self.prefix}/media/recipes/{recipe_id}/assets/{file_name}"

    def media_recipes_recipe_id_images_file_name(self, recipe_id, file_name):
        """`/media/recipes/{recipe_id}/images/{file_name}`"""
        return f"{self.prefix}/media/recipes/{recipe_id}/images/{file_name}"

    def media_users_user_id_file_name(self, user_id, file_name):
        """`/media/users/{user_id}/{file_name}`"""
        return f"{self.prefix}/media/users/{user_id}/{file_name}"

    def organizers_categories_item_id(self, item_id):
        """`/organizers/categories/{item_id}`"""
        return f"{self.prefix}/organizers/categories/{item_id}"

    def organizers_categories_slug_category_slug(self, category_slug):
        """`/organizers/categories/slug/{category_slug}`"""
        return f"{self.prefix}/organizers/categories/slug/{category_slug}"

    def organizers_tags_item_id(self, item_id):
        """`/organizers/tags/{item_id}`"""
        return f"{self.prefix}/organizers/tags/{item_id}"

    def organizers_tags_slug_tag_slug(self, tag_slug):
        """`/organizers/tags/slug/{tag_slug}`"""
        return f"{self.prefix}/organizers/tags/slug/{tag_slug}"

    def organizers_tools_item_id(self, item_id):
        """`/organizers/tools/{item_id}`"""
        return f"{self.prefix}/organizers/tools/{item_id}"

    def organizers_tools_slug_tool_slug(self, tool_slug):
        """`/organizers/tools/slug/{tool_slug}`"""
        return f"{self.prefix}/organizers/tools/slug/{tool_slug}"

    def recipes_shared_token_id(self, token_id):
        """`/recipes/shared/{token_id}`"""
        return f"{self.prefix}/recipes/shared/{token_id}"

    def recipes_slug(self, slug):
        """`/recipes/{slug}`"""
        return f"{self.prefix}/recipes/{slug}"

    def recipes_slug_assets(self, slug):
        """`/recipes/{slug}/assets`"""
        return f"{self.prefix}/recipes/{slug}/assets"

    def recipes_slug_comments(self, slug):
        """`/recipes/{slug}/comments`"""
        return f"{self.prefix}/recipes/{slug}/comments"

    def recipes_slug_exports(self, slug):
        """`/recipes/{slug}/exports`"""
        return f"{self.prefix}/recipes/{slug}/exports"

    def recipes_slug_exports_zip(self, slug):
        """`/recipes/{slug}/exports/zip`"""
        return f"{self.prefix}/recipes/{slug}/exports/zip"

    def recipes_slug_image(self, slug):
        """`/recipes/{slug}/image`"""
        return f"{self.prefix}/recipes/{slug}/image"

    def shared_recipes_item_id(self, item_id):
        """`/shared/recipes/{item_id}`"""
        return f"{self.prefix}/shared/recipes/{item_id}"

    def units_item_id(self, item_id):
        """`/units/{item_id}`"""
        return f"{self.prefix}/units/{item_id}"

    def users_api_tokens_token_id(self, token_id):
        """`/users/api-tokens/{token_id}`"""
        return f"{self.prefix}/users/api-tokens/{token_id}"

    def users_id_favorites(self, id):
        """`/users/{id}/favorites`"""
        return f"{self.prefix}/users/{id}/favorites"

    def users_id_favorites_slug(self, id, slug):
        """`/users/{id}/favorites/{slug}`"""
        return f"{self.prefix}/users/{id}/favorites/{slug}"

    def users_id_image(self, id):
        """`/users/{id}/image`"""
        return f"{self.prefix}/users/{id}/image"

    def users_item_id(self, item_id):
        """`/users/{item_id}`"""
        return f"{self.prefix}/users/{item_id}"
