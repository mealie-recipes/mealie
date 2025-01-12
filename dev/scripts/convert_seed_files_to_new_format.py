import glob
import json
import pathlib


def get_seed_locale_names() -> set[str]:
    """Find all locales in the seed/resources/ folder

    Returns:
        A set of every file name where there's both a seed label and seed food file
    """

    LABELS_PATH = "/workspaces/mealie/mealie/repos/seed/resources/labels/locales/"
    FOODS_PATH = "/workspaces/mealie/mealie/repos/seed/resources/foods/locales/"
    label_locales = glob.glob("*.json", root_dir=LABELS_PATH)
    foods_locales = glob.glob("*.json", root_dir=FOODS_PATH)

    # ensure that a locale has both a label and a food seed file
    return set(label_locales).intersection(foods_locales)


def get_labels_from_file(locale: str) -> list[str]:
    """Query a locale to get all of the labels so that they can be added to the new foods seed format

    Returns:
        All of the labels found within the seed file for a given locale
    """

    locale_path = pathlib.Path("/workspaces/mealie/mealie/repos/seed/resources/labels/locales/" + locale)
    label_names = [label["name"] for label in json.loads(locale_path.read_text(encoding="utf-8"))]
    return label_names


def transform_foods(locale: str):
    """
    Convert the current food seed file for a locale into a new format which maps each food to a label

    Existing format of foods seed file is a dictionary where each key is a food name and the values are a dictionary
        of attributes such as name and plural_name

    New format maps each food to a label. The top-level dictionary has each key as a label e.g. "Fruits".
        Each label key as a value that is a dictionary with an element called "foods"
        "Foods" is a dictionary of each food for that label, with a key of the english food name e.g. "baking-soda"
        and a value of attributes, including the translated name of the item e.g. "bicarbonate of soda" for en-GB.
    """

    locale_path = pathlib.Path("/workspaces/mealie/mealie/repos/seed/resources/foods/locales/" + locale)

    with open(locale_path, encoding="utf-8") as infile:
        data = json.load(infile)

    transformed_data = {"": {"foods": dict(data.items())}}

    # Seeding for labels now pulls from the foods file and parses the labels from there (as top-level keys),
    #   thus we need to add all of the existing labels to the new food seed file and give them an empty foods dictionary
    label_names = get_labels_from_file(locale)
    for label in label_names:
        transformed_data[label] = {"foods": {}}

    with open(locale_path, "w", encoding="utf-8") as outfile:
        json.dump(transformed_data, outfile, indent=4, ensure_ascii=False)


def main():
    for locale in get_seed_locale_names():
        transform_foods(locale)


if __name__ == "__main__":
    main()
