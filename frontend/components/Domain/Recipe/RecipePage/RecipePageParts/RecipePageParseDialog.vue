<template>
  <BaseDialog
    :model-value="modelValue"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <v-container class="pa-2 ma-0" style="background-color: rgb(var(--v-theme-background));">
      <BaseCardSectionTitle :title="$t('recipe.parser.ingredient-parser')">
        <div class="d-flex align-center">
          <div class="my-auto">
            {{ $t("recipe.parser.select-parser") }}
          </div>
          <BaseOverflowButton
            v-model="parser"
            :disabled="parserLoading"
            btn-class="mx-2 my-auto"
            :items="availableParsers"
          />
          <v-btn
            icon
            size="40"
            color="info"
            class="ml-auto"
            :disabled="parserLoading"
            @click="parseIngredients"
          >
            <v-icon>{{ $globals.icons.refresh }}</v-icon>
          </v-btn>
        </div>
      </BaseCardSectionTitle>
      <AppLoader v-if="parserLoading" waiting-text="" class="my-6" />
    </v-container>
  </BaseDialog>
</template>

<script setup lang="ts">
import type { RecipeIngredient } from "~/lib/api/types/recipe";
import type { Parser } from "~/lib/api/user/recipes/recipe";
import type { NoUndefinedField } from "~/lib/api/types/non-generated";
import { useAppInfo, useUserApi } from "~/composables/api";
import { useGlobalI18n } from "~/composables/use-global-i18n";
import { useParsingPreferences } from "~/composables/use-users/preferences";

const props = defineProps<{
  modelValue: boolean;
  ingredients: NoUndefinedField<RecipeIngredient[]>;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: boolean): void;
  (e: "update:ingredients", value: NoUndefinedField<RecipeIngredient[]>): void;
}>();

const i18n = useGlobalI18n();
const api = useUserApi();
const appInfo = useAppInfo();

const parserPreferences = useParsingPreferences();
const parser = ref<Parser>(parserPreferences.value.parser || "nlp");
const availableParsers = computed(() => {
  return [
    {
      text: i18n.t("recipe.parser.natural-language-processor"),
      value: "nlp",
    },
    {
      text: i18n.t("recipe.parser.brute-parser"),
      value: "brute",
    },
    {
      text: i18n.t("recipe.parser.openai-parser"),
      value: "openai",
      hide: !appInfo.value?.enableOpenai,
    },
  ];
});

const parserLoading = ref(true);
async function parseIngredients() {
  if (!props.ingredients || props.ingredients.length === 0) {
    parserLoading.value = false;
    return;
  }
  parserLoading.value = true;
  try {
    const ingsAsString = props.ingredients.map(ing => ing.display ?? "");
    const { data, error } = await api.recipes.parseIngredients(parser.value, ingsAsString);
    if (error) {
      throw new Error("Failed to parse ingredients");
    } else {
      console.log(data); // TODO: use parsed data
    }
  } catch (error) {
    console.error("Error parsing ingredients:", error);
  } finally {
    parserLoading.value = false;
  }
}

onMounted(() => {
  parseIngredients();
});

watch(parser, () => {
  parseIngredients();
});

</script>
