import { Recipe, Ingredient, UserPreferences } from '@/store/types';

// Helper to generate a unique ID
const generateId = () => Math.random().toString(36).substr(2, 9);

export async function generateRecipesFromAI(
    ingredients: Ingredient[],
    preferences: UserPreferences
): Promise<Recipe[]> {
    // Simulate an API call delay
    await new Promise((resolve) => setTimeout(resolve, 2000));

    const availableIngredients = ingredients.filter((ing) => ing.isSelected);
    const proteins = availableIngredients.filter((i) => i.category === 'Proteins');
    const veggies = availableIngredients.filter((i) => i.category === 'Veggies');
    const carbs = availableIngredients.filter((i) => i.category === 'Carbs');

    const recipes: Recipe[] = [];

    // Generate 5 fallback dynamic recipes based strictly on selected ingredients
    for (let i = 0; i < 5; i++) {
        // Pick random ingredients from what's available
        const mainProtein = proteins.length > 0 ? proteins[Math.floor(Math.random() * proteins.length)] : null;
        const mainVeggie = veggies.length > 0 ? veggies[Math.floor(Math.random() * veggies.length)] : null;
        const mainCarb = carbs.length > 0 ? carbs[Math.floor(Math.random() * carbs.length)] : null;

        if (!mainProtein && !mainVeggie && !mainCarb) {
            // If none selected somehow, skip generating specific complex meals
            break;
        }

        const titleParts = [];
        if (mainProtein) titleParts.push(`Roasted ${mainProtein.name}`);
        if (mainVeggie) titleParts.push(`with ${mainVeggie.name}`);
        if (mainCarb) titleParts.push(`over ${mainCarb.name}`);

        const title = titleParts.length > 0 ? titleParts.join(' ') : 'Simple Quick Meal';

        const recipeIngredients = [];
        if (mainProtein) recipeIngredients.push({ ingredientId: mainProtein.id, name: mainProtein.name, quantity: 200, unit: 'g' });
        if (mainVeggie) recipeIngredients.push({ ingredientId: mainVeggie.id, name: mainVeggie.name, quantity: 150, unit: 'g' });
        if (mainCarb) recipeIngredients.push({ ingredientId: mainCarb.id, name: mainCarb.name, quantity: 100, unit: 'g' });

        // Ensure we respect the user's cook time preference by scaling the mock time
        const prepTime = Math.max(15, Math.min(preferences.cookTimeMinutes, 15 + Math.floor(Math.random() * 20)));
        const tags = [];
        if (preferences.batchCookMode) tags.push('Batch Friendly');
        if (prepTime <= 30) tags.push('Quick Meal');
        if (mainProtein) tags.push('High Protein');

        recipes.push({
            id: generateId(),
            title,
            description: `A delicious, customized meal tailored strictly to your pantry. Features ${mainProtein?.name || 'fresh ingredients'} as the star.`,
            prepTimeMinutes: prepTime,
            ingredients: recipeIngredients,
            instructions: [
                `Preheat your pan or oven.`,
                `Prepare the ${mainProtein?.name || 'main ingredients'} with your favorite selected spices.`,
                `Cook until perfectly tender (approx. ${Math.floor(prepTime / 2)} mins).`,
                `Serve hot and enjoy!`,
            ],
            // Using a generic placeholder image
            imageUrl: `https://picsum.photos/seed/${Math.random()}/400/300`,
            tags,
        });
    }

    return recipes;
}
