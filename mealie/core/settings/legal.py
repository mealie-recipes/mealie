from pydantic_settings import BaseSettings, SettingsConfigDict


class Legal(BaseSettings):
    """Identity shown on the /legal pages (mentions légales, politique de confidentialité).

    Left blank by default on purpose: the operator's name/contact are personal information this
    app has no business guessing, so the frontend shows a "to be completed" notice until these
    are set via env vars.
    """

    controller_name: str = ""
    contact_email: str = ""
    # The actual source this instance runs from - required by the AGPLv3 this project is
    # licensed under (network use counts as distribution, so users must be able to get the
    # source, including any modifications). Not personal information, just a repo URL.
    source_url: str = "https://github.com/mealie-recipes/mealie"

    model_config = SettingsConfigDict(env_prefix="legal_", extra="allow")
