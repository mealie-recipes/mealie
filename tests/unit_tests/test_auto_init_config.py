from pydantic import ConfigDict

from mealie.db.models._model_utils.auto_init import _get_config


class _NoConfig:
    pass


class _CustomExcludeOnly:
    model_config = ConfigDict(exclude={"households_with_ingredient_food"})


class _CustomExcludeWithId:
    model_config = ConfigDict(exclude={"id", "recipe"})


class _OtherConfigKeyOnly:
    model_config = ConfigDict(get_attr="slug")


def test_get_config_defaults_to_excluding_id_when_no_model_config():
    cfg = _get_config(_NoConfig)
    assert cfg.exclude == {"id"}


def test_get_config_merges_custom_exclude_with_default_id_exclusion():
    """Regression test for GH issue #8088."""
    cfg = _get_config(_CustomExcludeOnly)
    assert cfg.exclude == {"id", "households_with_ingredient_food"}


def test_get_config_does_not_duplicate_id_when_custom_exclude_already_has_it():
    cfg = _get_config(_CustomExcludeWithId)
    assert cfg.exclude == {"id", "recipe"}


def test_get_config_preserves_default_exclude_for_unrelated_config_keys():
    cfg = _get_config(_OtherConfigKeyOnly)
    assert cfg.get_attr == "slug"
    assert cfg.exclude == {"id"}
