from mealie.services.scraper.cleaner import Cleaner


def test_clean_category():
    assert Cleaner.category("my-category") == ["my-category"]


def test_clean_html():
    assert Cleaner.html("<div>Hello World</div>") == "Hello World"
