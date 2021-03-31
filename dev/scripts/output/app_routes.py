class AppRoutes:
    def __init__(self) -> None:
        self.prefix = "/api"

        self.users_sign_ups = "/api/users/sign-ups"
        self.auth_token = "/api/auth/token"
        self.auth_token_long = "/api/auth/token/long"
        self.auth_refresh = "/api/auth/refresh"
        self.users = "/api/users"
        self.users_self = "/api/users/self"
        self.groups = "/api/groups"
        self.groups_self = "/api/groups/self"
        self.recipes = "/api/recipes"
        self.recipes_category = "/api/recipes/category"
        self.recipes_tag = "/api/recipes/tag"
        self.categories = "/api/categories"
        self.recipes_tags = "/api/recipes/tags/"
        self.recipes_create = "/api/recipes/create"
        self.recipes_create_url = "/api/recipes/create-url"
        self.meal_plans_all = "/api/meal-plans/all"
        self.meal_plans_create = "/api/meal-plans/create"
        self.meal_plans_this_week = "/api/meal-plans/this-week"
        self.meal_plans_today = "/api/meal-plans/today"
        self.site_settings_custom_pages = "/api/site-settings/custom-pages"
        self.site_settings = "/api/site-settings"
        self.site_settings_webhooks_test = "/api/site-settings/webhooks/test"
        self.themes = "/api/themes"
        self.themes_create = "/api/themes/create"
        self.backups_available = "/api/backups/available"
        self.backups_export_database = "/api/backups/export/database"
        self.backups_upload = "/api/backups/upload"
        self.migrations = "/api/migrations"
        self.debug_version = "/api/debug/version"
        self.debug_last_recipe_json = "/api/debug/last-recipe-json"

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

    def groups_id(self, id):
        return f"{self.prefix}/groups/{id}"

    def categories_category(self, category):
        return f"{self.prefix}/categories/{category}"

    def recipes_tags_tag(self, tag):
        return f"{self.prefix}/recipes/tags/{tag}"

    def recipes_recipe_slug(self, recipe_slug):
        return f"{self.prefix}/recipes/{recipe_slug}"

    def recipes_recipe_slug_image(self, recipe_slug):
        return f"{self.prefix}/recipes/{recipe_slug}/image"

    def meal_plans_plan_id(self, plan_id):
        return f"{self.prefix}/meal-plans/{plan_id}"

    def meal_plans_id_shopping_list(self, id):
        return f"{self.prefix}/meal-plans/{id}/shopping-list"

    def site_settings_custom_pages_id(self, id):
        return f"{self.prefix}/site-settings/custom-pages/{id}"

    def themes_theme_name(self, theme_name):
        return f"{self.prefix}/themes/{theme_name}"

    def backups_file_name_download(self, file_name):
        return f"{self.prefix}/backups/{file_name}/download"

    def backups_file_name_import(self, file_name):
        return f"{self.prefix}/backups/{file_name}/import"

    def backups_file_name_delete(self, file_name):
        return f"{self.prefix}/backups/{file_name}/delete"

    def migrations_type_file_name_import(self, type, file_name):
        return f"{self.prefix}/migrations/{type}/{file_name}/import"

    def migrations_type_file_name_delete(self, type, file_name):
        return f"{self.prefix}/migrations/{type}/{file_name}/delete"

    def migrations_type_upload(self, type):
        return f"{self.prefix}/migrations/{type}/upload"

    def debug_log_num(self, num):
        return f"{self.prefix}/debug/log/{num}"
