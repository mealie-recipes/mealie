"""
Helper script to download raw recipe data from a URL and dump it to disk.
The resulting files can be used as test input data.
"""

import sys, json
from scrape_schema_recipe import scrape_url

for url in sys.argv[1:]:
    try:
        data = scrape_url(url)[0]
        slug = list(filter(None, url.split("/")))[-1]
        filename = f"{slug}.json"
        with open(filename, "w") as f:
            json.dump(data, f, indent=4, default=str)
        print(f"Saved {filename}")
    except Exception as e:
        print(f"Error for {url}: {e}")
