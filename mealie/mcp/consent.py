"""Browser consent and Mealie API controls for native MCP."""

import html
import json
import logging
import secrets
from datetime import UTC
from urllib.parse import SplitResult, quote, urlsplit

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from mcp.server.auth.provider import AuthorizationCode, AuthorizationParams, construct_redirect_uri
from pydantic import BaseModel
from sqlalchemy.orm import Session

from mealie.core.dependencies import get_admin_user, get_current_user
from mealie.db.db_setup import generate_session
from mealie.db.models.server.mcp import McpAuthorizationCode, McpAuthorizationRequest, McpClient, McpGrant, McpToken
from mealie.mcp.oauth import (
    CODE_LIFETIME,
    SCOPES,
    digest,
    issuer_url,
    mcp_enabled,
    mcp_url,
    public_base_url,
    set_mcp_enabled,
    utcnow,
    validate_enablement_url,
)
from mealie.schema.user import PrivateUser

router = APIRouter()
logger = logging.getLogger("mealie.mcp")

SCOPE_LABELS = {
    "profile:read": "Identify your Mealie account and household",
    "recipes:read": "Read recipes",
    "recipes:write": "Create and edit recipes",
    "mealplans:read": "Read your household meal plan",
    "mealplans:write": "Change your household meal plan",
    "shopping:read": "Read your household shopping lists",
    "shopping:write": "Create and change your household shopping lists",
}
# Every connection can identify its account; the rest are the user's choice
REQUIRED_SCOPE = "profile:read"


def _csp_source(redirect: SplitResult) -> str:
    if redirect.scheme in {"http", "https"}:
        return f"{redirect.scheme}://{redirect.netloc}"
    return f"{redirect.scheme}:"


def _pending(session: Session, request_secret: str) -> McpAuthorizationRequest:
    if len(request_secret) > 100:
        raise HTTPException(400, "Invalid authorization request")
    row = session.query(McpAuthorizationRequest).filter_by(request_hash=digest(request_secret)).one_or_none()
    if not row or row.expires_at <= utcnow():
        raise HTTPException(400, "Authorization request expired")
    return row


async def _browser_user(request: Request, session: Session) -> PrivateUser | None:
    if "mealie.access_token" not in request.cookies:
        return None
    try:
        return get_current_user(token=request.cookies["mealie.access_token"], session=session)
    except HTTPException:
        return None


@router.get("/oauth/consent", response_class=HTMLResponse)
async def consent_page(request: Request, session: Session = Depends(generate_session)):
    if not mcp_enabled(session):
        raise HTTPException(404)
    request_secret = request.query_params.get("request", "")
    pending = _pending(session, request_secret)
    user = await _browser_user(request, session)
    if not user:
        return_url = quote(f"/oauth/consent?request={request_secret}", safe="")
        return RedirectResponse(
            f"{public_base_url()}/login?redirect={return_url}",
            status_code=302,
        )
    from mealie.mcp.server import provider

    client = await provider.get_client(pending.client_id)
    if not client:
        raise HTTPException(400, "Client no longer available")
    params = AuthorizationParams.model_validate_json(pending.params_json)
    csrf = secrets.token_urlsafe(32)
    client_name = html.escape(client.client_name or client.client_id)
    redirect = urlsplit(str(params.redirect_uri))
    redirect_target = html.escape(redirect.netloc or f"{redirect.scheme}:")
    # Self-registered clients can claim any name; a metadata URL client_id is vouched for by its domain
    publisher = urlsplit(client.client_id).hostname if client.client_id.startswith("https://") else None
    publisher_line = (
        f"Published by {html.escape(publisher)}" if publisher else "This app registered itself and is not verified"
    )
    # Offer every scope, ticked, even if the client asked for less: many clients never
    # ask again for write access, so the user decides here and can change it later
    scope_items = "".join(
        f"<li>{html.escape(SCOPE_LABELS[scope])}</li>"
        if scope == REQUIRED_SCOPE
        else f'<li><label><input type="checkbox" name="scope" value="{scope}" checked> '
        f"{html.escape(SCOPE_LABELS[scope])}</label></li>"
        for scope in SCOPES
    )
    body = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Connect {client_name} to Mealie</title>
<style>
body {{font-family:system-ui,sans-serif;max-width:38rem;margin:3rem auto;padding:0 1rem;line-height:1.5}}
button {{padding:.7rem 1.2rem;margin-right:.6rem}}
.account {{padding:1rem;background:#f4f4f4;border-radius:.5rem}}
ul.scopes {{list-style:none;padding-left:0}}
ul.scopes li {{margin:.3rem 0}}
</style>
</head>
<body>
<h1>Connect {client_name} to Mealie?</h1>
<p>{publisher_line}. After you decide, you will be sent to <strong>{redirect_target}</strong>.</p>
<p class="account">Account: {html.escape(user.email)}<br>Household: {html.escape(user.household)}</p>
<form method="post" action="{html.escape(public_base_url())}/oauth/consent">
<p>Allow this app to:</p>
<ul class="scopes">{scope_items}</ul>
<p>You can change these permissions or revoke this connection later in Mealie's Connected apps settings.</p>
<input type="hidden" name="request" value="{html.escape(request_secret)}">
<input type="hidden" name="csrf" value="{html.escape(csrf)}">
<button type="submit" name="decision" value="approve">Allow</button>
<button type="submit" name="decision" value="deny">Deny</button>
</form>
</body>
</html>"""
    response = HTMLResponse(
        body,
        headers={
            "Cache-Control": "no-store",
            "Content-Security-Policy": (
                "default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; "
                # Chromium applies form-action to the redirect after the POST, so the client's
                # callback must be allowed or Allow/Deny never reach it
                f"form-action 'self' {_csp_source(redirect)}"
            ),
        },
    )
    response.set_cookie(
        "mealie.mcp.csrf",
        csrf,
        httponly=True,
        secure=public_base_url().startswith("https://"),
        samesite="lax",
        max_age=600,
    )
    return response


@router.post("/oauth/consent")
async def consent_decision(request: Request, session: Session = Depends(generate_session)):
    if not mcp_enabled(session):
        raise HTTPException(404)
    user = await _browser_user(request, session)
    if not user:
        raise HTTPException(401)
    form = await request.form()
    csrf = form.get("csrf")
    if not isinstance(csrf, str) or not secrets.compare_digest(csrf, request.cookies.get("mealie.mcp.csrf", "")):
        raise HTTPException(403, "Invalid consent form")
    request_secret = form.get("request")
    if not isinstance(request_secret, str):
        raise HTTPException(400, "Invalid authorization request")
    pending = _pending(session, request_secret)
    params = AuthorizationParams.model_validate_json(pending.params_json)
    # The SDK has already checked this URI against the client's registration.
    if params.resource != mcp_url():
        raise HTTPException(400, "Invalid resource")
    session.delete(pending)
    if form.get("decision") != "approve":
        session.commit()
        logger.info("MCP consent denied for user %s client %s", user.id, pending.client_id)
        redirect = construct_redirect_uri(
            str(params.redirect_uri), error="access_denied", state=params.state, iss=issuer_url()
        )
    else:
        chosen = set(form.getlist("scope")) | {REQUIRED_SCOPE}
        scopes = [scope for scope in SCOPES if scope in chosen]
        grant = McpGrant(
            user_id=user.id,
            household_id=user.household_id,
            client_id=pending.client_id,
            scopes_json=json.dumps(scopes),
        )
        session.add(grant)
        session.flush()
        code = secrets.token_urlsafe(48)
        auth_code = AuthorizationCode(
            code=code,
            scopes=scopes,
            expires_at=(utcnow() + CODE_LIFETIME).replace(tzinfo=UTC).timestamp(),
            client_id=pending.client_id,
            code_challenge=params.code_challenge,
            redirect_uri=params.redirect_uri,
            redirect_uri_provided_explicitly=params.redirect_uri_provided_explicitly,
            resource=params.resource,
            subject=str(user.id),
        )
        session.add(
            McpAuthorizationCode(
                code_hash=digest(code),
                grant_id=grant.id,
                client_id=pending.client_id,
                params_json=auth_code.model_copy(update={"code": ""}).model_dump_json(),
                expires_at=utcnow() + CODE_LIFETIME,
            )
        )
        session.commit()
        logger.info("MCP consent approved for user %s client %s grant %s", user.id, pending.client_id, grant.id)
        redirect = construct_redirect_uri(str(params.redirect_uri), code=code, state=params.state, iss=issuer_url())
    response = RedirectResponse(redirect, status_code=302, headers={"Cache-Control": "no-store"})
    response.delete_cookie("mealie.mcp.csrf")
    return response


class McpSettingRequest(BaseModel):
    enabled: bool


class McpConnectionUpdate(BaseModel):
    scopes: list[str]


@router.get("/api/admin/mcp")
def admin_mcp_settings(_: PrivateUser = Depends(get_admin_user), session: Session = Depends(generate_session)):
    try:
        url = validate_enablement_url()
        error = None
    except ValueError as exc:
        url = None
        error = str(exc)
    return {"enabled": mcp_enabled(session), "url": url, "configuration_error": error}


@router.put("/api/admin/mcp")
def update_admin_mcp_settings(
    data: McpSettingRequest, user: PrivateUser = Depends(get_admin_user), session: Session = Depends(generate_session)
):
    if data.enabled:
        try:
            validate_enablement_url()
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc
    set_mcp_enabled(session, data.enabled)
    logger.info("MCP feature %s by administrator %s", "enabled" if data.enabled else "disabled", user.id)
    try:
        url = validate_enablement_url()
    except ValueError:
        url = None
    return {"enabled": mcp_enabled(session), "url": url}


@router.get("/api/users/mcp/connections")
def list_mcp_connections(user: PrivateUser = Depends(get_current_user), session: Session = Depends(generate_session)):
    grants = session.query(McpGrant).filter_by(user_id=user.id).order_by(McpGrant.id.desc()).all()
    clients = {item.client_id: item for item in session.query(McpClient).all()}
    result = []
    for grant in grants:
        client = clients.get(grant.client_id)
        result.append(
            {
                "id": grant.id,
                "client_name": client.client_name if client and client.client_name else grant.client_id,
                "client_id": grant.client_id,
                "scopes": json.loads(grant.scopes_json),
                "created_at": grant.created_at,
                "revoked": grant.revoked_at is not None,
            }
        )
    return result


@router.delete("/api/users/mcp/connections/{grant_id}")
def revoke_mcp_connection(
    grant_id: int, user: PrivateUser = Depends(get_current_user), session: Session = Depends(generate_session)
):
    grant = session.query(McpGrant).filter_by(id=grant_id, user_id=user.id).one_or_none()
    if not grant:
        raise HTTPException(404)
    grant.revoked_at = utcnow()
    session.query(McpToken).filter_by(grant_id=grant.id).update({McpToken.revoked_at: utcnow()})
    session.commit()
    logger.info("MCP grant %s revoked by user %s", grant.id, user.id)
    return {"revoked": True}


@router.put("/api/users/mcp/connections/{grant_id}")
def update_mcp_connection(
    grant_id: int,
    data: McpConnectionUpdate,
    user: PrivateUser = Depends(get_current_user),
    session: Session = Depends(generate_session),
):
    grant = session.query(McpGrant).filter_by(id=grant_id, user_id=user.id).one_or_none()
    if not grant or grant.revoked_at:
        raise HTTPException(404)
    if not set(data.scopes).issubset(SCOPES):
        raise HTTPException(400, "Unsupported MCP scope")
    chosen = set(data.scopes) | {REQUIRED_SCOPE}
    scopes = [scope for scope in SCOPES if scope in chosen]
    grant.scopes_json = json.dumps(scopes)
    session.commit()
    logger.info("MCP grant %s scopes changed by user %s", grant.id, user.id)
    return {"id": grant.id, "scopes": scopes}
