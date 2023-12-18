import { test, expect } from '@playwright/test';

test('password login', async ({ page }) => {
    await page.goto('http://localhost:9000/login');
    await page.getByLabel('Email or Username').click();
    await page.getByLabel('Email or Username').fill('changeme@example.com');
    await page.locator('div').filter({ hasText: /^Password$/ }).nth(3).click();
    await page.getByLabel('Password').fill('MyPassword');
    await page.getByRole('button', { name: 'Login', exact: true }).click();
    await expect(page.getByRole('navigation')).toContainText('Change Me');
});

test('oidc initial login', async ({ page }) => {
    const username = "testUser"
    const name = "Test User"
    const claims = {
        "sub": username,
        "email": `${username}@example.com`,
        "preferred_username": username,
        "name": name
    }

    await page.goto('http://localhost:9000/login');
    await page.getByRole('button', { name: 'Login with OIDC' }).click();
    await page.getByPlaceholder('Enter any user/subject').fill(username);
    await page.getByPlaceholder('Optional claims JSON value,').fill(JSON.stringify(claims));
    await page.getByRole('button', { name: 'Sign-in' }).click();
    await expect(page.getByRole('navigation')).toContainText(name);
});

test('oidc sequential login', async ({ page }) => {
    const username = "testUser2"
    const name = "Test User 2"
    const claims = {
        "sub": username,
        "email": `${username}@example.com`,
        "preferred_username": username,
        "name": name
    }

    await page.goto('http://localhost:9000/login');
    await page.getByRole('button', { name: 'Login with OIDC' }).click();
    await page.getByPlaceholder('Enter any user/subject').fill(username);
    await page.getByPlaceholder('Optional claims JSON value,').fill(JSON.stringify(claims));
    await page.getByRole('button', { name: 'Sign-in' }).click();
    await expect(page.getByRole('navigation')).toContainText(name);
    await page.getByRole('button', { name: 'Logout' }).click();

    await page.goto('http://localhost:9000/login');
    await page.getByRole('button', { name: 'Login with OIDC' }).click();
    await page.getByPlaceholder('Enter any user/subject').fill(username);
    await page.getByPlaceholder('Optional claims JSON value,').fill(JSON.stringify(claims));
    await page.getByRole('button', { name: 'Sign-in' }).click();
    await expect(page.getByRole('navigation')).toContainText(name);
});

test('settings page verify oidc', async ({ page }) => {
    const username = "oidcUser"
    const name = "OIDC User"
    const claims = {
        "sub": username,
        "email": `${username}@example.com`,
        "preferred_username": username,
        "name": name
    }

    await page.goto('http://localhost:9000/login');
    await page.getByRole('button', { name: 'Login with OIDC' }).click();
    await page.getByPlaceholder('Enter any user/subject').fill(username);
    await page.getByPlaceholder('Optional claims JSON value,').fill(JSON.stringify(claims));
    await page.getByRole('button', { name: 'Sign-in' }).click();
    await expect(page.getByRole('navigation')).toContainText(name);
    await page.getByRole('button', { name: 'Logout' }).click();

    await page.goto('http://localhost:9000/login');
    await page.getByLabel('Email or Username').click();
    await page.getByLabel('Email or Username').fill('changeme@example.com');
    await page.getByLabel('Password').click();
    await page.getByLabel('Password').fill('MyPassword');
    await page.getByRole('button', { name: 'Login', exact: true }).click();
    await page.getByRole('link', { name: 'Settings' }).click();
    await page.getByRole('link', { name: 'Users' }).click();
    await page.getByRole('cell', { name: username, exact: true }).click();
    await expect(page.getByText('Permissions Administrator')).toBeVisible();
});

test('oidc admin user', async ({ page }) => {
    const username = "oidcAdmin"
    const name = "OIDC Admin"
    const claims = {
        "sub": username,
        "email": `${username}@example.com`,
        "preferred_username": username,
        "name": name,
        "groups": ["admin"]
    }

    await page.goto('http://localhost:9000/login');
    await page.getByRole('button', { name: 'Login with OIDC' }).click();
    await page.getByPlaceholder('Enter any user/subject').fill(username);
    await page.getByPlaceholder('Optional claims JSON value,').fill(JSON.stringify(claims));
    await page.getByRole('button', { name: 'Sign-in' }).click();
    await expect(page.getByRole('navigation')).toContainText(name);
});
