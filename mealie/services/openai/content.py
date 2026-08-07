import bs4


def extract_json_ld_data_from_html(soup: bs4.BeautifulSoup) -> str:
    data_parts: list[str] = []
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            script_data = script.string
            if script_data:
                data_parts.append(str(script_data))
        except AttributeError:
            pass

    return "\n\n".join(data_parts)


def find_image(soup: bs4.BeautifulSoup) -> str | None:
    # find the open graph image tag
    og_image = soup.find("meta", property="og:image")
    if og_image and og_image.get("content"):
        return og_image["content"]

    # find the largest image on the page
    largest_img = None
    max_size = 0
    for img in soup.find_all("img"):
        width = img.get("width", 0)
        height = img.get("height", 0)
        if not width or not height:
            continue

        try:
            size = int(width) * int(height)
        except (ValueError, TypeError):
            size = 1
        if size > max_size:
            max_size = size
            largest_img = img

    if largest_img:
        return largest_img.get("src")

    return None


def extract_page_content(html: str) -> tuple[str, str | None]:
    """
    Strips an HTML document down to its text content, with any ld+json data appended,
    along with the page's primary image, if one can be found.

    Raises if the document contains neither text nor ld+json data.
    """

    soup = bs4.BeautifulSoup(html, "lxml")

    text = soup.get_text(separator="\n", strip=True)
    text += extract_json_ld_data_from_html(soup)
    if not text:
        raise ValueError("No text or ld+json data found in HTML")

    try:
        image = find_image(soup)
    except Exception:
        image = None

    return text, image


def format_html_to_text(html: str) -> str:
    """Builds an AI prompt message out of a webpage's text content and its primary image, if found."""

    text, image = extract_page_content(html)

    components = [f"Convert this content to JSON: {text}"]
    if image:
        components.append(f"Recipe Image: {image}")
    return "\n".join(components)
