# MCP and OAuth

Mealie includes an optional Model Context Protocol (MCP) server with OAuth authorization.
Compatible AI clients can access recipes, meal plans, and shopping lists through your Mealie server.

## Why OAuth matters

OAuth lets you approve access with your Mealie account and choose which permissions a client receives.
You can change permissions or revoke a connection without a new API token for every client.
Each connection belongs to one user and household.

Remote connectors let desktop clients, such as ChatGPT and Dot, access Mealie through HTTPS.
The client must support remote MCP and the OAuth flow that Mealie provides.
For example, you can ask a client to find recipes and add items to your household shopping list.

You do not need a local Claude Code or Codex process, an MCP bridge, or a separate identity provider.
Mealie serves the MCP tools in its existing backend process.
Your AI client or provider supplies the model; Mealie does not run a local model.
Client subscriptions, model costs, and connector availability remain subject to the client's requirements.

## Enable MCP

1. Set `BASE_URL` to your public HTTPS Mealie URL.
2. Sign in as an administrator.
3. Open **Site Settings** and enable MCP.
4. Copy the MCP URL from that page.

The URL normally has the form `https://mealie.example.com/mcp`.
MCP starts disabled. Production instances require HTTPS.
Local development and tests can use an HTTP loopback address.
The client must be able to reach your Mealie server.
Allow OAuth discovery and `/oauth` requests through your reverse proxy, as well as `/mcp` requests.

## Connect a client

1. Add a remote MCP connection in your client's connector settings.
2. Enter the MCP URL from Mealie.
3. Select OAuth if the client asks for an authentication method.
4. Sign in to Mealie in the browser.
5. Check the client name and requested permissions.
6. Approve the connection.

Mealie supports dynamic client registration and HTTPS Client ID Metadata Documents.
Public clients use authorization codes with PKCE S256.
Native clients can use loopback callbacks with different local ports.
See the [ChatGPT authentication documentation](https://developers.openai.com/plugins/build/auth) for that client's OAuth requirements.

## Permissions and account controls

Read permissions start selected. Write permissions require explicit consent.
The profile permission identifies the account and remains required.
Separate scopes control recipe, meal plan, and shopping list read and write access.

Open **User Profile → Connected Apps** to change a connection's permissions or revoke it.
Changes apply to subsequent requests, including requests with an existing access token.
Account removal, credential resets, and household changes also invalidate affected access.
The administrator can disable MCP for the whole instance without disabling the normal Mealie API.

## Available tools

- Account profile identification.
- Recipe search, retrieval, creation, and name or description changes.
- Meal plan retrieval, new entries, and entry changes.
- Shopping list retrieval, creation, and name changes.
- Shopping item addition, changes, deletion, and checked-state controls.

The server checks OAuth scopes and Mealie permissions before each operation.
It does not expose every REST endpoint as an MCP tool.
Access tokens expire after 15 minutes. Refresh tokens expire after 30 days and rotate on use.
Mealie stores token hashes and encrypts registered client secrets with a key derived from its application secret.
Keep that secret stable across restarts so existing client credentials remain usable.
