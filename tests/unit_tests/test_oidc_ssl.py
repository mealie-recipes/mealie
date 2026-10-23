import ssl
from pathlib import Path

from pytest import MonkeyPatch

from mealie.routes.auth import auth as auth_routes

TEST_CERT = """-----BEGIN CERTIFICATE-----
MIIDBTCCAe2gAwIBAgIUA/xvUb9Kfht66Q/ZCuc0TlFcRuUwDQYJKoZIhvcNAQEL
BQAwEjEQMA4GA1UEAwwHVGVzdCBDQTAeFw0yNjEwMjAwNjU3MTNaFw0yNzEwMjAw
NjU3MTNaMBIxEDAOBgNVBAMMB1Rlc3QgQ0EwggEiMA0GCSqGSIb3DQEBAQUAA4IB
DwAwggEKAoIBAQC0SpM0h5CwebttY9II3dHLP0p7qH3ssbXALMotBRQX2YjqM9xm
IdrAuiYGvJsRg3ZTTNJizur8gP8CuAnaIOw+e1NAJl6J9TNiGJNBfNGtn87bBf9m
OZAbxH+z2cGn/924cT26Ijq7CUaUFODO6NFoGFTr6t2Wk2BnE+hcACh5MxeLkicJ
91rtkAv7afB/zNVtuIbZsNe08+Pm0osAdQh5Kv4vBexh2hbMcs0oghikCP/d/tKH
s8/mxeTBJsX6be4IechDuXXb2oDMtb5dTrF6QVuUbYAtYxeGo3YGG8260YF2QHFU
gy34MgM0ezZ/GVEataeLLbnIqJPjhkFWdWlbAgMBAAGjUzBRMB0GA1UdDgQWBBRH
xgjwClKENvszoeCKab8BAXgCxTAfBgNVHSMEGDAWgBRHxgjwClKENvszoeCKab8B
AXgCxTAPBgNVHRMBAf8EBTADAQH/MA0GCSqGSIb3DQEBCwUAA4IBAQAHQD0HvF6h
Zh9WcPpXKEA41antnK5sUsaPNfTF2Isx8Ss2fOE+GYylVW1jhI+AIIDyFtJY+Vdr
Z/QAlF7b6E+5FJ2BphzWiGwQMwsPA/Qjr62uws/LJs9Ac/PB5Kj+wysthRnMBGgE
lHD5hMvcVXEVpD5pvHQWVmITOLZ04mbHU531u2wxsWLtgmXPImgEe8OSSWDAx9gR
QxRQ+mwrIsnCRhgg7yinQr1HDvgTyJxuG1KXcG7qETcl3IONDSjulQbsEC8Xq/FE
EzdKxOhbswBFBQFyvIzaweeEfgzUZBt68NQ/hEMeEp3CBxb2XKEHtOMKkRzMGslb
xQfVmPNTv9YI
-----END CERTIFICATE-----"""


def test_default_oidc_ssl_context_returns_none():
    """When neither custom CA nor relaxed strict is requested, return None to use httpx defaults."""
    ctx = auth_routes._create_oidc_ssl_context(cafile=None, verify_strict=True)
    assert ctx is None


def test_relaxed_strict_default_ca():
    """When relaxed strict is requested with default CAs, return an SSLContext with VERIFY_X509_STRICT cleared."""
    ctx = auth_routes._create_oidc_ssl_context(cafile=None, verify_strict=False)
    assert isinstance(ctx, ssl.SSLContext)
    assert not (ctx.verify_flags & ssl.VERIFY_X509_STRICT)
    assert len(ctx.get_ca_certs()) > 0


def test_custom_ca_strict(tmp_path: Path):
    """When a custom CA is specified with strict verification, return an SSLContext with VERIFY_X509_STRICT enabled."""
    cert_file = tmp_path / "test_ca.crt"
    cert_file.write_text(TEST_CERT)

    ctx = auth_routes._create_oidc_ssl_context(cafile=str(cert_file), verify_strict=True)
    assert isinstance(ctx, ssl.SSLContext)
    assert bool(ctx.verify_flags & ssl.VERIFY_X509_STRICT)
    assert len(ctx.get_ca_certs()) > 0


def test_custom_ca_relaxed_strict(tmp_path: Path):
    """When both custom CA and relaxed strict are specified, return an SSLContext with custom CA and relaxed flags."""
    cert_file = tmp_path / "test_ca.crt"
    cert_file.write_text(TEST_CERT)

    ctx = auth_routes._create_oidc_ssl_context(cafile=str(cert_file), verify_strict=False)
    assert isinstance(ctx, ssl.SSLContext)
    assert not (ctx.verify_flags & ssl.VERIFY_X509_STRICT)
    assert len(ctx.get_ca_certs()) > 0


def test_oidc_client_args_verify_integration(tmp_path: Path, monkeypatch: MonkeyPatch):
    """Verify that settings are correctly mapped to client_args['verify'] without overriding each other."""
    cert_file = tmp_path / "test_ca.crt"
    cert_file.write_text(TEST_CERT)

    monkeypatch.setattr(auth_routes.settings, "OIDC_TLS_CACERTFILE", str(cert_file))
    monkeypatch.setattr(auth_routes.settings, "OIDC_VERIFY_X509_STRICT", False)

    ctx = auth_routes._create_oidc_ssl_context(
        auth_routes.settings.OIDC_TLS_CACERTFILE,
        auth_routes.settings.OIDC_VERIFY_X509_STRICT,
    )
    assert isinstance(ctx, ssl.SSLContext)
    assert not (ctx.verify_flags & ssl.VERIFY_X509_STRICT)
    assert len(ctx.get_ca_certs()) > 0
