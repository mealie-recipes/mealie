<template>
  <RecipeDialogAddToShoppingList
    v-model="shoppingListDialog"
    :recipes="[{ ...recipe, scale: 1 }]"
    :shopping-lists="shoppingLists"
  />

  <v-card v-if="!dismissed" variant="tonal" class="mb-4 d-print-none">
    <v-card-title class="d-flex align-center ga-2 text-subtitle-1">
      <v-icon>{{ $globals.icons.cartCheck }}</v-icon>
      {{ $t("recipe.pantry-check") }}
      <v-spacer />
      <v-btn
        :aria-label="$t('recipe.pantry-dismiss')"
        :title="$t('recipe.pantry-dismiss')"
        :icon="$globals.icons.close"
        size="small"
        variant="text"
        @click="dismissed = true"
      />
    </v-card-title>
    <v-card-text class="pt-0">
      <div v-if="onHandFoods.length || neededIngredients.length" class="d-flex flex-wrap ga-2 mb-2">
        <v-chip v-if="onHandFoods.length" color="success" size="small">
          {{ $t("recipe.pantry-on-hand-count", onHandFoods.length) }}
        </v-chip>
        <v-chip color="primary" size="small">
          {{ $t("recipe.pantry-needed-count", neededIngredients.length) }}
        </v-chip>
      </div>

      <p v-if="neededIngredients.length" class="text-body-2">
        {{ neededIngredients.join(", ") }}
      </p>
      <p v-else-if="onHandFoods.length" class="text-body-2 text-success">
        {{ $t("recipe.pantry-all-ingredients-on-hand") }}
      </p>
      <p v-else class="text-body-2 text-medium-emphasis">
        {{ $t("recipe.pantry-parse-ingredients-description") }}
      </p>
    </v-card-text>
    <v-card-actions v-if="neededIngredients.length">
      <v-btn
        color="primary"
        variant="tonal"
        :prepend-icon="$globals.icons.cartCheck"
        :loading="shoppingListsLoading"
        @click="openShoppingLists"
      >
        {{ $t("recipe.pantry-add-needed-to-shopping-list") }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import RecipeDialogAddToShoppingList from "~/components/Domain/Recipe/RecipeDialogAddToShoppingList.vue";
import { useUserApi } from "~/composables/api";
import { alert } from "~/composables/use-toast";
import type { ShoppingListSummary } from "~/lib/api/types/household";
import type { Recipe } from "~/lib/api/types/recipe";
import { getRecipePantryStatus } from "~/lib/recipe/pantry-status";

const props = defineProps<{ recipe: Recipe }>();
const api = useUserApi();
const auth = useMealieAuth();
const { t } = useI18n();

const shoppingListDialog = ref(false);
const shoppingListsLoading = ref(false);
const shoppingLists = ref<ShoppingListSummary[]>([]);
const dismissed = ref(false);
const currentHouseholdSlug = computed(() => auth.user.value?.householdSlug || "");

const pantryStatus = computed(() => getRecipePantryStatus(props.recipe, currentHouseholdSlug.value));

const onHandFoods = computed(() => pantryStatus.value.onHandFoods);
const neededIngredients = computed(() => pantryStatus.value.neededIngredients);

async function openShoppingLists() {
  shoppingListsLoading.value = true;
  const { data, error } = await api.shopping.lists.getAll(1, -1, { orderBy: "name", orderDirection: "asc" });
  shoppingListsLoading.value = false;
  if (error || !data) {
    alert.error(t("shopping-list.failed-to-load-shopping-lists"));
    return;
  }

  shoppingLists.value = data.items || [];
  shoppingListDialog.value = true;
}
</script>
