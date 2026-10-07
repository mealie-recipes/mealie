<?php

namespace App\Areas\AuthUsers\Http;

use App\Areas\AuthUsers\Support\Settings;
use App\Areas\AuthUsers\Support\Users;
use App\Support\Json;
use Illuminate\Http\JsonResponse;

/** mealie/routes/app/app_about.py */
class AppController
{
    /** GET /app/about — get_app_info */
    public function about(): JsonResponse
    {
        $db = Users::db();
        $groupSlug = null;
        $householdSlug = null;

        $group = $db->table('groups')->where('name', Settings::defaultGroup())->first();
        if ($group) {
            $prefs = $db->table('group_preferences')->where('group_id', $group->id)->first();
            if ($prefs && ! $prefs->private_group) {
                $groupSlug = $group->slug;
            }
        }
        if ($group && $groupSlug) {
            $household = $db->table('households')->where('name', Settings::defaultHousehold())->where('group_id', $group->id)->first();
            if ($household) {
                $prefs = $db->table('household_preferences')->where('household_id', $household->id)->first();
                if ($prefs && ! $prefs->private_household) {
                    $householdSlug = $household->slug;
                }
            }
        }

        return Json::respond([
            'production' => Settings::production(),
            'version' => 'develop',
            'demoStatus' => Settings::isDemo(),
            'allowSignup' => Settings::allowSignup(),
            'allowPasswordLogin' => Settings::allowPasswordLogin(),
            'defaultGroupSlug' => $groupSlug,
            'defaultHouseholdSlug' => $householdSlug,
            'enableOidc' => Settings::oidcReady(),
            'oidcRedirect' => Settings::bool('OIDC_AUTO_REDIRECT', false),
            'oidcProviderName' => Settings::str('OIDC_PROVIDER_NAME', 'OAuth'),
            'tokenTime' => Settings::tokenTime(),
            'allowedIframeHosts' => Settings::allowedIframeHosts(),
        ]);
    }

    /** GET /app/about/startup-info — get_startup_info */
    public function startupInfo(): JsonResponse
    {
        return Json::respond([
            'isFirstLogin' => Users::db()->table('users')->where('email', 'changeme@example.com')->exists(),
            'isDemo' => Settings::isDemo(),
        ]);
    }

    /** GET /app/about/theme — get_app_theme */
    public function theme(): JsonResponse
    {
        $out = [];
        foreach (Settings::theme() as $key => $value) {
            $out[Json::camel($key)] = $value;
        }

        return Json::respond($out)->header('Cache-Control', 'public, max-age=604800');
    }
}
