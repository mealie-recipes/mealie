from pathlib import Path

from mealie.pkgs.i18n.json_provider import JsonProvider
from mealie.services.event_bus_service.event_types import EventBusMessage, EventTypes


def test_event_message_uses_localized_title():
    translator = JsonProvider(
        {
            "notifications": {
                "event-title": {
                    "mealplan-entry-created": "已创建膳食计划条目",
                }
            }
        }
    )

    message = EventBusMessage.from_type(
        EventTypes.mealplan_entry_created,
        body="测试正文",
        translator=translator,
    )

    assert message.title == "已创建膳食计划条目"
    assert message.body == "测试正文"


def test_event_message_uses_english_title_without_translator():
    message = EventBusMessage.from_type(
        EventTypes.mealplan_entry_created,
        body="test body",
    )

    assert message.title == "Mealplan Entry Created"
    assert message.body == "test body"


def test_event_message_uses_fallback_for_missing_translation():
    translator = JsonProvider({})

    message = EventBusMessage.from_type(
        EventTypes.mealplan_entry_created,
        body="test body",
        translator=translator,
    )

    assert message.title == "Mealplan Entry Created"


def test_empty_body_uses_generic_fallback():
    message = EventBusMessage.from_type(EventTypes.test_message)

    assert message.body == "generic"


def test_english_notification_translations():
    repo_root = Path(__file__).parents[4]
    translator = JsonProvider(repo_root / "mealie/lang/messages/en-US.json")

    message = EventBusMessage.from_type(EventTypes.mealplan_entry_created, translator=translator)
    body = translator.t(
        "notifications.mealplan-entry-created",
        date="2026-08-17",
        entry_type=translator.t("mealplan.entry-type.dinner"),
    )

    assert message.title == "Meal Plan Entry Created"
    assert body == "Meal plan entry created for 2026-08-17 for dinner"


def test_every_event_type_has_an_english_title_translation():
    repo_root = Path(__file__).parents[4]
    translator = JsonProvider(repo_root / "mealie/lang/messages/en-US.json")

    missing_keys = []
    for event_type in EventTypes:
        event_name = event_type.name.replace("_", "-")
        key = f"notifications.event-title.{event_name}"
        if translator.t(key) == key:
            missing_keys.append(key)

    assert not missing_keys, f"Missing event title translations: {missing_keys}"
