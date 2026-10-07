<?php

namespace App\Areas\GroupsAdmin\Controllers;

use App\Areas\GroupsAdmin\Support\Db;
use App\Areas\GroupsAdmin\Support\Settings;
use App\Support\Json;

/** mealie/routes/admin/admin_about.py and admin_email.py (GET only) */
class AdminAboutController
{
    /** GET /admin/about/statistics */
    public function statistics()
    {
        return Json::respond([
            'totalRecipes' => Db::table('recipes')->count(),
            'totalUsers' => Db::table('users')->count(),
            'totalHouseholds' => Db::table('households')->count(),
            'totalGroups' => Db::table('groups')->count(),
            // `RecipeModel.recipe_category == None` on a many-to-many renders as NOT EXISTS
            'uncategorizedRecipes' => Db::table('recipes')->whereNotExists(fn ($q) => $q->selectRaw('1')->from('recipes_to_categories')->whereColumn('recipes_to_categories.recipe_id', 'recipes.id'))->count(),
            'untaggedRecipes' => Db::table('recipes')->whereNotExists(fn ($q) => $q->selectRaw('1')->from('recipes_to_tags')->whereColumn('recipes_to_tags.recipe_id', 'recipes.id'))->count(),
        ]);
    }

    /** GET /admin/about/check */
    public function check()
    {
        $version = Settings::appVersion();

        return Json::respond([
            'emailReady' => Settings::smtpEnabled(),
            'ldapReady' => Settings::ldapEnabled(),
            'ldapDisabled' => ! Settings::bool('LDAP_AUTH_ENABLED', false),
            'oidcReady' => Settings::oidcReady(),
            'oidcDisabled' => ! Settings::bool('OIDC_AUTH_ENABLED', false),
            'baseUrlSet' => Settings::baseUrl() !== 'http://localhost:8080',
            // anything but develop/nightly needs the GitHub release check (outside service)
            'isUpToDate' => in_array($version, ['develop', 'nightly'], true),
        ]);
    }

    /** GET /admin/email */
    public function email()
    {
        return Json::respond(['ready' => Settings::smtpEnabled()]);
    }
}
