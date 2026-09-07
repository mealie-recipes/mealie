import { createHash, randomBytes } from 'node:crypto';
import { test, expect } from '@playwright/test';

// Native (mobile/desktop) OIDC flow: the client owns PKCE + state and captures the redirect
// itself; the server exchanges the code without a browser session cookie. Verified end-to-end
// against the mock-oauth2-server from docker-compose, mirroring the web OIDC tests in login.spec.ts.

const REDIRECT_URI = 'http://localhost:9999/native-callback';
const NATIVE_CONFIG_URL = '/api/auth/oauth/native/config';
const NATIVE_TOKEN_URL = '/api/auth/oauth/native/token';

test('oidc native flow exchanges an app-captured code for a mealie token', async ({ page, request }) => {
    const configResp = await request.get(NATIVE_CONFIG_URL);
    expect(configResp.status()).toBe(200);
    const config = await configResp.json();

    // The native client generates its own PKCE pair, state, and nonce.
    const codeVerifier = randomBytes(32).toString('base64url');
    const codeChallenge = createHash('sha256').update(codeVerifier).digest('base64url');
    const state = 'native-state';
    const nonce = 'native-nonce';

    const username = 'nativeUser';
    const claims = {
        sub: username,
        email: `${username}@example.com`,
        email_verified: true,
        preferred_username: username,
        name: 'Native User',
        groups: ['user'],
    };

    const authUrl =
        `${config.authorization_endpoint}?response_type=code` +
        `&client_id=${encodeURIComponent(config.client_id)}` +
        `&redirect_uri=${encodeURIComponent(REDIRECT_URI)}` +
        `&scope=${encodeURIComponent(config.scope)}` +
        `&state=${state}&nonce=${nonce}` +
        `&code_challenge=${codeChallenge}&code_challenge_method=S256`;

    // Capture the redirect URL. The browser will navigate to localhost:9999 (nothing listening)
    // and show a connection error — that's fine. We only need the code from the URL, which
    // page.on('request') captures before the network failure.
    let capturedUrl = '';
    page.on('request', (req) => {
        if (req.url().startsWith(REDIRECT_URI)) {
            capturedUrl = req.url();
        }
    });

    await page.goto(authUrl);
    await page.getByPlaceholder('Enter any user/subject').fill(username);
    await page.getByPlaceholder('Optional claims JSON value,').fill(JSON.stringify(claims));
    await page.getByRole('button', { name: 'Sign-in' }).click();

    await expect.poll(() => capturedUrl).toContain('code=');
    const code = new URL(capturedUrl).searchParams.get('code');

    const tokenResp = await request.post(NATIVE_TOKEN_URL, {
        data: { code, code_verifier: codeVerifier, redirect_uri: REDIRECT_URI, nonce },
    });
    expect(tokenResp.status()).toBe(200);

    const token = await tokenResp.json();
    expect(token.access_token).toBeTruthy();

    // The minted token is a usable Mealie token.
    const selfResp = await request.get('/api/users/self', {
        headers: { Authorization: `Bearer ${token.access_token}` },
    });
    expect(selfResp.status()).toBe(200);
    expect((await selfResp.json()).username).toBe(username);
});

test('oidc native token rejects an invalid authorization code', async ({ request }) => {
    const resp = await request.post(NATIVE_TOKEN_URL, {
        data: {
            code: 'invalid-code',
            code_verifier: 'invalid-verifier',
            redirect_uri: REDIRECT_URI,
        },
    });
    expect(resp.status()).toBe(401);
});
