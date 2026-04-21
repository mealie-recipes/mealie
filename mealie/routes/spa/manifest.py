import json
from urllib.parse import urlparse

from fastapi import Response

from mealie.core.config import get_app_settings


def serve_manifest():
    settings = get_app_settings()
    sub_path = urlparse(settings.BASE_URL).path or "/"

    manifest = {
        "name": "Mealie",
        "short_name": "Mealie",
        "id": "/",
        "start_url": sub_path,
        "scope": sub_path,
        "display": "standalone",
        "background_color": "#1E1E1E",
        "theme_color": settings.theme.light_primary,
        "description": "Mealie is a recipe management and meal planning app",
        "lang": "en",
        "display_override": ["standalone", "minimal-ui", "browser", "window-controls-overlay"],
        "categories": ["food", "lifestyle"],
        "prefer_related_applications": False,
        "handle_links": "preferred",
        "launch_handler": {"client_mode": ["focus-existing", "auto"]},
        "edge_side_panel": {"preferred_width": 400},
        "share_target": {
            "action": "/r/create/url",
            "method": "GET",
            "enctype": "application/x-www-form-urlencoded",
            "params": {"text": "recipe_import_url"},
        },
        "icons": [
            {"src": "/icons/android-chrome-192x192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
            {"src": "/icons/android-chrome-512x512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
            {
                "src": "/icons/android-chrome-maskable-192x192.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "maskable",
            },
            {
                "src": "/icons/android-chrome-maskable-512x512.png",
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "maskable",
            },
        ],
        "screenshots": [
            {
                "src": "/screenshots/home-narrow.png",
                "sizes": "1600x2420",
                "form_factor": "narrow",
                "label": "Home Page",
            },
            {
                "src": "/screenshots/recipe-narrow.png",
                "sizes": "1600x2420",
                "form_factor": "narrow",
                "label": "Recipe Page",
            },
            {
                "src": "/screenshots/editor-narrow.png",
                "sizes": "1600x2420",
                "form_factor": "narrow",
                "label": "Editor Page",
            },
            {
                "src": "/screenshots/parser-narrow.png",
                "sizes": "1600x2420",
                "form_factor": "narrow",
                "label": "Parser Page",
            },
            {"src": "/screenshots/home-wide.png", "sizes": "2560x1460", "form_factor": "wide", "label": "Home Page"},
            {
                "src": "/screenshots/recipe-wide.png",
                "sizes": "2560x1460",
                "form_factor": "wide",
                "label": "Recipe Page",
            },
            {
                "src": "/screenshots/editor-wide.png",
                "sizes": "2560x1460",
                "form_factor": "wide",
                "label": "Editor Page",
            },
            {
                "src": "/screenshots/parser-wide.png",
                "sizes": "2560x1460",
                "form_factor": "wide",
                "label": "Parser Page",
            },
        ],
        "shortcuts": [
            {
                "name": "Shopping Lists",
                "short_name": "Shopping Lists",
                "description": "Open the shopping lists",
                "url": "/shopping-lists",
                "icons": [
                    {"src": "/icons/mdiFormatListChecks-192x192.png", "sizes": "192x192"},
                    {"src": "/icons/mdiFormatListChecks-96x96.png", "sizes": "96x96"},
                ],
            },
            {
                "name": "Meal Planner",
                "short_name": "Meal Planner",
                "description": "Open the meal planner",
                "url": "/household/mealplan/planner/view",
                "icons": [
                    {"src": "/icons/mdiCalendarMultiselect-192x192.png", "sizes": "192x192"},
                    {"src": "/icons/mdiCalendarMultiselect-96x96.png", "sizes": "96x96"},
                ],
            },
        ],
    }

    return Response(
        content=json.dumps(manifest),
        media_type="application/manifest+json",
        headers={"Cache-Control": "no-cache"},
    )
