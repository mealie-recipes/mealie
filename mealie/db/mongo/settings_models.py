import mongoengine


class WebhooksDocument(mongoengine.EmbeddedDocument):
    webhookURLs = mongoengine.ListField(required=False, default=[])
    webhookTime = mongoengine.StringField(required=False, default="00:00")
    enabled = mongoengine.BooleanField(required=False, default=False)


class SiteSettingsDocument(mongoengine.Document):
    name = mongoengine.StringField(require=True, default="main", unique=True)
    webhooks = mongoengine.EmbeddedDocumentField(WebhooksDocument, required=True)

    meta = {
        "db_alias": "core",
        "collection": "settings",
    }


class ThemeColorsDocument(mongoengine.EmbeddedDocument):
    primary = mongoengine.StringField(require=True)
    accent = mongoengine.StringField(require=True)
    secondary = mongoengine.StringField(require=True)
    success = mongoengine.StringField(require=True)
    info = mongoengine.StringField(require=True)
    warning = mongoengine.StringField(require=True)
    error = mongoengine.StringField(require=True)


class SiteThemeDocument(mongoengine.Document):
    name = mongoengine.StringField(require=True, unique=True)
    colors = mongoengine.EmbeddedDocumentField(ThemeColorsDocument, required=True)

    meta = {
        "db_alias": "core",
        "collection": "themes",
    }
