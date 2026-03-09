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
    key: str
    name: str
    dir: LocaleTextDirection = LocaleTextDirection.LTR
    plural_food_handling: LocalePluralFoodHandling = LocalePluralFoodHandling.ALWAYS


LOCALE_CONFIG: dict[str, LocaleConfig] = {
    "af-ZA": LocaleConfig(key="af-ZA", name="Afrikaans (Afrikaans)"),
    "ar-SA": LocaleConfig(key="ar-SA", name="العربية (Arabic)", dir=LocaleTextDirection.RTL),
    "bg-BG": LocaleConfig(key="bg-BG", name="Български (Bulgarian)"),
    "ca-ES": LocaleConfig(key="ca-ES", name="Català (Catalan)"),
    "cs-CZ": LocaleConfig(key="cs-CZ", name="Čeština (Czech)"),
    "da-DK": LocaleConfig(key="da-DK", name="Dansk (Danish)"),
    "de-DE": LocaleConfig(key="de-DE", name="Deutsch (German)"),
    "el-GR": LocaleConfig(key="el-GR", name="Ελληνικά (Greek)"),
    "en-GB": LocaleConfig(
        key="en-GB", name="British English", plural_food_handling=LocalePluralFoodHandling.WITHOUT_UNIT
    ),
    "en-US": LocaleConfig(
        key="en-US", name="American English", plural_food_handling=LocalePluralFoodHandling.WITHOUT_UNIT
    ),
    "es-ES": LocaleConfig(key="es-ES", name="Español (Spanish)"),
    "et-EE": LocaleConfig(key="et-EE", name="Eesti (Estonian)"),
    "fi-FI": LocaleConfig(key="fi-FI", name="Suomi (Finnish)"),
    "fr-BE": LocaleConfig(key="fr-BE", name="Belge (Belgian)"),
    "fr-CA": LocaleConfig(key="fr-CA", name="Français canadien (Canadian French)"),
    "fr-FR": LocaleConfig(key="fr-FR", name="Français (French)"),
    "gl-ES": LocaleConfig(key="gl-ES", name="Galego (Galician)"),
    "he-IL": LocaleConfig(key="he-IL", name="עברית (Hebrew)", dir=LocaleTextDirection.RTL),
    "hr-HR": LocaleConfig(key="hr-HR", name="Hrvatski (Croatian)"),
    "hu-HU": LocaleConfig(key="hu-HU", name="Magyar (Hungarian)"),
    "is-IS": LocaleConfig(key="is-IS", name="Íslenska (Icelandic)"),
    "it-IT": LocaleConfig(key="it-IT", name="Italiano (Italian)"),
    "ja-JP": LocaleConfig(key="ja-JP", name="日本語 (Japanese)", plural_food_handling=LocalePluralFoodHandling.NEVER),
    "ko-KR": LocaleConfig(key="ko-KR", name="한국어 (Korean)", plural_food_handling=LocalePluralFoodHandling.NEVER),
    "lt-LT": LocaleConfig(key="lt-LT", name="Lietuvių (Lithuanian)"),
    "lv-LV": LocaleConfig(key="lv-LV", name="Latviešu (Latvian)"),
    "nl-NL": LocaleConfig(key="nl-NL", name="Nederlands (Dutch)"),
    "no-NO": LocaleConfig(key="no-NO", name="Norsk (Norwegian)"),
    "pl-PL": LocaleConfig(key="pl-PL", name="Polski (Polish)"),
    "pt-BR": LocaleConfig(key="pt-BR", name="Português do Brasil (Brazilian Portuguese)"),
    "pt-PT": LocaleConfig(key="pt-PT", name="Português (Portuguese)"),
    "ro-RO": LocaleConfig(key="ro-RO", name="Română (Romanian)"),
    "ru-RU": LocaleConfig(key="ru-RU", name="Pусский (Russian)"),
    "sk-SK": LocaleConfig(key="sk-SK", name="Slovenčina (Slovak)"),
    "sl-SI": LocaleConfig(key="sl-SI", name="Slovenščina (Slovenian)"),
    "sr-SP": LocaleConfig(key="sr-SP", name="српски (Serbian)"),
    "sv-SE": LocaleConfig(key="sv-SE", name="Svenska (Swedish)"),
    "tr-TR": LocaleConfig(key="tr-TR", name="Türkçe (Turkish)", plural_food_handling=LocalePluralFoodHandling.NEVER),
    "uk-UA": LocaleConfig(key="uk-UA", name="Українська (Ukrainian)"),
    "vi-VN": LocaleConfig(
        key="vi-VN", name="Tiếng Việt (Vietnamese)", plural_food_handling=LocalePluralFoodHandling.NEVER
    ),
    "zh-CN": LocaleConfig(
        key="zh-CN", name="简体中文 (Chinese simplified)", plural_food_handling=LocalePluralFoodHandling.NEVER
    ),
    "zh-TW": LocaleConfig(
        key="zh-TW", name="繁體中文 (Chinese traditional)", plural_food_handling=LocalePluralFoodHandling.NEVER
    ),
}
