from pathlib import Path
from pprint import pprint

PROJECT_DIR = Path(__file__).parent.parent.parent


datetime_dir = PROJECT_DIR / "frontend" / "lang" / "dateTimeFormats"
locales_dir = PROJECT_DIR / "datetime" / "lang" / "messages"


"""
{
    code: "en-US",
    file: "en-US.json",
}

"en-US": require("./lang/dateTimeFormats/en-US.json"),

"""


def main():
    print("Starting...")

    all_langs = []
    for match in datetime_dir.glob("*.json"):
        print(f'"{match.stem}": require("./lang/dateTimeFormats/{match.name}"),')

        all_langs.append({"code": match.stem, "file": match.name})

    print("\n\n\n--------- All Languages -----------")
    pprint(all_langs)

    print("Finished...")


if __name__ == "__main__":
    main()
