class AppRoutes:
    def __init__(self) -> None:
        self.prefix = "/api"

        self.auth_token = "/api/auth/token"
        self.auth_token_long = "/api/auth/token/long"
        self.auth_refresh = "/api/auth/refresh"
        self.users_sign_ups = "/api/users/sign-ups"
        self.users = "/api/users"
        self.users_self = "/api/users/self"
        self.users_api_tokens = "/api/users/api-tokens"
        self.groups = "/api/groups"
        self.groups_self = "/api/groups/self"
        self.recipes_summary = "/api/recipes/summary"
        self.recipes_summary_untagged = "/api/recipes/summary/untagged"
        self.recipes_summary_uncategorized = "/api/recipes/summary/uncategorized"
        self.recipes_category = "/api/recipes/category"
        self.recipes_tag = "/api/recipes/tag"
        self.recipes_create = "/api/recipes/create"
        self.recipes_create_url = "/api/recipes/create-url"
        self.categories = "/api/categories"
        self.categories_empty = "/api/categories/empty"
        self.tags = "/api/tags"
        self.tags_empty = "/api/tags/empty"
        self.about_events = "/api/about/events"
        self.meal_plans_all = "/api/meal-plans/all"
        self.meal_plans_create = "/api/meal-plans/create"
        self.meal_plans_this_week = "/api/meal-plans/this-week"
        self.meal_plans_today = "/api/meal-plans/today"
        self.meal_plans_today_image = "/api/meal-plans/today/image"
        self.site_settings_custom_pages = "/api/site-settings/custom-pages"
        self.site_settings = "/api/site-settings"
        self.site_settings_webhooks_test = "/api/site-settings/webhooks/test"
        self.themes = "/api/themes"
        self.themes_create = "/api/themes/create"
        self.backups_available = "/api/backups/available"
        self.backups_export_database = "/api/backups/export/database"
        self.backups_upload = "/api/backups/upload"
        self.migrations = "/api/migrations"
        self.debug = "/api/debug"
        self.debug_statistics = "/api/debug/statistics"
        self.debug_version = "/api/debug/version"
        self.debug_last_recipe_json = "/api/debug/last-recipe-json"
        self.debug_log = "/api/debug/log"
        self.utils_download = "/api/utils/download"

    def users_sign_ups_token(self, token):
        return f"{self.prefix}/users/sign-ups/{token}"

    def users_id(self, id):
        return f"{self.prefix}/users/{id}"

    def users_id_reset_password(self, id):
        return f"{self.prefix}/users/{id}/reset-password"

    def users_id_image(self, id):
        return f"{self.prefix}/users/{id}/image"

    def users_id_password(self, id):
        return f"{self.prefix}/users/{id}/password"

    def users_api_tokens_token_id(self, token_id):
        return f"{self.prefix}/users/api-tokens/{token_id}"

    def groups_id(self, id):
        return f"{self.prefix}/groups/{id}"

    def recipes_recipe_slug(self, recipe_slug):
        return f"{self.prefix}/recipes/{recipe_slug}"

    def recipes_recipe_slug_image(self, recipe_slug):
        return f"{self.prefix}/recipes/{recipe_slug}/image"

    def recipes_recipe_slug_assets(self, recipe_slug):
        return f"{self.prefix}/recipes/{recipe_slug}/assets"

    def categories_category(self, category):
        return f"{self.prefix}/categories/{category}"

    def tags_tag(self, tag):
        return f"{self.prefix}/tags/{tag}"

    def media_recipes_recipe_slug_images_file_name(self, recipe_slug, file_name):
        return f"{self.prefix}/media/recipes/{recipe_slug}/images/{file_name}"

    def media_recipes_recipe_slug_assets_file_name(self, recipe_slug, file_name):
        return f"{self.prefix}/media/recipes/{recipe_slug}/assets/{file_name}"

    def about_events_id(self, id):
        return f"{self.prefix}/about/events/{id}"

    def meal_plans_plan_id(self, plan_id):
        return f"{self.prefix}/meal-plans/{plan_id}"

    def meal_plans_id_shopping_list(self, id):
        return f"{self.prefix}/meal-plans/{id}/shopping-list"

    def site_settings_custom_pages_id(self, id):
        return f"{self.prefix}/site-settings/custom-pages/{id}"

    def themes_id(self, id):
        return f"{self.prefix}/themes/{id}"

    def backups_file_name_download(self, file_name):
        return f"{self.prefix}/backups/{file_name}/download"

    def backups_file_name_import(self, file_name):
        return f"{self.prefix}/backups/{file_name}/import"

    def backups_file_name_delete(self, file_name):
        return f"{self.prefix}/backups/{file_name}/delete"

    def migrations_import_type_file_name_import(self, import_type, file_name):
        return f"{self.prefix}/migrations/{import_type}/{file_name}/import"

    def migrations_import_type_file_name_delete(self, import_type, file_name):
        return f"{self.prefix}/migrations/{import_type}/{file_name}/delete"

    def migrations_import_type_upload(self, import_type):
        return f"{self.prefix}/migrations/{import_type}/upload"

    def debug_log_num(self, num):
        return f"{self.prefix}/debug/log/{num}"
