<template>
  <div>
    <BaseDialog
      v-model="discardDialog"
      bottom-sheet
      :title="$t('general.discard-changes')"
      color="warning"
      :icon="$globals.icons.alertCircle"
      can-confirm
      @confirm="confirmDiscard"
      @cancel="cancelDiscard"
    >
      <v-card-text>
        {{ $t("general.discard-changes-description") }}
      </v-card-text>
    </BaseDialog>
    <RecipePageParseDialog
      :model-value="isParsing"
      :ingredients="recipe.recipeIngredient"
      :width="$vuetify.display.smAndDown ? '100%' : '80%'"
      @update:model-value="toggleIsParsing"
      @save="saveParsedIngredients"
    />
    <!-- Editor -->
    <div v-if="isEditMode" key="recipe-edit" class="recipe-edit">
      <RecipePageEditBar
        ref="recipeToolbar"
        :recipe="recipe"
        @save="saveRecipe"
        @delete="deleteRecipe"
        @close="closeEditor"
      />
      <div class="recipe-edit__body d-print-none">
        <section v-if="isEditJSON" class="recipe-edit__card mealie-card">
          <RecipeJsonEditor
            v-model="recipe"
            mode="text"
            :main-menu-bar="false"
          />
        </section>
        <template v-else>
          <section class="recipe-edit__card mealie-card">
            <h2 class="recipe-edit__heading">
              {{ $t("recipe-edit.details") }}
            </h2>
            <div class="recipe-edit__details">
              <div class="recipe-edit__photo-column">
                <div class="recipe-edit__photo mealie-photo-placeholder">
                  <img
                    v-if="recipe.image && !editImageFailed"
                    :key="imageKey"
                    :src="recipeImage(recipe.id, recipe.image, imageKey)"
                    alt=""
                    @error="editImageFailed = true"
                  >
                </div>
                <RecipePageEditorToolbar v-model="recipe" class="recipe-edit__photo-tools" />
              </div>
              <RecipePageInfoEditor v-model="recipe" class="recipe-edit__fields" />
            </div>
          </section>

          <section class="recipe-edit__card mealie-card">
            <RecipePageIngredientEditor v-model="recipe" />
          </section>

          <section class="recipe-edit__card mealie-card">
            <RecipePageInstructions
              v-model="recipe.recipeInstructions"
              v-model:assets="recipe.assets"
              :recipe="displayedRecipe"
              :scale="scale"
              :ingredient-storage-key="ingredientStorageKey"
            />
            <div class="d-flex justify-end ga-2 mt-2">
              <RecipeDialogBulkAdd @bulk-data="addStep" />
              <BaseButton @click="addStep()">
                {{ $t("general.add") }}
              </BaseButton>
            </div>
          </section>

          <section class="recipe-edit__card mealie-card">
            <h2 class="recipe-edit__heading">
              {{ $t("recipe-edit.organize") }}
            </h2>
            <RecipePageOrganizers v-model="recipe" @item-selected="chipClicked" />
          </section>

          <section class="recipe-edit__card mealie-card">
            <h2 class="recipe-edit__heading">
              {{ $t("recipe-edit.more") }}
            </h2>
            <RecipeNotes v-model="recipe.notes" edit />
            <RecipePageFooter v-model="recipe" />
          </section>
        </template>
      </div>
    </div>
    <!-- Reading view -->
    <div v-else v-show="!isCookMode" key="recipe-view" class="recipe-view">
      <RecipePageHero :recipe="recipe" :scale="scale" />
      <div class="recipe-view__body d-print-none">
        <div class="recipe-view__columns">
          <div class="recipe-view__ingredients">
            <RecipePageIngredientToolsView
              :recipe="displayedRecipe"
              :scale="scale"
              :ingredient-storage-key="ingredientStorageKey"
            >
              <template #header-append>
                <RecipeUnitSystemButton compact :recipe="recipe" />
                <RecipePageServingsStepper v-model="scale" :recipe="recipe" />
              </template>
            </RecipePageIngredientToolsView>
            <RecipePageOrganizers v-if="$vuetify.display.mdAndUp" v-model="recipe" class="mt-6" @item-selected="chipClicked" />
          </div>
          <div class="recipe-view__method">
            <RecipePageInstructions
              v-model="recipe.recipeInstructions"
              v-model:assets="recipe.assets"
              :recipe="displayedRecipe"
              :scale="scale"
              :ingredient-storage-key="ingredientStorageKey"
            />
            <div v-if="!$vuetify.display.mdAndUp" class="mt-6">
              <RecipePageOrganizers v-model="recipe" @item-selected="chipClicked" />
            </div>
            <RecipeNotes v-model="recipe.notes" :edit="false" class="mt-6" />
          </div>
        </div>
        <RecipePageFooter v-model="recipe" class="mt-8" />
        <WakelockSwitch />
        <RecipePageComments
          v-if="!disableComments"
          v-model="recipe"
          class="px-1 my-4"
        />
      </div>
    </div>
    <RecipePrintContainer :recipe="displayedRecipe" :scale="scale" />
    <!-- Floating save button when toolbar scrolls out of view -->
    <v-fab
      v-if="isEditMode && !toolbarVisible"
      color="success"
      location="bottom end"
      size="large"
      app
      appear
      class="d-print-none"
      @click="saveRecipe"
    >
      <v-icon>{{ $globals.icons.save }}</v-icon>
      <v-tooltip activator="parent" location="left">
        {{ $t("general.save") }}
      </v-tooltip>
    </v-fab>
    <!-- Cook mode fills the window, one step at a time -->
    <RecipePageCookMode
      v-if="isCookMode"
      v-model:scale="scale"
      :recipe="displayedRecipe"
      :ingredient-storage-key="ingredientStorageKey"
      @exit="setMode(PageMode.VIEW)"
    />
  </div>
</template>

<script setup lang="ts">
import type { ComponentPublicInstance } from "vue";
import { invoke, until } from "@vueuse/core";
import type { RouteLocationNormalized } from "vue-router";
import RecipePageEditorToolbar from "./RecipePageParts/RecipePageEditorToolbar.vue";
import RecipePageFooter from "./RecipePageParts/RecipePageFooter.vue";
import RecipePageIngredientEditor from "./RecipePageParts/RecipePageIngredientEditor.vue";
import RecipePageIngredientToolsView from "./RecipePageParts/RecipePageIngredientToolsView.vue";
import RecipePageInstructions from "./RecipePageParts/RecipePageInstructions.vue";
import RecipePageOrganizers from "./RecipePageParts/RecipePageOrganizers.vue";
import RecipePageParseDialog from "./RecipePageParts/RecipeParseDialog/RecipePageParseDialog.vue";
import RecipePageInfoEditor from "./RecipePageParts/RecipePageInfoEditor.vue";
import RecipePageComments from "./RecipePageParts/RecipePageComments.vue";
import RecipePageCookMode from "./RecipePageParts/RecipePageCookMode.vue";
import RecipePageHero from "./RecipePageParts/RecipePageHero.vue";
import RecipePageEditBar from "./RecipePageParts/RecipePageEditBar.vue";
import RecipePageServingsStepper from "./RecipePageParts/RecipePageServingsStepper.vue";
import RecipeUnitSystemButton from "~/components/Domain/Recipe/RecipeUnitSystemButton.vue";
import RecipePrintContainer from "~/components/Domain/Recipe/RecipePrintContainer.vue";
import {
  clearPageState,
  PageMode,
  usePageState,
} from "~/composables/recipe-page/shared-state";
import { useCookModeQuery, type BooleanString } from "~/composables/recipe-page/use-cook-mode-query";
import type { NoUndefinedField } from "~/lib/api/types/non-generated";
import type { Recipe, RecipeCategory, RecipeIngredient, RecipeTag, RecipeTool } from "~/lib/api/types/recipe";
import { useRouteQuery } from "~/composables/use-router";
import { useStaticRoutes, useUserApi } from "~/composables/api";
import { uuid4, deepCopy } from "~/composables/use-utils";
import RecipeDialogBulkAdd from "~/components/Domain/Recipe/RecipeDialogBulkAdd.vue";
import RecipeNotes from "~/components/Domain/Recipe/RecipeNotes.vue";
import { useLoggedInState } from "~/composables/use-logged-in-state";
import { useNavigationWarning } from "~/composables/use-navigation-warning";
import { useUnitConversion, useUnitSystem } from "~/composables/recipes";
import { useHouseholdSelf } from "~/composables/use-households";

const recipe = defineModel<NoUndefinedField<Recipe>>({ required: true });

const auth = useMealieAuth();
const route = useRoute();
const { isOwnGroup } = useLoggedInState();

const { household } = useHouseholdSelf();

const disableComments = computed(() =>
  household.value?.preferences?.recipeDisableComments
  || recipe.value?.settings?.disableComments
  || false,
);

const groupSlug = computed(() => (route.params.groupSlug as string) || auth.user?.value?.groupSlug || "");
const ingredientStorageKey = computed(() => `recipe-ingredients:${recipe.value.id || recipe.value.slug}:checked`);

const router = useRouter();
const api = useUserApi();
const { pageMode, setMode, isEditJSON, isCookMode, isEditMode, isParsing, toggleIsParsing, imageKey }
  = usePageState(recipe.value.slug);
const { recipeImage } = useStaticRoutes();
const editImageFailed = ref(false);
watch(() => [recipe.value.image, imageKey.value], () => {
  editImageFailed.value = false;
});
const { deactivateNavigationWarning } = useNavigationWarning();
const scale = ref(1);

const { unitSystem } = useUnitSystem();
const { convertIngredient } = useUnitConversion();

/**
 * The recipe as the reader asked to see it — the recipe itself unless they've opted into a unit
 * system. Cook mode, print and the ingredient list all read this, so they convert together.
 *
 * Returns `recipe` by identity whenever nothing is being converted, and always does so in edit
 * mode. That is load-bearing rather than cosmetic: `recipe` is a defineModel the editors below
 * mutate in place, so handing them a derived copy would silently drop edits. Conversion is
 * display-only and never reaches anything that saves.
 */
const displayedRecipe = computed<NoUndefinedField<Recipe>>(() => {
  if (isEditMode.value || !unitSystem.value) {
    return recipe.value;
  }

  return {
    ...recipe.value,
    recipeIngredient: recipe.value.recipeIngredient.map(
      ingredient => convertIngredient(ingredient, unitSystem.value!, scale.value),
    ),
  };
});

/** =============================================================
 * Floating save button — track toolbar visibility
 */
const recipeToolbar = ref<ComponentPublicInstance | null>(null);
const toolbarVisible = ref(true);
let toolbarObserver: IntersectionObserver | undefined;

// the editor's toolbar only exists in edit mode, so start watching it whenever it appears
watch(recipeToolbar, async (toolbar) => {
  toolbarObserver?.disconnect();
  toolbarVisible.value = true;
  await nextTick();
  const el = toolbar?.$el as HTMLElement | undefined;
  if (!el) return;
  toolbarObserver = new IntersectionObserver(
    ([entry]) => { toolbarVisible.value = entry.isIntersecting; },
    { threshold: 0 },
  );
  toolbarObserver.observe(el);
}, { flush: "post" });

onUnmounted(() => toolbarObserver?.disconnect());

/** =============================================================
 * Recipe Snapshot on Mount
 * this is used to determine if the recipe has been changed since the last save
 * and prompts the user to save if they have unsaved changes.
 */
const originalRecipe = ref<Recipe | null>(null);
const discardDialog = ref(false);
const pendingRoute = ref<RouteLocationNormalized | null>(null);

invoke(async () => {
  await until(recipe.value).not.toBeNull();
  originalRecipe.value = deepCopy(recipe.value);
});

function hasUnsavedChanges(): boolean {
  if (originalRecipe.value === null) {
    return false;
  }
  return JSON.stringify(recipe.value) !== JSON.stringify(originalRecipe.value);
}

function restoreOriginalRecipe() {
  if (originalRecipe.value) {
    recipe.value = deepCopy(originalRecipe.value) as NoUndefinedField<Recipe>;
  }
}

function closeEditor() {
  if (hasUnsavedChanges()) {
    pendingRoute.value = null;
    discardDialog.value = true;
  }
  else {
    setMode(PageMode.VIEW);
  }
}

function confirmDiscard() {
  restoreOriginalRecipe();
  discardDialog.value = false;

  if (pendingRoute.value) {
    const destination = pendingRoute.value;
    pendingRoute.value = null;
    router.push(destination);
  }
  else {
    setMode(PageMode.VIEW);
  }
}

function cancelDiscard() {
  discardDialog.value = false;
  pendingRoute.value = null;
}

onBeforeRouteLeave((to) => {
  if (isEditMode.value && hasUnsavedChanges()) {
    pendingRoute.value = to;
    discardDialog.value = true;
    return false;
  }
});

onUnmounted(() => {
  deactivateNavigationWarning();
  clearPageState(recipe.value.slug || "");
});
/** =============================================================
 * Set State onMounted
 */

const paramsEdit = useRouteQuery<BooleanString>("edit", "");
const paramsParse = useRouteQuery<BooleanString>("parse", "");
const paramsCook = useRouteQuery<BooleanString>("cook", "");
const { hydrateCookMode } = useCookModeQuery({
  cookQuery: paramsCook,
  isEditMode,
  pageMode,
  setMode,
});

onMounted(() => {
  if (paramsEdit.value === "true" && isOwnGroup.value) {
    setMode(PageMode.EDIT);
  }

  if (paramsParse.value === "true" && isOwnGroup.value) {
    toggleIsParsing(true);
  }

  hydrateCookMode();
});

// When set, the isEditMode watcher skips its URL cleanup because saveRecipe
// is navigating to a new slug that naturally omits ?edit=true.
const isNavigatingAfterRename = ref(false);

watch(isEditMode, (newVal) => {
  if (!newVal) {
    if (isNavigatingAfterRename.value) {
      isNavigatingAfterRename.value = false;
      return;
    }
    paramsEdit.value = undefined;
  }
});

watch(isParsing, () => {
  if (!isParsing.value) {
    paramsParse.value = undefined;
  }
});

/** =============================================================
 * Recipe Save Delete
 */

async function saveRecipe() {
  const { data, error } = await api.recipes.updateOne(route.params.slug as string, recipe.value);
  if (!error) {
    if (data?.slug && data.slug !== route.params.slug) {
      isNavigatingAfterRename.value = true;
    }
    setMode(PageMode.VIEW);
  }
  if (data?.slug) {
    recipe.value = data as NoUndefinedField<Recipe>;
    originalRecipe.value = deepCopy(recipe.value);
    if (data.slug !== route.params.slug) {
      router.replace(`/g/${groupSlug.value}/r/` + data.slug);
    }
  }
}

async function saveParsedIngredients(ingredients: NoUndefinedField<RecipeIngredient[]>) {
  const returnToEdit = isEditMode.value;
  recipe.value.recipeIngredient = ingredients;
  await saveRecipe();
  toggleIsParsing(false);
  if (returnToEdit) {
    setMode(PageMode.EDIT);
  }
}

async function deleteRecipe() {
  const { data } = await api.recipes.deleteOne(recipe.value.slug);
  if (data?.slug) {
    router.push(`/g/${groupSlug.value}`);
  }
}

/** =============================================================
 * Bulk Step Editor
 * TODO: Move to RecipePageInstructions component
 */

function addStep(steps: Array<string> | null = null) {
  if (!recipe.value.recipeInstructions) {
    return;
  }

  if (steps) {
    const cleanedSteps = steps.map((step) => {
      return { id: uuid4(), text: step, title: "", summary: "", ingredientReferences: [], noteReferences: [] };
    });

    recipe.value.recipeInstructions.push(...cleanedSteps);
  }
  else {
    recipe.value.recipeInstructions.push({
      id: uuid4(),
      text: "",
      title: "",
      summary: "",
      ingredientReferences: [],
      noteReferences: [],
    });
  }
}

/** =============================================================
 * RecipeChip Clicked
 */

function chipClicked(item: RecipeTag | RecipeCategory | RecipeTool, itemType: string) {
  if (!item.id) {
    return;
  }
  router.push(`/g/${groupSlug.value}?${itemType}=${item.id}`);
}

// expose to template
// (all variables used in template are top-level in <script setup>)
</script>

<style lang="css">
.recipe-edit {
  padding-bottom: 96px;
}

.recipe-edit__body {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 1100px;
  margin: 0 auto;
  padding: 28px 32px 0;
}

.recipe-edit__card {
  padding: 24px 28px;
}

.recipe-edit__heading {
  margin: 0 0 16px;
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--mealie-ink);
}

.recipe-edit__details {
  display: grid;
  grid-template-columns: minmax(0, 320px) minmax(0, 1fr);
  gap: 32px;
}

.recipe-edit__photo {
  position: relative;
  aspect-ratio: 4 / 3;
  border-radius: 18px;
  overflow: hidden;
}

.recipe-edit__photo img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.recipe-edit__photo-tools {
  margin-top: 8px;
}

/* the owner picker sits under the photo rather than out to the side */
.recipe-edit__photo-tools .v-spacer {
  display: none;
}

.recipe-edit__photo-tools .v-select {
  flex-basis: 100%;
  max-width: none !important;
}

/* calmer fields: soft filled boxes instead of underlines, sized to the page's type */
.recipe-edit .v-field--variant-underlined,
.recipe-edit .v-field--variant-filled {
  --v-field-padding-start: 12px;
  --v-field-padding-end: 12px;
  border-radius: 10px;
  background: var(--mealie-fill-subtle);
}

/* the outline also carries the floating label, so only its lines are hidden */
.recipe-edit .v-field--variant-underlined .v-field__outline::before,
.recipe-edit .v-field--variant-underlined .v-field__outline::after,
.recipe-edit .v-field--variant-filled .v-field__outline::before,
.recipe-edit .v-field--variant-filled .v-field__outline::after {
  border-color: transparent !important;
}

/* labels and text share the box's inner padding */
.recipe-edit .v-field--variant-underlined .v-field-label {
  margin-inline-start: 12px;
}

.recipe-edit .v-field--variant-underlined .v-field-label--floating {
  top: 14px;
}

.recipe-edit .v-field--variant-underlined .v-field__input,
.recipe-edit .v-field--variant-underlined .v-text-field__prefix,
.recipe-edit .v-field--variant-underlined .v-text-field__suffix {
  padding-top: 24px;
  padding-bottom: 6px;
}

/* the editors' buttons, in the page's quieter colours */
.recipe-edit__photo-tools .v-btn {
  background: var(--mealie-fill-subtle) !important;
  color: var(--mealie-ink) !important;
  box-shadow: none !important;
  border-radius: 999px !important;
}

.recipe-edit .split-main,
.recipe-edit .split-dropdown {
  background: rgb(var(--v-theme-primary)) !important;
  color: #fff !important;
  box-shadow: none !important;
}

.recipe-edit .v-field--variant-underlined.v-field--focused,
.recipe-edit .v-field--variant-filled.v-field--focused {
  box-shadow: 0 0 0 2px rgba(var(--v-theme-primary), 0.45);
}

.recipe-edit .v-field--variant-underlined .v-field__overlay,
.recipe-edit .v-field--variant-filled .v-field__overlay {
  opacity: 0 !important;
}

/* steps sit inside a card already, so their own cards drop the shadow for a hairline */
.recipe-edit .list-group-item > .v-card {
  border-radius: 16px !important;
  background: var(--mealie-canvas) !important;
  box-shadow: inset 0 0 0 1px var(--mealie-hairline-strong) !important;
}

/* the editors' own headings, matched to the cards' */
.recipe-edit h2.text-h5,
.recipe-edit .method-title {
  font-size: 22px !important;
  font-weight: 700 !important;
  letter-spacing: -0.02em;
  opacity: 1 !important;
  color: var(--mealie-ink);
}

@media (max-width: 960px) {
  .recipe-edit__body {
    padding: 20px 16px 0;
  }

  .recipe-edit__card {
    padding: 20px 16px;
  }

  .recipe-edit__details {
    grid-template-columns: minmax(0, 1fr);
    gap: 20px;
  }
}

.recipe-view {
  max-width: 1360px;
  margin: 0 auto;
  padding-bottom: 72px;
}

.recipe-view__body {
  padding: 36px 48px 0;
}

.recipe-view__columns {
  display: grid;
  grid-template-columns: minmax(0, 360px) minmax(0, 1fr);
  gap: 56px;
}

@media (max-width: 960px) {
  .recipe-view__body {
    padding: 28px 24px 0;
  }

  .recipe-view__columns {
    grid-template-columns: minmax(0, 1fr);
    gap: 36px;
  }
}

@media (max-width: 600px) {
  .recipe-view__body {
    padding: 24px 16px 0;
  }
}

.flip-list-move {
  transition: transform 0.5s;
}

.no-move {
  transition: transform 0s;
}

.ghost {
  opacity: 0.5;
}

.list-group {
  min-height: 38px;
}

.list-group-item i {
  cursor: pointer;
}
</style>
