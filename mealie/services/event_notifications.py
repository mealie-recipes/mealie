import apprise
from mealie.schema.event_notifications import EventNotificationIn
from mealie.schema.events import Event


def post_notifications(event: Event, notification_dests=list[EventNotificationIn]):
    # Create an Apprise instance

    # discord = Discord(
    #     webhook_id="840358511842295829",
    #     webhook_token="EtcH6ACFM-qpHRkPw1TUTc_r8AiVMlKYhGEzlANvXj7SlGGFZt18dkYy96ayZHZ8HaI9",
    # )
    # Create our asset object
    asset = apprise.AppriseAsset(async_mode=False)

    # Create our object
    apobj = apprise.Apprise(asset=asset)

    # Add all of the notification services by their server url.
    # A sample email notification:

    for dest in notification_dests:
        dest: EventNotificationIn
        apobj.add(dest.notification_url)

    # A sample pushbullet notification
    # Then notify these services any time you desire. The below would
    # notify all of the services loaded into our Apprise object.
    apobj.notify(
        body=event.text,
        title=event.title,
    )
