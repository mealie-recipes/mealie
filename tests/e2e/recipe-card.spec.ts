import { test, expect, Page } from '@playwright/test';

const username = "changeme@example.com"
const password = "MyPassword"

// cards with and without tags must keep their actions (favorite, rating, menu) in the same place
async function actionsOffset(page: Page, recipeName: string) {
    const card = page.locator('.v-card', { hasText: recipeName }).first();
    const actions = card.locator('.v-card-actions');
    await expect(actions).toBeVisible();

    const cardBox = await card.boundingBox();
    const actionsBox = await actions.boundingBox();
    return actionsBox!.y - cardBox!.y;
}

for (const { name, width } of [{ name: 'desktop', width: 1400 }, { name: 'mobile', width: 400 }]) {
    test(`recipe card actions align with and without tags (${name})`, async ({ page }) => {
        await page.setViewportSize({ width, height: 1000 });

        // logging in through the API sets the session cookie for the page as well
        const login = await page.request.post('/api/auth/token', { form: { username, password } });
        expect(login.ok()).toBeTruthy();

        const suffix = `${name}-${Date.now()}`;
        const untaggedName = `Card Untagged ${suffix}`;
        const taggedName = `Card Tagged ${suffix}`;

        const untagged = await page.request.post('/api/recipes', { data: { name: untaggedName } });
        const tagged = await page.request.post('/api/recipes', { data: { name: taggedName } });
        const tag = await page.request.post('/api/organizers/tags', { data: { name: `Tag ${suffix}` } });
        const taggedSlug = await tagged.json();
        await page.request.patch(`/api/recipes/${taggedSlug}`, { data: { tags: [await tag.json()] } });

        try {
            await page.goto('/g/home');
            // Firefox lays out at sub-pixel precision, so compare to the nearest pixel
            expect(await actionsOffset(page, untaggedName)).toBeCloseTo(await actionsOffset(page, taggedName), 0);
        }
        finally {
            await page.request.delete(`/api/recipes/${await untagged.json()}`);
            await page.request.delete(`/api/recipes/${taggedSlug}`);
        }
    });
}
