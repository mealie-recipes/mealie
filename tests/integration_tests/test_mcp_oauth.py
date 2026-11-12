"""End-to-end checks for the MCP feature in the normal Mealie ASGI app."""

import base64
import hashlib
import json
import os
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from urllib.parse import parse_qs, urlsplit
from uuid import UUID, uuid4

from bs4 import BeautifulSoup
from fastapi.testclient import TestClient

from mealie.app import app
from mealie.db.db_setup import session_context
from mealie.db.models.server.mcp import McpToken
from mealie.db.models.users.users import User
from mealie.mcp.oauth import REFRESH_REUSE_GRACE, digest, utcnow
from mealie.mcp.tools import TOOL_SCOPES

RESOURCE = "http://localhost:8080/mcp"


def _tool(client: TestClient, token: str, name: str, arguments: dict | None = None):
    return client.post(
        "/mcp",
        headers={
            "Authorization": f"Bearer {token}",
            "MCP-Protocol-Version": "2026-07-28",
            "Mcp-Method": "tools/call",
            "Mcp-Name": name,
        },
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": arguments or {},
                "_meta": {
                    "io.modelcontextprotocol/protocolVersion": "2026-07-28",
                    "io.modelcontextprotocol/clientCapabilities": {},
                    "io.modelcontextprotocol/clientInfo": {"name": "Mealie test", "version": "1"},
                },
            },
        },
    )


def _list_tools(client: TestClient, token: str):
    return client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}", "MCP-Protocol-Version": "2026-07-28", "Mcp-Method": "tools/list"},
        json={
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {
                "_meta": {
                    "io.modelcontextprotocol/protocolVersion": "2026-07-28",
                    "io.modelcontextprotocol/clientCapabilities": {},
                    "io.modelcontextprotocol/clientInfo": {"name": "Mealie test", "version": "1"},
                }
            },
        },
    )


def _consent_form(page: str) -> dict:
    """The consent form as a browser would submit it with the default ticks."""
    soup = BeautifulSoup(page, "html.parser")
    form: dict = {item["name"]: item["value"] for item in soup.select("input[type=hidden]")}
    form["scope"] = [item["value"] for item in soup.select("input[name=scope][checked]")]
    return form


def _tool_result(response) -> dict:
    assert response.status_code == 200, response.text
    result = response.json()["result"]
    assert not result["isError"], response.text
    return json.loads(result["content"][0]["text"])


def test_native_mcp_oauth_flow_and_switch():
    with TestClient(app, base_url="http://localhost:8080") as client:
        login = client.post("/api/auth/token", data={"username": "changeme@example.com", "password": "MyPassword"})
        assert login.status_code == 200
        mealie_auth = {"Authorization": f"Bearer {login.json()['access_token']}"}
        assert client.put("/api/admin/mcp", json={"enabled": False}).status_code == 200
        assert client.get("/mcp").status_code == 404
        assert client.get("/.well-known/oauth-protected-resource/mcp").status_code == 404
        assert client.put("/api/admin/mcp", json={"enabled": True}).status_code == 200

        metadata = client.get("/.well-known/oauth-protected-resource/mcp").json()
        assert metadata["resource"] == RESOURCE
        assert "recipes:read" in metadata["scopes_supported"]
        auth_metadata = client.get("/.well-known/oauth-authorization-server/oauth").json()
        assert auth_metadata["issuer"] == "http://localhost:8080/oauth"
        assert "none" in auth_metadata["token_endpoint_auth_methods_supported"]
        assert auth_metadata["code_challenge_methods_supported"] == ["S256"]
        preflight = client.options(
            "/.well-known/oauth-protected-resource/mcp",
            headers={
                "Origin": "http://localhost:6274",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "mcp-protocol-version",
            },
        )
        assert preflight.status_code == 200
        assert preflight.headers["access-control-allow-origin"] in ("*", "http://localhost:6274")
        for probe in ("/.well-known/openid-configuration", "/.well-known/oauth-protected-resource"):
            missing = client.get(probe)
            assert missing.status_code == 404 and missing.headers["content-type"].startswith("application/json")
        assert client.get("/mcp").status_code == 401
        assert _tool(client, login.json()["access_token"], "get_profile").status_code == 401
        registration = client.post(
            "/oauth/register",
            json={
                "client_name": "Mealie test client",
                "redirect_uris": ["http://127.0.0.1:5599/callback"],
                "token_endpoint_auth_method": "none",
                "application_type": "native",
            },
        )
        assert registration.status_code in (200, 201), registration.text
        client_id = registration.json()["client_id"]
        extra_scopes = client.post(
            "/oauth/register",
            json={
                "client_name": "Client asking for OIDC scopes",
                "redirect_uris": ["http://127.0.0.1:5599/callback"],
                "token_endpoint_auth_method": "none",
                "application_type": "native",
                "scope": "openid offline_access recipes:read",
            },
        )
        assert extra_scopes.status_code in (200, 201), extra_scopes.text

        verifier = "test-verifier-for-mcp-oauth-pkce-12345678901234567890"
        challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
        auth_params = {
            "client_id": client_id,
            "redirect_uri": "http://127.0.0.1:5599/callback",
            "response_type": "code",
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "resource": RESOURCE,
            "scope": "profile:read recipes:read",
            "state": "test-state",
        }
        default_authorization = client.get(
            "/oauth/authorize",
            params={key: value for key, value in auth_params.items() if key != "scope"},
            follow_redirects=False,
        )
        assert default_authorization.status_code == 302, default_authorization.text
        default_consent = client.get(default_authorization.headers["location"])
        assert default_consent.status_code == 200
        csp = default_consent.headers["content-security-policy"]
        assert "form-action 'self' http://127.0.0.1:5599" in csp
        assert "you will be sent to <strong>127.0.0.1:5599</strong>" in default_consent.text
        assert "registered itself and is not verified" in default_consent.text
        # Every permission is offered and ticked, even when the client asked for nothing
        default_form = _consent_form(default_consent.text)
        assert default_form["scope"] == [
            "recipes:read",
            "recipes:write",
            "mealplans:read",
            "mealplans:write",
            "shopping:read",
            "shopping:write",
        ]
        assert "Create and change your household shopping lists" in default_consent.text
        default_denial = client.post(
            "/oauth/consent", data={**default_form, "decision": "deny"}, follow_redirects=False
        )
        assert default_denial.status_code == 302
        assert parse_qs(urlsplit(default_denial.headers["location"]).query)["error"] == ["access_denied"]
        wrong_redirect = client.get(
            "/oauth/authorize",
            params={**auth_params, "redirect_uri": "http://127.0.0.1:5599/other"},
            follow_redirects=False,
        )
        assert wrong_redirect.status_code == 400
        # RFC 8252 section 7.3: native apps pick their loopback port at runtime
        other_port = client.get(
            "/oauth/authorize",
            params={**auth_params, "redirect_uri": "http://127.0.0.1:5600/callback"},
            follow_redirects=False,
        )
        assert other_port.status_code == 302
        assert urlsplit(other_port.headers["location"]).path == "/oauth/consent"
        # Clients differ in how they send the resource indicator and which scopes they ask for
        for variant in (
            {"resource": None},
            {"resource": RESOURCE + "/"},
            {"resource": RESOURCE.removesuffix("/mcp")},
            {"scope": "openid profile:read recipes:read offline_access"},
        ):
            variant_params = {key: value for key, value in {**auth_params, **variant}.items() if value is not None}
            response = client.get("/oauth/authorize", params=variant_params, follow_redirects=False)
            assert urlsplit(response.headers["location"]).path == "/oauth/consent", variant
        wrong_resource = client.get(
            "/oauth/authorize", params={**auth_params, "resource": "https://wrong.example/mcp"}, follow_redirects=False
        )
        assert parse_qs(urlsplit(wrong_resource.headers["location"]).query)["error"] == ["invalid_target"]
        plain_pkce = client.get(
            "/oauth/authorize", params={**auth_params, "code_challenge_method": "plain"}, follow_redirects=False
        )
        assert plain_pkce.status_code == 302
        assert "error" in parse_qs(urlsplit(plain_pkce.headers["location"]).query)
        authorization = client.get("/oauth/authorize", params=auth_params, follow_redirects=False)
        assert authorization.status_code == 302, authorization.text
        consent = client.get(authorization.headers["location"])
        assert consent.status_code == 200
        assert "Read recipes" in consent.text
        # The user unticks everything except reading recipes
        form = {**_consent_form(consent.text), "scope": ["recipes:read"]}
        assert client.post("/oauth/consent", data={**form, "csrf": "wrong", "decision": "approve"}).status_code == 403
        approval = client.post("/oauth/consent", data={**form, "decision": "approve"}, follow_redirects=False)
        assert approval.status_code == 302, approval.text
        code = parse_qs(urlsplit(approval.headers["location"]).query)["code"][0]
        token_fields = {
            "grant_type": "authorization_code",
            "code": code,
            "code_verifier": verifier,
            "client_id": client_id,
            "redirect_uri": auth_params["redirect_uri"],
            "resource": RESOURCE,
        }
        assert (
            client.post("/oauth/token", data={**token_fields, "resource": "https://wrong.example/mcp"}).status_code
            == 400
        )
        assert client.post("/oauth/token", data={**token_fields, "code_verifier": "wrong"}).status_code == 400
        # The resource indicator is optional at the token endpoint
        tokens = client.post("/oauth/token", data={k: v for k, v in token_fields.items() if k != "resource"})
        assert tokens.status_code == 200, tokens.text
        access = tokens.json()["access_token"]
        assert client.post("/oauth/token", data=token_fields).status_code == 400  # one-time code
        listed = _list_tools(client, access)
        assert listed.status_code == 200, listed.text
        advertised = {tool["name"]: tool for tool in listed.json()["result"]["tools"]}
        assert advertised.keys() == TOOL_SCOPES.keys()
        for name, required_scope in TOOL_SCOPES.items():
            assert advertised[name]["securitySchemes"] == [{"type": "oauth2", "scopes": [required_scope]}]
            assert advertised[name]["_meta"]["securitySchemes"] == advertised[name]["securitySchemes"]
        assert advertised["get_profile"]["_meta"]["openai/profile"] is True
        assert advertised["get_profile"]["outputSchema"]["additionalProperties"] is False
        profile_response = _tool(client, access, "get_profile")
        profile = _tool_result(profile_response)
        assert profile_response.json()["result"]["structuredContent"]["id"] == profile["id"]
        _tool_result(_tool(client, access, "search_recipes"))
        denied = _tool(
            client, access, "add_shopping_item", {"list_id": "00000000-0000-0000-0000-000000000000", "note": "Milk"}
        )
        assert denied.status_code == 403
        # Step-up keeps the scopes already granted so re-authorizing doesn't drop read access
        assert 'scope="profile:read recipes:read shopping:write"' in denied.headers["www-authenticate"]
        assert denied.json()["result"]["_meta"]["mcp/www_authenticate"] == [denied.headers["www-authenticate"]]
        assert client.get("/api/users/self", headers={"Authorization": f"Bearer {access}"}).status_code == 401
        read_connection = client.get("/api/users/mcp/connections", headers=mealie_auth).json()[0]
        read_grant_id = read_connection["id"]
        assert read_connection["scopes"] == ["profile:read", "recipes:read"]

        # Permissions edited in Mealie apply to the client's existing token straight away
        connection_url = f"/api/users/mcp/connections/{read_grant_id}"
        assert client.put(connection_url, json={"scopes": ["admin"]}, headers=mealie_auth).status_code == 400
        widened = client.put(connection_url, json={"scopes": ["recipes:read", "shopping:read"]}, headers=mealie_auth)
        assert widened.status_code == 200, widened.text
        assert widened.json()["scopes"] == ["profile:read", "recipes:read", "shopping:read"]
        _tool_result(_tool(client, access, "list_shopping_lists"))
        narrowed = client.put(connection_url, json={"scopes": []}, headers=mealie_auth)
        assert narrowed.json()["scopes"] == ["profile:read"]
        assert _tool(client, access, "search_recipes").status_code == 403
        _tool_result(_tool(client, access, "get_profile"))
        assert client.put(connection_url, json={"scopes": ["recipes:read"]}, headers=mealie_auth).status_code == 200

        # A separate approval can add a write scope without changing the first grant.
        write_auth = client.get(
            "/oauth/authorize",
            params={
                **auth_params,
                "scope": " ".join(
                    [
                        "profile:read",
                        "recipes:read",
                        "recipes:write",
                        "mealplans:read",
                        "mealplans:write",
                        "shopping:read",
                        "shopping:write",
                    ]
                ),
            },
            follow_redirects=False,
        )
        write_consent = client.get(write_auth.headers["location"])
        write_form = _consent_form(write_consent.text)
        write_approval = client.post(
            "/oauth/consent", data={**write_form, "decision": "approve"}, follow_redirects=False
        )
        write_code = parse_qs(urlsplit(write_approval.headers["location"]).query)["code"][0]
        write_token = client.post("/oauth/token", data={**token_fields, "code": write_code})
        assert write_token.status_code == 200
        write_access = write_token.json()["access_token"]
        shopping_list = client.post(
            "/api/households/shopping/lists", json={"name": "MCP test list"}, headers=mealie_auth
        )
        assert shopping_list.status_code == 201, shopping_list.text
        list_id = shopping_list.json()["id"]
        item = _tool_result(_tool(client, write_access, "add_shopping_item", {"list_id": list_id, "note": "Milk"}))
        item_id = item["createdItems"][0]["id"]
        _tool_result(_tool(client, write_access, "update_shopping_item", {"item_id": item_id, "quantity": 2}))
        _tool_result(_tool(client, write_access, "set_shopping_item_checked", {"item_id": item_id, "checked": True}))
        _tool_result(_tool(client, write_access, "get_shopping_list", {"list_id": list_id}))
        _tool_result(_tool(client, write_access, "list_shopping_lists"))

        created_list = _tool_result(_tool(client, write_access, "create_shopping_list", {"name": "MCP groceries"}))
        new_list_id = created_list["id"]
        renamed = _tool_result(
            _tool(client, write_access, "rename_shopping_list", {"list_id": new_list_id, "name": "MCP weekly shop"})
        )
        assert renamed["name"] == "MCP weekly shop"
        for note in ("Eggs", "Bread", "Butter"):
            _tool_result(_tool(client, write_access, "add_shopping_item", {"list_id": new_list_id, "note": note}))
        items = _tool_result(_tool(client, write_access, "get_shopping_list", {"list_id": new_list_id}))["listItems"]
        assert len(items) == 3
        removed = _tool_result(_tool(client, write_access, "delete_shopping_item", {"item_id": items[0]["id"]}))
        assert [item["id"] for item in removed["deletedItems"]] == [items[0]["id"]]
        _tool_result(_tool(client, write_access, "set_all_shopping_items_checked", {"list_id": new_list_id}))
        items = _tool_result(_tool(client, write_access, "get_shopping_list", {"list_id": new_list_id}))["listItems"]
        assert len(items) == 2 and all(item["checked"] for item in items)
        _tool_result(
            _tool(client, write_access, "set_shopping_item_checked", {"item_id": items[0]["id"], "checked": False})
        )
        cleared = _tool_result(_tool(client, write_access, "clear_checked_shopping_items", {"list_id": new_list_id}))
        assert [item["id"] for item in cleared["deletedItems"]] == [items[1]["id"]]
        items = _tool_result(_tool(client, write_access, "get_shopping_list", {"list_id": new_list_id}))["listItems"]
        assert [item["id"] for item in items] == [items[0]["id"]]
        assert _tool(client, write_access, "create_shopping_list", {"name": " "}).json()["result"]["isError"]

        recipe = _tool_result(_tool(client, write_access, "create_recipe", {"name": "MCP test recipe"}))
        _tool_result(_tool(client, write_access, "get_recipe", {"slug_or_id": recipe["slug"]}))
        _tool_result(
            _tool(client, write_access, "update_recipe", {"slug_or_id": recipe["slug"], "name": "MCP recipe updated"})
        )
        meal = _tool_result(
            _tool(
                client,
                write_access,
                "add_meal_plan_entry",
                {"date": datetime.now(UTC).date().isoformat(), "title": "MCP dinner"},
            )
        )
        _tool_result(
            _tool(client, write_access, "update_meal_plan_entry", {"entry_id": meal["id"], "title": "MCP supper"})
        )
        _tool_result(_tool(client, write_access, "list_meal_plan"))

        with session_context() as session:
            access_row = session.query(McpToken).filter_by(token_hash=digest(write_access)).one()
            original_expiry = access_row.expires_at
            access_row.expires_at = utcnow() - timedelta(seconds=1)
            session.commit()
        assert _tool(client, write_access, "get_profile").status_code == 401
        with session_context() as session:
            access_row = session.query(McpToken).filter_by(token_hash=digest(write_access)).one()
            access_row.expires_at = original_expiry
            session.commit()
        assert _tool(client, write_access, "get_profile").status_code == 200

        # Even an administrator's MCP grant stays bound to the approved household.
        group = client.get("/api/groups/self", headers=mealie_auth).json()
        other_name = f"MCP other {uuid4().hex[:8]}"
        other_household = client.post(
            "/api/admin/households", json={"name": other_name, "groupId": group["id"]}, headers=mealie_auth
        )
        assert other_household.status_code == 201, other_household.text
        other_email = f"mcp-{uuid4().hex[:12]}@example.com"
        other_user = client.post(
            "/api/admin/users",
            json={
                "fullName": "Other MCP user",
                "username": f"mcp{uuid4().hex[:12]}",
                "email": other_email,
                "password": "other-user-password",
                "group": group["name"],
                "household": other_name,
                "admin": False,
                "tokens": [],
            },
            headers=mealie_auth,
        )
        assert other_user.status_code == 201, other_user.text
        other_login = client.post("/api/auth/token", data={"username": other_email, "password": "other-user-password"})
        assert other_login.status_code == 200
        other_auth = {"Authorization": f"Bearer {other_login.json()['access_token']}"}
        other_recipe = client.post("/api/recipes", json={"name": "Other household secret"}, headers=other_auth)
        assert other_recipe.status_code == 201, other_recipe.text
        other_slug = other_recipe.json()
        search = _tool_result(_tool(client, write_access, "search_recipes", {"search": "Other household secret"}))
        assert all(item["slug"] != other_slug for item in search["items"])
        assert _tool(client, write_access, "get_recipe", {"slug_or_id": other_slug}).json()["result"]["isError"]
        assert _tool(client, write_access, "update_recipe", {"slug_or_id": other_slug, "name": "Wrong"}).json()[
            "result"
        ]["isError"]
        other_meal = client.post(
            "/api/households/mealplans",
            json={"date": datetime.now(UTC).date().isoformat(), "entry_type": "dinner", "title": "Other dinner"},
            headers=other_auth,
        )
        assert other_meal.status_code == 201, other_meal.text
        other_meal_id = other_meal.json()["id"]
        plans = _tool_result(_tool(client, write_access, "list_meal_plan"))
        assert all(item["id"] != other_meal_id for item in plans["items"])
        assert _tool(
            client, write_access, "update_meal_plan_entry", {"entry_id": other_meal_id, "title": "Wrong"}
        ).json()["result"]["isError"]
        other_list = client.post("/api/households/shopping/lists", json={"name": "Other list"}, headers=other_auth)
        assert other_list.status_code == 201
        other_list_id = other_list.json()["id"]
        lists = _tool_result(_tool(client, write_access, "list_shopping_lists"))
        assert all(item["id"] != other_list_id for item in lists["items"])
        assert _tool(client, write_access, "get_shopping_list", {"list_id": other_list_id}).json()["result"]["isError"]
        assert _tool(client, write_access, "add_shopping_item", {"list_id": other_list_id, "note": "Wrong"}).json()[
            "result"
        ]["isError"]
        other_item = client.post(
            "/api/households/shopping/items",
            json={"shopping_list_id": other_list_id, "note": "Other milk", "quantity": 1},
            headers=other_auth,
        )
        assert other_item.status_code == 201, other_item.text
        other_item_id = other_item.json()["createdItems"][0]["id"]
        assert _tool(client, write_access, "update_shopping_item", {"item_id": other_item_id, "note": "Wrong"}).json()[
            "result"
        ]["isError"]
        assert _tool(
            client, write_access, "set_shopping_item_checked", {"item_id": other_item_id, "checked": True}
        ).json()["result"]["isError"]
        for name, arguments in (
            ("delete_shopping_item", {"item_id": other_item_id}),
            ("set_all_shopping_items_checked", {"list_id": other_list_id}),
            ("clear_checked_shopping_items", {"list_id": other_list_id}),
            ("rename_shopping_list", {"list_id": other_list_id, "name": "Wrong"}),
        ):
            assert _tool(client, write_access, name, arguments).json()["result"]["isError"], name
        assert client.get(f"/api/households/shopping/items/{other_item_id}", headers=other_auth).status_code == 200
        other_connection = client.put(connection_url, json={"scopes": ["recipes:write"]}, headers=other_auth)
        assert other_connection.status_code == 404

        with session_context() as session:
            user_model = session.get(User, UUID(profile["id"]))
            assert user_model is not None
            original_household = user_model.household_id
            user_model.household_id = UUID(other_household.json()["id"])
            session.commit()
        assert _tool(client, write_access, "get_profile").status_code == 401
        with session_context() as session:
            user_model = session.get(User, UUID(profile["id"]))
            assert user_model is not None
            user_model.household_id = original_household
            user_model.locked_at = utcnow()
            session.commit()
        assert _tool(client, write_access, "get_profile").status_code == 401
        with session_context() as session:
            user_model = session.get(User, UUID(profile["id"]))
            assert user_model is not None
            user_model.locked_at = None
            original_valid_after = user_model.tokens_valid_after
            user_model.tokens_valid_after = utcnow() + timedelta(seconds=1)
            session.commit()
        assert _tool(client, write_access, "get_profile").status_code == 401
        with session_context() as session:
            user_model = session.get(User, UUID(profile["id"]))
            assert user_model is not None
            user_model.tokens_valid_after = original_valid_after
            session.commit()
        assert _tool(client, write_access, "get_profile").status_code == 200

        connections = client.get("/api/users/mcp/connections", headers=mealie_auth)
        assert connections.status_code == 200
        assert client.delete(f"/api/users/mcp/connections/{read_grant_id}", headers=mealie_auth).status_code == 200
        assert _tool(client, access, "get_profile").status_code == 401
        refresh_fields = {
            "grant_type": "refresh_token",
            "refresh_token": write_token.json()["refresh_token"],
            "client_id": client_id,
            "resource": RESOURCE,
        }
        rotated = client.post("/oauth/token", data=refresh_fields)
        assert rotated.status_code == 200, rotated.text
        reused = client.post("/oauth/token", data=refresh_fields)
        assert reused.status_code == 400
        # An immediate replay (client retry, concurrent refresh) is refused without revoking the grant
        assert _tool(client, rotated.json()["access_token"], "get_profile").status_code == 200
        with session_context() as session:
            session.query(McpToken).filter_by(token_hash=digest(refresh_fields["refresh_token"])).update(
                {McpToken.used_at: utcnow() - REFRESH_REUSE_GRACE - timedelta(seconds=1)}
            )
            session.commit()
        assert client.post("/oauth/token", data=refresh_fields).status_code == 400
        assert _tool(client, write_access, "get_profile").status_code == 401
        assert _tool(client, rotated.json()["access_token"], "get_profile").status_code == 401

        revoke_authorization = client.get("/oauth/authorize", params=auth_params, follow_redirects=False)
        revoke_consent = client.get(revoke_authorization.headers["location"])
        revoke_form = _consent_form(revoke_consent.text)
        revoke_approval = client.post(
            "/oauth/consent", data={**revoke_form, "decision": "approve"}, follow_redirects=False
        )
        revoke_code = parse_qs(urlsplit(revoke_approval.headers["location"]).query)["code"][0]
        revoke_tokens = client.post("/oauth/token", data={**token_fields, "code": revoke_code})
        assert revoke_tokens.status_code == 200, revoke_tokens.text
        revoke_access = revoke_tokens.json()["access_token"]
        assert _tool(client, revoke_access, "get_profile").status_code == 200
        revocation = client.post(
            "/oauth/revoke",
            data={"token": revoke_access, "token_type_hint": "access_token", "client_id": client_id},
        )
        assert revocation.status_code == 200, revocation.text
        assert _tool(client, revoke_access, "get_profile").status_code == 401
        assert (
            client.post(
                "/oauth/token",
                data={**refresh_fields, "refresh_token": revoke_tokens.json()["refresh_token"]},
            ).status_code
            == 400
        )
        assert client.put("/api/admin/mcp", json={"enabled": False}, headers=mealie_auth).status_code == 200
        assert _tool(client, write_access, "get_profile").status_code == 404
        assert client.get("/.well-known/oauth-authorization-server").status_code == 404


def test_http_base_url_does_not_prevent_mealie_startup(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            """from mealie.app import app
from mealie.mcp.oauth import validate_enablement_url
assert app is not None
try:
    validate_enablement_url()
except ValueError:
    pass
else:
    raise AssertionError('Remote HTTP must not enable MCP')
""",
        ],
        env={
            **os.environ,
            "BASE_URL": "http://mealie.example.com",
            "DATA_DIR": str(tmp_path),
            "PRODUCTION": "True",
            "TESTING": "True",
        },
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    assert result.returncode == 0, result.stderr
