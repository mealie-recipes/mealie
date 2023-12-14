from bs4 import BeautifulSoup

from mealie.routes.spa import MetaTag, inject_meta, inject_recipe_json
from tests import data as test_data
from tests.utils.factories import random_string


def test_spa_metadata_injection():
    fp = test_data.html_mealie_recipe
    with open(fp) as f:
        soup = BeautifulSoup(f, "lxml")
        assert soup.html and soup.html.head

        tags = soup.find_all("meta")
        assert tags

        title_tag = None
        for tag in tags:
            if tag.get("data-hid") == "og:title":
                title_tag = tag
                break

        assert title_tag and title_tag["content"]

        new_title_tag = MetaTag(hid="og:title", property_name="og:title", content=random_string())
        new_arbitrary_tag = MetaTag(hid=random_string(), property_name=random_string(), content=random_string())
        new_html = inject_meta(str(soup), [new_title_tag, new_arbitrary_tag])

    # verify changes were injected
    soup = BeautifulSoup(new_html, "lxml")
    assert soup.html and soup.html.head

    tags = soup.find_all("meta")
    assert tags

    title_tag = None
    for tag in tags:
        if tag.get("data-hid") == "og:title":
            title_tag = tag
            break

    assert title_tag and title_tag["content"] == new_title_tag.content

    arbitrary_tag = None
    for tag in tags:
        if tag.get("data-hid") == new_arbitrary_tag.hid:
            arbitrary_tag = tag
            break

    assert arbitrary_tag and arbitrary_tag["content"] == new_arbitrary_tag.content


def test_spa_recipe_json_injection():
    recipe_name = random_string()
    schema = {
        "@context": "https://schema.org",
        "@type": "Recipe",
        "name": recipe_name,
    }

    fp = test_data.html_mealie_recipe
    with open(fp) as f:
        soup = BeautifulSoup(f, "lxml")
        assert "https://schema.org" not in str(soup)

        html = inject_recipe_json(str(soup), schema)

    assert "@context" in html
    assert "https://schema.org" in html
    assert recipe_name in html
