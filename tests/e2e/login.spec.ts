import { test, expect } from '@playwright/test';

test('password login', async ({ page }) => {
    const username = "changeme@example.com"
    const password = "MyPassword"
    const name = "Change Me"

    await page.goto('/login');
    await page.getByLabel('Email or Username', { exact: true }).fill(username);
    await page.getByLabel('Password', { exact: true }).fill(password);
    await page.getByRole('button', { name: 'Login', exact: true }).click();
    // skip admin setup page
    await page.getByRole('link', { name: "I'm already set up, just bring me to the homepage" }).click();
    await expect(page.getByRole('navigation')).toContainText(name);
});

test('ldap login', async ({ page }) => {
    const username = "bender"
    const password = "bender"
    const name = "Bender Bending Rodríguez"

    await page.goto('/login');
    await page.getByLabel('Email or Username', { exact: true }).fill(username);
    await page.getByLabel('Password', { exact: true }).fill(password);
    await page.getByRole('button', { name: 'Login', exact: true }).click();
    await expect(page).toHaveURL(/\/g\/home/);
    await expect(page.getByRole('navigation')).toContainText(name);
    await expect(page.getByRole('link', { name: 'Settings' })).not.toBeVisible();
});

test('ldap admin login', async ({ page }) => {
    const username = "professor"
    const password = "professor"
    const name = "Hubert J. Farnsworth"

    await page.goto('/login');
    await page.getByLabel('Email or Username', { exact: true }).fill(username);
    await page.getByLabel('Password', { exact: true }).fill(password);
    await page.getByRole('button', { name: 'Login', exact: true }).click();
    // skip admin setup page
    await page.getByRole('link', { name: "I'm already set up, just bring me to the homepage" }).click();
    await expect(page.getByRole('navigation')).toContainText(name);
    await expect(page.getByRole('link', { name: 'Settings' })).toBeVisible();
});

test('oidc initial login', async ({ page }) => {
    const username = "testUser"
    const name = "Test User"
    const claims = {
        "sub": username,
        "email": `${username}@example.com`,
        "preferred_username": username,
        "name": name,
        "groups": ["user"]
    }

    await page.goto('/login');
    await page.getByRole('button', { name: 'Login with OAuth' }).click();
    await page.getByPlaceholder('Enter any user/subject').fill(username);
    await page.getByPlaceholder('Optional claims JSON value,').fill(JSON.stringify(claims));
    await page.getByRole('button', { name: 'Sign-in' }).click();
    await expect(page).toHaveURL(/\/g\/home/);
    await expect(page.getByRole('navigation')).toContainText(name);
    await expect(page.getByRole('link', { name: 'Settings' })).not.toBeVisible();
});

test('oidc login with user not in propery group', async ({ page }) => {
    const username = "testUserNoGroup"
    const name = "Test User No Group"
    const claims = {
        "sub": username,
        "email": `${username}@example.com`,
        "preferred_username": username,
        "name": name,
        "groups": []
    }

    await page.goto('/login');
    await page.getByRole('button', { name: 'Login with OAuth' }).click();
    await page.getByPlaceholder('Enter any user/subject').fill(username);
    await page.getByPlaceholder('Optional claims JSON value,').fill(JSON.stringify(claims));
    await page.getByRole('button', { name: 'Sign-in' }).click();
    await expect(page).toHaveURL(/\/login\?direct=1/);
    await expect(page.getByRole('button', { name: 'Login with OAuth' })).toBeVisible()
});

test('oidc sequential login', async ({ page }) => {
    const username = "testUser2"
    const name = "Test User 2"
    const claims = {
        "sub": username,
        "email": `${username}@example.com`,
        "preferred_username": username,
        "name": name,
        "groups": ["user"]
    }

    await page.goto('/login');
    await page.getByRole('button', { name: 'Login with OAuth' }).click();
    await page.getByPlaceholder('Enter any user/subject').fill(username);
    await page.getByPlaceholder('Optional claims JSON value,').fill(JSON.stringify(claims));
    await page.getByRole('button', { name: 'Sign-in' }).click();
    await expect(page).toHaveURL(/\/g\/home/, { timeout: 15000 });
    await expect(page.getByRole('navigation')).toContainText(name);
    await page.getByRole('button', { name: 'Logout' }).click();

    await expect(page).toHaveURL(/\/login\?direct=1/);
    await page.getByRole('button', { name: 'Login with OAuth' }).click();
    await page.getByPlaceholder('Enter any user/subject').fill(username);
    await page.getByPlaceholder('Optional claims JSON value,').fill(JSON.stringify(claims));
    await page.getByRole('button', { name: 'Sign-in' }).click();
    await expect(page.getByRole('navigation')).toContainText(name, { timeout: 15000 });
});

test('settings page verify oidc', async ({ page }) => {
    const username = "oidcUser"
    const name = "OIDC User"
    const claims = {
        "sub": username,
        "email": `${username}@example.com`,
        "preferred_username": username,
        "name": name,
        "groups": ["user"]
    }

    await page.goto('/login');
    await page.getByRole('button', { name: 'Login with OAuth' }).click();
    await page.getByPlaceholder('Enter any user/subject').fill(username);
    await page.getByPlaceholder('Optional claims JSON value,').fill(JSON.stringify(claims));
    await page.getByRole('button', { name: 'Sign-in' }).click();
    await expect(page.getByRole('navigation')).toContainText(name);
    await page.getByRole('button', { name: 'Logout' }).click();

    await expect(page).toHaveURL(/\/login\?direct=1/);
    await page.getByLabel('Email or Username').click();
    await page.getByLabel('Email or Username').fill('changeme@example.com');
    await page.getByLabel('Password', { exact: true }).click();
    await page.getByLabel('Password', { exact: true }).fill('MyPassword');
    await page.getByRole('button', { name: 'Login', exact: true }).click();
    // skip admin setup page
    await expect(page).toHaveURL(/\/admin\/setup/, { timeout: 15000 });
    await page.getByRole('link', { name: "I'm already set up, just bring me to the homepage" }).click();
    await expect(page).toHaveURL(/\/g\/home/);
    // validate user settings
    await page.goto('/admin/manage/users');
    await page.getByRole('cell', { name: username, exact: true }).click();
    await expect(page.getByText('Administrator')).toBeVisible();
});

test('oidc admin user', async ({ page }) => {
    const username = "oidcAdmin"
    const name = "OIDC Admin"
    const claims = {
        "sub": username,
        "email": `${username}@example.com`,
        "preferred_username": username,
        "name": name,
        "groups": ["user", "admin"]
    }

    await page.goto('/login');
    await page.getByRole('button', { name: 'Login with OAuth' }).click();
    await page.getByPlaceholder('Enter any user/subject').fill(username);
    await page.getByPlaceholder('Optional claims JSON value,').fill(JSON.stringify(claims));
    await page.getByRole('button', { name: 'Sign-in' }).click();
    // skip admin setup page
    await expect(page).toHaveURL(/\/admin\/setup/, { timeout: 15000 });
    await page.getByRole('link', { name: "I'm already set up, just bring me to the homepage" }).click();
    await expect(page.getByRole('navigation')).toContainText(name);
    await expect(page.getByRole('link', { name: 'Settings' })).toBeVisible();
});
