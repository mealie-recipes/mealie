from dataclasses import dataclass
from enum import StrEnum


class LocaleTextDirection(StrEnum):
    LTR = "ltr"
    RTL = "rtl"


class LocalePluralFoodHandling(StrEnum):
    ALWAYS = "always"
    WITHOUT_UNIT = "without-unit"
    NEVER = "never"


@dataclass
class LocaleConfig:
    name: str
    dir: LocaleTextDirection = LocaleTextDirection.LTR
    plural_food_handling: LocalePluralFoodHandling = LocalePluralFoodHandling.ALWAYS


LOCALE_CONFIG: dict[str, LocaleConfig] = {
    "af-ZA": LocaleConfig(name="Afrikaans (Afrikaans)"),
    "ar-SA": LocaleConfig(name="العربية (Arabic)", dir=LocaleTextDirection.RTL),
    "bg-BG": LocaleConfig(name="Български (Bulgarian)"),
    "ca-ES": LocaleConfig(name="Català (Catalan)"),
    "cs-CZ": LocaleConfig(name="Čeština (Czech)"),
    "da-DK": LocaleConfig(name="Dansk (Danish)"),
    "de-DE": LocaleConfig(name="Deutsch (German)"),
    "el-GR": LocaleConfig(name="Ελληνικά (Greek)"),
    "en-GB": LocaleConfig(name="British English", plural_food_handling=LocalePluralFoodHandling.WITHOUT_UNIT),
    "en-US": LocaleConfig(name="American English", plural_food_handling=LocalePluralFoodHandling.WITHOUT_UNIT),
    "es-ES": LocaleConfig(name="Español (Spanish)"),
    "et-EE": LocaleConfig(name="Eesti (Estonian)"),
    "fi-FI": LocaleConfig(name="Suomi (Finnish)"),
    "fr-BE": LocaleConfig(name="Belge (Belgian)"),
    "fr-CA": LocaleConfig(name="Français canadien (Canadian French)"),
    "fr-FR": LocaleConfig(name="Français (French)"),
    "gl-ES": LocaleConfig(name="Galego (Galician)"),
    "he-IL": LocaleConfig(name="עברית (Hebrew)", dir=LocaleTextDirection.RTL),
    "hr-HR": LocaleConfig(name="Hrvatski (Croatian)"),
    "hu-HU": LocaleConfig(name="Magyar (Hungarian)"),
    "is-IS": LocaleConfig(name="Íslenska (Icelandic)"),
    "it-IT": LocaleConfig(name="Italiano (Italian)"),
    "ja-JP": LocaleConfig(name="日本語 (Japanese)", plural_food_handling=LocalePluralFoodHandling.NEVER),
    "ko-KR": LocaleConfig(name="한국어 (Korean)", plural_food_handling=LocalePluralFoodHandling.NEVER),
    "lt-LT": LocaleConfig(name="Lietuvių (Lithuanian)"),
    "lv-LV": LocaleConfig(name="Latviešu (Latvian)"),
    "nl-NL": LocaleConfig(name="Nederlands (Dutch)"),
    "no-NO": LocaleConfig(name="Norsk (Norwegian)"),
    "pl-PL": LocaleConfig(name="Polski (Polish)"),
    "pt-BR": LocaleConfig(name="Português do Brasil (Brazilian Portuguese)"),
    "pt-PT": LocaleConfig(name="Português (Portuguese)"),
    "ro-RO": LocaleConfig(name="Română (Romanian)"),
    "ru-RU": LocaleConfig(name="Pусский (Russian)"),
    "sk-SK": LocaleConfig(name="Slovenčina (Slovak)"),
    "sl-SI": LocaleConfig(name="Slovenščina (Slovenian)"),
    "sr-SP": LocaleConfig(name="српски (Serbian)"),
    "sv-SE": LocaleConfig(name="Svenska (Swedish)"),
    "tr-TR": LocaleConfig(name="Türkçe (Turkish)", plural_food_handling=LocalePluralFoodHandling.NEVER),
    "uk-UA": LocaleConfig(name="Українська (Ukrainian)"),
    "vi-VN": LocaleConfig(name="Tiếng Việt (Vietnamese)", plural_food_handling=LocalePluralFoodHandling.NEVER),
    "zh-CN": LocaleConfig(name="简体中文 (Chinese simplified)", plural_food_handling=LocalePluralFoodHandling.NEVER),
    "zh-TW": LocaleConfig(name="繁體中文 (Chinese traditional)", plural_food_handling=LocalePluralFoodHandling.NEVER),
}
