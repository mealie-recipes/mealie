import { test, expect } from '@playwright/test';

test('oidc-login', async ({ page }) => {
    const claims = {
        "sub": "testUser",
        "email": "test@example.com",
        "preferred_username": "test",
        "name": "Test User"
    }

    await page.goto('http://localhost:8081/login');
    await page.getByRole('button', { name: 'Login with OIDC' }).click();
    await page.getByPlaceholder('Enter any user/subject').fill('testUser');
    await page.getByPlaceholder('Optional claims JSON value,').fill(JSON.stringify(claims));
    await page.getByRole('button', { name: 'Sign-in' }).click();
    await expect(page.getByRole('button', { name: 'Create', exact: true })).toBeVisible();
});
