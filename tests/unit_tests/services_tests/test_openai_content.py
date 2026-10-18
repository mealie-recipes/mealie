import json

import pytest

from mealie.services.openai.content import extract_page_content, is_facebook_url


def facebook_page(video_id: str = "123", caption: str = "Mix flour and milk, then bake.") -> str:
    data = {
        "require": [["Relay", {"data": {"video": {"id": video_id, "creation_story": {"message": {"text": caption}}}}}]],
        "related": {"id": "456", "creation_story": {"message": {"text": "Unrelated recipe"}}},
    }
    return (
        '<meta property="og:url" content="https://www.facebook.com/reel/123/">'
        '<meta property="og:description" content="Mix flour...">'
        '<meta property="og:image" content="https://example.com/recipe.jpg">'
        '<script type="application/json">broken JSON</script>'
        f'<script type="application/json">{json.dumps(data)}</script><body>Facebook</body>'
    )


@pytest.mark.parametrize(
    "canonical",
    [
        "https://www.facebook.com/reel/123/",
        "https://m.facebook.com/reel/123?share=1",
        "https://facebook.com/user/videos/a-recipe/123/",
        "https://www.facebook.com/watch/?v=123",
    ],
)
def test_extract_full_facebook_caption(canonical: str):
    caption = "Chicken Alfredo 🧀\n1 cup Gruyère\nMix, then bake."
    html = facebook_page(caption=caption).replace("https://www.facebook.com/reel/123/", canonical)
    text, image = extract_page_content(html)

    assert text.startswith(caption)
    assert "Unrelated recipe" not in text
    assert image == "https://example.com/recipe.jpg"


@pytest.mark.parametrize("video_id", ["456", "999"])
def test_only_extract_current_facebook_video(video_id: str):
    text, _ = extract_page_content(facebook_page(video_id=video_id))
    assert text == "Facebook"


@pytest.mark.parametrize("host", ["example.com", "facebook.com.evil.example"])
def test_only_read_facebook_hydration_data(host: str):
    html = facebook_page().replace("www.facebook.com", host)
    text, _ = extract_page_content(html)
    assert text == "Facebook"


def test_malformed_facebook_story_does_not_break_page_text():
    html = facebook_page().replace('"message": {"text": "Mix flour and milk, then bake."}', '"message": null')
    assert extract_page_content(html)[0] == "Facebook"


def test_normal_page_text_and_json_ld_are_preserved():
    html = '<p>Mix and bake.</p><script type="application/ld+json">{"@type":"Recipe"}</script>'
    text, _ = extract_page_content(html)
    assert "Mix and bake." in text
    assert '{"@type":"Recipe"}' in text


def test_plain_text_is_preserved():
    assert extract_page_content("Mix flour and water.")[0] == "Mix flour and water."


def test_invalid_canonical_url_does_not_break_page_text():
    html = facebook_page().replace("https://www.facebook.com/reel/123/", "https://[invalid")
    assert extract_page_content(html)[0] == "Facebook"


@pytest.mark.parametrize("url", ["https://[invalid", "https://facebook.com.evil.example/reel/123", ""])
def test_invalid_or_unrelated_url_is_not_facebook(url: str):
    assert not is_facebook_url(url)
