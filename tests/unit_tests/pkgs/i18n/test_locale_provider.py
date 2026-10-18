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

    assert factory.get("en-US") is factory.get("asdfadsf")
    assert set(factory._store) == {"en-US"}


def test_locale_provider_loads_supported_locale():
    factory = ProviderFactory(locale_dir)

    assert factory.get("af-ZA") is not factory.get("en-US")
    assert set(factory._store) == {"af-ZA", "en-US"}


def test_locale_provider_rejects_path_traversal(tmp_path):
    outside = tmp_path / "secret.json"
    outside.write_text('{"secret": "leaked"}')
    relative = "../" * len(locale_dir.resolve().parts) + str(outside.with_suffix("")).lstrip("/")

    factory = ProviderFactory(locale_dir)
    fallback = factory.get("en-US")

    for locale in [str(outside.with_suffix("")), relative, "../en-US", "./en-US"]:
        provider = factory.get(locale)
        assert provider is fallback
        assert provider.t("secret") == "secret"

    assert set(factory._store) == {"en-US"}
