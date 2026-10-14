import logging

from authlib.integrations.starlette_client import OAuth
from pytest import LogCaptureFixture, MonkeyPatch

from mealie.routes.auth import auth as auth_routes

WEB_CLIENT_ID = "web-client-id"
WEB_CLIENT_SECRET = "web-client-secret"


def register_native_client(monkeypatch: MonkeyPatch, native_id: str | None, confidential: bool):
    monkeypatch.setattr(auth_routes.settings, "OIDC_CLIENT_ID", WEB_CLIENT_ID)
    monkeypatch.setattr(auth_routes.settings, "OIDC_CLIENT_SECRET", WEB_CLIENT_SECRET)
    monkeypatch.setattr(auth_routes.settings, "OIDC_NATIVE_CLIENT_ID", native_id)
    monkeypatch.setattr(auth_routes.settings, "OIDC_NATIVE_CONFIDENTIAL", confidential)

    client_args = {"scope": "openid email profile"}
    snapshot = dict(client_args)
    oauth = OAuth()
    auth_routes._register_native_oidc_client(oauth, client_args)

    assert client_args == snapshot, "client_args is shared with the web client and must not be mutated"
    return oauth.create_client("oidc_native")


def test_no_native_id_uses_web_client(monkeypatch: MonkeyPatch):
    client = register_native_client(monkeypatch, None, True)

    assert client.client_id == WEB_CLIENT_ID
    assert client.client_secret == WEB_CLIENT_SECRET
    assert "token_endpoint_auth_method" not in client.client_kwargs


def test_native_id_confidential_keeps_secret(monkeypatch: MonkeyPatch):
    client = register_native_client(monkeypatch, "native-app", True)

    assert client.client_id == "native-app"
    assert client.client_secret == WEB_CLIENT_SECRET
    assert "token_endpoint_auth_method" not in client.client_kwargs


def test_native_id_public_drops_secret(monkeypatch: MonkeyPatch):
    client = register_native_client(monkeypatch, "native-app", False)

    assert client.client_id == "native-app"
    assert client.client_secret is None
    assert client.client_kwargs["token_endpoint_auth_method"] == "none"
    assert client.client_kwargs["scope"] == "openid email profile"


def test_public_without_native_id_warns_and_stays_confidential(monkeypatch: MonkeyPatch, caplog: LogCaptureFixture):
    caplog.set_level(logging.WARNING)
    client = register_native_client(monkeypatch, None, False)

    assert client.client_id == WEB_CLIENT_ID
    assert client.client_secret == WEB_CLIENT_SECRET
    assert "token_endpoint_auth_method" not in client.client_kwargs
    assert "OIDC_NATIVE_CONFIDENTIAL=false has no effect" in caplog.text


def test_empty_native_id_falls_back_to_web_client(monkeypatch: MonkeyPatch):
    client = register_native_client(monkeypatch, "", True)

    assert client.client_id == WEB_CLIENT_ID
    assert client.client_secret == WEB_CLIENT_SECRET


def test_public_native_client_leaves_web_client_unaffected(monkeypatch: MonkeyPatch):
    monkeypatch.setattr(auth_routes.settings, "OIDC_CLIENT_ID", WEB_CLIENT_ID)
    monkeypatch.setattr(auth_routes.settings, "OIDC_CLIENT_SECRET", WEB_CLIENT_SECRET)
    monkeypatch.setattr(auth_routes.settings, "OIDC_NATIVE_CLIENT_ID", "native-app")
    monkeypatch.setattr(auth_routes.settings, "OIDC_NATIVE_CONFIDENTIAL", False)

    client_args = {"scope": "openid email profile"}
    oauth = OAuth()
    oauth.register(
        "oidc",
        client_id=auth_routes.settings.OIDC_CLIENT_ID,
        client_secret=auth_routes.settings.OIDC_CLIENT_SECRET,
        server_metadata_url=auth_routes.settings.OIDC_CONFIGURATION_URL,
        client_kwargs=client_args,
        code_challenge_method="S256",
    )
    auth_routes._register_native_oidc_client(oauth, client_args)

    web = oauth.create_client("oidc")
    assert web.client_id == WEB_CLIENT_ID
    assert web.client_secret == WEB_CLIENT_SECRET
    assert "token_endpoint_auth_method" not in web.client_kwargs

    native = oauth.create_client("oidc_native")
    assert native.client_id == "native-app"
    assert native.client_secret is None
    assert native.client_kwargs["token_endpoint_auth_method"] == "none"
