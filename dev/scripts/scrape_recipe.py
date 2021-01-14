"""
Helper script to download raw recipe data from a URL and dump it to disk.
The resulting files can be used as test input data.
"""

import sys, json, pprint
import requests
import extruct
from scrape_schema_recipe import scrape_url
from w3lib.html import get_base_url

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
        print("Trying extruct instead")
        pp = pprint.PrettyPrinter(indent=2)
        r = requests.get(url)
        base_url = get_base_url(r.text, r.url)
        data = extruct.extract(r.text, base_url=base_url)
        pp.pprint(data)
