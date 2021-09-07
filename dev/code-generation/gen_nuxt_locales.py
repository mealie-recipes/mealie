from pathlib import Path

from _gen_utils import inject_inline
from _static import CodeKeys

PROJECT_DIR = Path(__file__).parent.parent.parent


datetime_dir = PROJECT_DIR / "frontend" / "lang" / "dateTimeFormats"
locales_dir = PROJECT_DIR / "frontend" / "lang" / "messages"
nuxt_config = PROJECT_DIR / "frontend" / "nuxt.config.js"

"""
This snippet walks the message and dat locales directories and generates the import information
for the nuxt.config.js file and automatically injects it into the nuxt.config.js file. Note that
the code generation ID is hardcoded into the script and required in the nuxt config.
"""


def main():  # sourcery skip: list-comprehension
    print("Starting...")

    all_date_locales = []
    for match in datetime_dir.glob("*.json"):
        all_date_locales.append(f'"{match.stem}": require("./lang/dateTimeFormats/{match.name}"),')

    all_langs = []
    for match in locales_dir.glob("*.json"):
        lang_string = f'{{ code: "{match.stem}", file: "{match.name}" }},'
        all_langs.append(lang_string)

    inject_inline(nuxt_config, CodeKeys.nuxt_local_messages, all_langs)
    inject_inline(nuxt_config, CodeKeys.nuxt_local_dates, all_date_locales)

    print("Finished...")


if __name__ == "__main__":
    main()
