<template>
  <BaseDialog
    v-model="dialog"
    width="650"
    :title="title"
    :icon="$globals.icons.organizers"
    :loading="loading"
    disable-submit-on-enter
    @cancel="cancel"
  >
    <v-card-text>
      <v-radio-group
        v-if="isBulk"
        v-model="operation"
        inline
        hide-details
        class="mb-4"
      >
        <v-radio
          value="add"
          :label="$t('recipe.add-organizers')"
        />
        <v-radio
          value="remove"
          :label="$t('recipe.remove-organizers')"
        />
      </v-radio-group>

      <RecipeOrganizerSelector
        v-model="tags"
        :selector-type="Organizer.Tag"
        :show-add="true"
      />
      <RecipeOrganizerSelector
        v-model="recipeCategory"
        :selector-type="Organizer.Category"
        :show-add="true"
      />
    </v-card-text>

    <template #card-actions>
      <BaseButton
        cancel
        :disabled="loading"
        @click="cancel"
      />
      <v-spacer />
      <BaseButton
        save
        :loading="loading"
        :disabled="!canSave"
        @click="save"
      />
    </template>
  </BaseDialog>
</template>

<script setup lang="ts">
import { alert } from "~/composables/use-toast";
import { deepCopy } from "~/composables/use-utils";
import { useUserApi } from "~/composables/api";
import type {
  BulkOrganizeRecipes,
  CategoryBase,
  Recipe,
  RecipeCategory,
  RecipeSummary,
  RecipeTag,
  TagBase,
  OrganizerOperation,
} from "~/lib/api/types/recipe";
import { Organizer } from "~/lib/api/types/non-generated";

type OrganizerDialogMode = "single" | "bulk";

interface Props {
  recipes?: Recipe[];
  mode?: OrganizerDialogMode;
}

const props = withDefaults(defineProps<Props>(), {
  mode: "single",
  recipes: () => [],
});

const emit = defineEmits<{
  saved: [recipes: RecipeSummary[]];
}>();

const dialog = defineModel<boolean>({ default: false });

const { $globals } = useNuxtApp();
const i18n = useI18n();
const api = useUserApi();

const tags = ref<RecipeTag[]>([]);
const recipeCategory = ref<RecipeCategory[]>([]);
const operation = ref<OrganizerOperation>("add");
const loading = ref(false);

const isBulk = computed(() => props.mode === "bulk");
const title = computed(() => isBulk.value ? i18n.t("recipe.organize-recipes") : i18n.t("recipe.organize-recipe"));
const canSave = computed(() => {
  if (props.recipes.length === 0 || loading.value) {
    return false;
  }

  return !isBulk.value || toTagBases(tags.value).length > 0 || toCategoryBases(recipeCategory.value).length > 0;
});

function initialize() {
  operation.value = "add";

  if (isBulk.value) {
    tags.value = [];
    recipeCategory.value = [];
    return;
  }

  const recipe = props.recipes[0];
  tags.value = deepCopy(recipe?.tags ?? []);
  recipeCategory.value = deepCopy(recipe?.recipeCategory ?? []);
}

watch(dialog, (isOpen) => {
  if (isOpen) {
    initialize();
  }
});

watch(
  () => props.recipes,
  () => {
    if (dialog.value) {
      initialize();
    }
  },
);

function cancel() {
  if (!loading.value) {
    dialog.value = false;
  }
}

function showSaveError() {
  alert.error(i18n.t("recipe.recipe-update-failed"));
}

async function save() {
  if (!canSave.value) {
    return;
  }

  loading.value = true;

  try {
    if (isBulk.value) {
      await saveBulk();
    }
    else {
      await saveOne();
    }
  }
  catch (error) {
    console.error("Failed to organize recipes", error);
    showSaveError();
  }
  finally {
    loading.value = false;
  }
}

async function saveOne() {
  const recipe = props.recipes[0];
  const recipeSlug = recipe?.slug || recipe?.id;
  if (!recipe || !recipeSlug) {
    showSaveError();
    return;
  }

  const patch = {
    tags: tags.value,
    recipeCategory: recipeCategory.value,
  };
  const { data, error } = await api.recipes.patchOne(recipeSlug, patch);
  if (error || !data) {
    showSaveError();
    return;
  }

  alert.success(i18n.t("recipe.recipe-updated"));
  dialog.value = false;
  emit("saved", [data]);
}

async function saveBulk() {
  const recipeIds = props.recipes
    .map(recipe => recipe.id)
    .filter((id): id is string => !!id);
  const selectedTags = toTagBases(tags.value);
  const selectedCategories = toCategoryBases(recipeCategory.value);

  if (recipeIds.length !== props.recipes.length) {
    showSaveError();
    return;
  }

  if (recipeIds.length === 0 || (selectedTags.length === 0 && selectedCategories.length === 0)) {
    return;
  }

  const payload: BulkOrganizeRecipes = {
    recipes: recipeIds,
    operation: operation.value,
    tags: selectedTags,
    categories: selectedCategories,
  };
  const { data, error } = await api.bulk.bulkOrganize(payload);
  if (error || !data) {
    showSaveError();
    return;
  }

  if (data.length > 0) {
    alert.success(i18n.t("recipe.recipe-updated"));
  }
  dialog.value = false;
  emit("saved", data);
}

function toTagBases(tags: RecipeTag[]): TagBase[] {
  return tags.flatMap((tag) => {
    if (!tag.id) {
      return [];
    }

    return [{ id: tag.id, name: tag.name, slug: tag.slug }];
  });
}

function toCategoryBases(categories: RecipeCategory[]): CategoryBase[] {
  return categories.flatMap((category) => {
    if (!category.id) {
      return [];
    }

    return [{ id: category.id, name: category.name, slug: category.slug }];
  });
}
</script>
