import type { PlanEntryOut } from "~/lib/api/types/meal-plan";
import type { RecipeOut, RecipeSummary } from "~/lib/api/types/recipe";
import type {
  IngredientFoodOut,
  HouseholdPreferencesOut,
  IngredientUnitOut,
  MultiPurposeLabelSummary,
  ShoppingListItemOut,
  ShoppingListMultiPurposeLabelOut,
  ShoppingListOut,
} from "~/lib/api/types/household";
import type { GroupPreferencesOut } from "~/lib/api/types/group";
import type { ReportEntryOut } from "~/lib/api/types/reports";
import type { UserOut } from "~/lib/api/types/user";

export function makeRecipeSummary(overrides: Partial<RecipeSummary> = {}): RecipeSummary {
  return {
    id: "recipe-id",
    userId: "user-id",
    householdId: "household-id",
    groupId: "group-id",
    name: "Recipe",
    slug: "recipe",
    image: null,
    recipeServings: 0,
    recipeYieldQuantity: 0,
    recipeYield: null,
    totalTime: null,
    prepTime: null,
    performTime: null,
    totalTimeSeconds: null,
    prepTimeSeconds: null,
    performTimeSeconds: null,
    description: "",
    recipeCategory: [],
    tags: [],
    tools: [],
    rating: null,
    orgURL: null,
    dateAdded: null,
    dateUpdated: null,
    createdAt: null,
    updatedAt: null,
    ...overrides,
  };
}

export function makeRecipe(overrides: Partial<RecipeOut> = {}): RecipeOut {
  return {
    ...makeRecipeSummary(),
    recipeIngredient: [],
    recipeInstructions: [],
    nutrition: {},
    settings: {},
    assets: [],
    notes: [],
    extras: {},
    comments: [],
    ...overrides,
  };
}

export function makePlanEntry(overrides: Partial<PlanEntryOut> = {}): PlanEntryOut {
  return {
    id: 1,
    date: "2026-08-19",
    endDate: null,
    entryType: "dinner",
    title: "",
    text: "",
    recipeId: null,
    recipeScale: 1,
    groupId: "group-id",
    userId: "user-id",
    householdId: "household-id",
    recipe: null,
    updatedAt: null,
    ...overrides,
  };
}

export function makeIngredientFood(overrides: Partial<IngredientFoodOut> = {}): IngredientFoodOut {
  return {
    id: "food-id",
    name: "Food",
    pluralName: null,
    description: "",
    extras: null,
    labelId: null,
    aliases: [],
    substitutions: [],
    householdsWithIngredientFood: [],
    label: null,
    recipeCount: 0,
    createdAt: null,
    updatedAt: null,
    ...overrides,
  };
}

export function makeIngredientUnit(overrides: Partial<IngredientUnitOut> = {}): IngredientUnitOut {
  return {
    id: "unit-id",
    name: "Unit",
    pluralName: null,
    description: "",
    extras: null,
    fraction: true,
    abbreviation: "",
    pluralAbbreviation: null,
    useAbbreviation: false,
    aliases: [],
    standardQuantity: null,
    standardUnit: null,
    createdAt: null,
    updatedAt: null,
    ...overrides,
  };
}

export function makeLabel(overrides: Partial<MultiPurposeLabelSummary> = {}): MultiPurposeLabelSummary {
  return {
    id: "label-id",
    name: "Label",
    color: "#959595",
    groupId: "group-id",
    ...overrides,
  };
}

export function makeShoppingListLabelSetting(
  overrides: Partial<ShoppingListMultiPurposeLabelOut> = {},
): ShoppingListMultiPurposeLabelOut {
  return {
    id: "label-setting-id",
    shoppingListId: "shopping-list-id",
    labelId: "label-id",
    position: 0,
    label: makeLabel(),
    ...overrides,
  };
}

export function makeShoppingListItem(overrides: Partial<ShoppingListItemOut> = {}): ShoppingListItemOut {
  return {
    id: "item-id",
    shoppingListId: "shopping-list-id",
    groupId: "group-id",
    householdId: "household-id",
    quantity: 1,
    unit: null,
    food: null,
    referencedRecipe: null,
    note: "",
    display: "",
    checked: false,
    position: 0,
    foodId: null,
    labelId: null,
    unitId: null,
    extras: null,
    label: null,
    recipeReferences: [],
    createdAt: null,
    updatedAt: null,
    ...overrides,
  };
}

export function makeShoppingList(overrides: Partial<ShoppingListOut> = {}): ShoppingListOut {
  return {
    id: "shopping-list-id",
    groupId: "group-id",
    userId: "user-id",
    householdId: "household-id",
    name: "Shopping List",
    extras: null,
    createdAt: null,
    updatedAt: null,
    listItems: [],
    recipeReferences: [],
    labelSettings: [],
    ...overrides,
  };
}

export function makeUser(overrides: Partial<UserOut> = {}): UserOut {
  return {
    id: "user-id",
    username: null,
    fullName: null,
    email: "user@example.com",
    authMethod: "Mealie",
    admin: false,
    group: "group",
    household: "household",
    advanced: false,
    showAnnouncements: false,
    lastReadAnnouncement: null,
    canInvite: false,
    canManage: false,
    canManageHousehold: false,
    canOrganize: false,
    groupId: "group-id",
    groupSlug: "group",
    householdId: "household-id",
    householdSlug: "household",
    tokens: null,
    cacheKey: "cache-key",
    ...overrides,
  };
}

export function makeReportEntry(overrides: Partial<ReportEntryOut> = {}): ReportEntryOut {
  return {
    id: "entry-id",
    reportId: "report-id",
    timestamp: "2026-09-25T12:00:00Z",
    success: true,
    message: "",
    exception: "",
    ...overrides,
  };
}

export function makeHouseholdPreferences(overrides: Partial<HouseholdPreferencesOut> = {}): HouseholdPreferencesOut {
  return {
    id: "household-preferences-id",
    privateHousehold: true,
    showAnnouncements: true,
    lockRecipeEditsFromOtherHouseholds: false,
    firstDayOfWeek: 0,
    recipePublic: true,
    recipeShowNutrition: false,
    recipeShowAssets: false,
    recipeLandscapeView: false,
    recipeDisableComments: false,
    ...overrides,
  };
}

export function makeGroupPreferences(overrides: Partial<GroupPreferencesOut> = {}): GroupPreferencesOut {
  return {
    id: "group-preferences-id",
    groupId: "group-id",
    privateGroup: true,
    showAnnouncements: true,
    ...overrides,
  };
}
