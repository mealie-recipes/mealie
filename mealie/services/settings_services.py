import json
from typing import List, Optional

from db.settings_models import (
    SiteSettingsDocument,
    SiteThemeDocument,
    ThemeColorsDocument,
    WebhooksDocument,
)
from pydantic import BaseModel


class Webhooks(BaseModel):
    webhookTime: str
    webhookURLs: Optional[List[str]]
    enabled: bool

    @staticmethod
    def run():
        pass


class SiteSettings(BaseModel):
    name: str = "main"
    webhooks: Webhooks

    @staticmethod
    def _unpack_doc(document: SiteSettingsDocument):
        document = json.loads(document.to_json())
        del document["_id"]
        document["webhhooks"] = Webhooks(**document["webhooks"])
        return SiteSettings(**document)

    @staticmethod
    def get_site_settings():
        try:
            document = SiteSettingsDocument.objects.get(name="main")
        except:
            webhooks = WebhooksDocument()
            document = SiteSettingsDocument(name="main", webhooks=webhooks)
            document.save()

        return SiteSettings._unpack_doc(document)

    def update(self):
        document = SiteSettingsDocument.objects.get(name="main")
        new_webhooks = WebhooksDocument(**self.webhooks.dict())

        document.update(set__webhooks=new_webhooks)

        document.save()


class Colors(BaseModel):
    primary: str
    accent: str
    secondary: str
    success: str
    info: str
    warning: str
    error: str


class SiteTheme(BaseModel):
    name: str
    colors: Colors

    @staticmethod
    def get_by_name(theme_name):
        document = SiteThemeDocument.objects.get(name=theme_name)
        return SiteTheme._unpack_doc(document)

    @staticmethod
    def _unpack_doc(document):
        document = json.loads(document.to_json())
        del document["_id"]
        theme_colors = SiteTheme(**document)
        return theme_colors

    @staticmethod
    def get_all():
        all_themes = []
        for theme in SiteThemeDocument.objects():
            all_themes.append(SiteTheme._unpack_doc(theme))

        return all_themes

    def save_to_db(self):
        theme = self.dict()
        theme["colors"] = ThemeColorsDocument(**theme["colors"])

        theme_document = SiteThemeDocument(**theme)

        theme_document.save()

    def update_document(self):
        theme = self.dict()
        theme["colors"] = ThemeColorsDocument(**theme["colors"])

        theme_document = SiteThemeDocument.objects.get(name=self.name)

        if theme_document:
            theme_document.update(set__colors=theme["colors"])

        theme_document.save()

    @staticmethod
    def delete_theme(theme_name: str) -> str:
        """ Removes the theme by name """
        document = SiteThemeDocument.objects.get(name=theme_name)

        if document:
            document.delete()
            return "Document Deleted"
