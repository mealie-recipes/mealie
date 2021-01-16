import json

import requests

POST_URL = "http://localhost:9921/api/site-settings/themes/create/"
GET_URL = "http://localhost:9921/api/site-settings/themes/"

SITE_SETTINGS = [
    {
        "name": "default",
        "colors": {
            "primary": "#E58325",
            "accent": "#00457A",
            "secondary": "#973542",
            "success": "#5AB1BB",
            "info": "#FFFD99",
            "warning": "#FF4081",
            "error": "#EF5350",
        },
    },
    {
        "name": "purple",
        "colors": {
            "accent": "#4527A0",
            "primary": "#FF4081",
            "secondary": "#26C6DA",
            "success": "#4CAF50",
            "info": "#2196F3",
            "warning": "#FB8C00",
            "error": "#FF5252",
        },
    },
]

if __name__ == "__main__":
    for theme in SITE_SETTINGS:
        data = json.dumps(theme)
        response = requests.post(POST_URL, data)
        response = requests.get(GET_URL)
