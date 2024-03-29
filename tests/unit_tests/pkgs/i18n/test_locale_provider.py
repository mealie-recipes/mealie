from mealie.pkgs.i18n import JsonProvider, ProviderFactory
from tests.data import locale_dir


def test_json_provider():
    provider = JsonProvider({"test": "test"})

    assert provider.t("test") == "test"
    assert provider.t("test2", "DEFAULT") == "DEFAULT"


def test_json_provider_plural():
    provider = JsonProvider({"test": "test | tests"})
    assert provider.t("test", count=0) == "tests"
    assert provider.t("test", count=0.5) == "tests"
    assert provider.t("test", count=1) == "test"
    assert provider.t("test", count=1.5) == "tests"
    assert provider.t("test", count=2) == "tests"

    provider = JsonProvider({"test": "test 0 | test | tests"})
    assert provider.t("test", count=0) == "test 0"
    assert provider.t("test", count=0.5) == "tests"
    assert provider.t("test", count=1) == "test"
    assert provider.t("test", count=1.5) == "tests"
    assert provider.t("test", count=2) == "tests"

    provider = JsonProvider({"test": "zero tests | one test | {count} tests"})
    assert provider.t("test", count=0) == "zero tests"
    assert provider.t("test", count=0.5) == "0.5 tests"
    assert provider.t("test", count=1) == "one test"
    assert provider.t("test", count=1.5) == "1.5 tests"
    assert provider.t("test", count=2) == "2 tests"


def test_json_provider_nested_keys():
    nested_dict = {
        "root": {
            "tier1": "tire1_value",
        },
    }

    provider = JsonProvider(nested_dict)

    assert provider.t("root.tier1") == "tire1_value"


def test_json_provider_nested_keys_not_found():
    nested_dict = {
        "root": {
            "tier1": "tire1_value",
        },
    }

    provider = JsonProvider(nested_dict)

    assert provider.t("root.tier2") == "root.tier2"


def test_locale_provider_defaults():
    factory = ProviderFactory(locale_dir)

    assert factory.get("en-US") is not None
    assert factory.get("asdfadsf") is not None

    assert factory._store["en-US"].locks == 1

    factory.release("en-US")

    assert "en-US" not in factory._store


def test_locale_providers_store_locks():
    factory = ProviderFactory(locale_dir)

    factory.get("en-US")
    factory.get("en-US")
    factory.get("en-US")

    assert factory._store["en-US"].locks == 3

    factory.release("en-US")

    assert factory._store["en-US"].locks == 2

    factory.release("en-US")
    factory.release("en-US")

    assert "en-US" not in factory._store
