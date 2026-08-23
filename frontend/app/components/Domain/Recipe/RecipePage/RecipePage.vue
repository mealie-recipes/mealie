<template>
  <div>
    <BaseDialog
      v-model="discardDialog"
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
    <v-container v-show="!isCookMode" key="recipe-page" class="px-0" :class="{ 'pa-0': $vuetify.display.smAndDown }">
      <v-card flat class="d-print-none">
        <RecipePageHeader
          ref="recipeToolbar"
          :recipe="recipe"
          :recipe-scale="scale"
          :landscape="landscape"
          @save="saveRecipe"
          @delete="deleteRecipe"
          @close="closeEditor"
        />
        <RecipeJsonEditor
          v-if="isEditJSON"
          v-model="recipe"
          class="mt-10"
          mode="text"
          :main-menu-bar="false"
        />
        <v-card-text v-else>
          <!--
            This is where most of the main content is rendered. Some components include state for both Edit and View modes
            which is why some have explicit v-if statements and others use the composition API to determine and manage
            the shared state internally.

            The global recipe object is shared down the tree of components and _is_ mutated by child components. This is
            some-what of a hack of the system and goes against the principles of Vue, but it _does_ seem to work and streamline
            a significant amount of prop management. When we move to Vue 3 and have access to some of the newer API's the plan to update this
            data management and mutation system we're using.
          -->
          <div>
            <RecipePageInfoEditor v-if="isEditMode" v-model="recipe" />
          </div>
          <div>
            <RecipePageEditorToolbar v-if="isEditForm" v-model="recipe" />
          </div>
          <div>
            <RecipePageIngredientEditor v-if="isEditForm" v-model="recipe" />
          </div>
          <div>
            <RecipePageScale v-model:scale="scale" v-model:unit-system="unitSystem" v-model:temperature-unit="temperatureUnit" :recipe="recipe" />
          </div>

          <!--
            This section contains the 2 column layout for the recipe steps and other content.
          -->
          <v-row>
            <!--
              The left column is conditionally rendered based on cook mode.
            -->
            <v-col
              v-if="!isCookMode || isEditForm"
              cols="12"
              sm="12"
              md="4"
              :class="$vuetify.display.mdAndUp ? 'border-e-thin' : null"
            >
              <RecipePageIngredientToolsView v-if="!isEditForm" :recipe="displayedRecipe" :scale="scale" class="pr-2" />
              <RecipePageOrganizers v-if="$vuetify.display.mdAndUp" v-model="recipe" class="pr-2" @item-selected="chipClicked" />
            </v-col>
            <!--
              the right column is always rendered, but it's layout width is determined by where the left column is
              rendered.
            -->
            <v-col cols="12" sm="12" :md="8 + (isCookMode ? 1 : 0) * 4">
              <RecipePageInstructions
                v-model="instructionsModel"
                v-model:assets="recipe.assets"
                :recipe="displayedRecipe"
                :scale="scale"
              />
              <div v-if="isEditForm" class="d-flex">
                <RecipeDialogBulkAdd class="ml-auto my-2 mr-1" @bulk-data="addStep" />
                <BaseButton class="my-2" @click="addStep()">
                  {{ $t("general.add") }}
                </BaseButton>
              </div>
              <div v-if="!$vuetify.display.mdAndUp">
                <RecipePageOrganizers v-model="recipe" />
              </div>
              <RecipeNotes v-model="recipe.notes" :edit="isEditForm" />
            </v-col>
          </v-row>
          <RecipePageFooter v-model="recipe" />
        </v-card-text>
      </v-card>
      <WakelockSwitch />
      <RecipePageComments
        v-if="!recipe.settings?.disableComments && !isEditForm && !isCookMode"
        v-model="recipe"
        class="px-1 my-4 d-print-none"
      />
      <RecipePrintContainer :recipe="displayedRecipe" :scale="scale" />
    </v-container>
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
    <!-- Cook mode displayes two columns with ingredients and instructions side by side, each being scrolled individually, allowing to view both at the same time -->
    <!-- The calc is to account for the navabar height (48px) -->
    <v-sheet
      v-show="isCookMode && !hasLinkedIngredients"
      key="cookmode"
      :height="$vuetify.display.smAndUp ? 'calc(100vh - 48px)' : 'auto'"
      class-name="overflow-hidden"
    >
      <!-- the calc is to account for the toolbar a more dynamic solution could be needed  -->
      <v-row style="height: 100%" no-gutters class="overflow-hidden">
        <v-col cols="12" sm="5" class="overflow-y-auto pl-4 pr-3 py-2" style="height: 100%">
          <div class="d-flex align-center">
            <RecipePageScale v-model:scale="scale" v-model:unit-system="unitSystem" v-model:temperature-unit="temperatureUnit" :recipe="recipe" />
          </div>
          <RecipePageIngredientToolsView
            v-if="!isEditForm"
            :recipe="displayedRecipe"
            :scale="scale"
            :is-cook-mode="isCookMode"
          />
          <v-divider />
        </v-col>
        <v-col
          class="overflow-y-auto"
          :class="$vuetify.display.smAndDown ? 'py-2': 'py-6'"
          style="height: 100%"
          cols="12"
          sm="7"
        >
          <h2 class="text-h5 px-4 font-weight-medium opacity-80">
            {{ $t('recipe.instructions') }}
          </h2>
          <RecipePageInstructions
            v-model="instructionsModel"
            v-model:assets="recipe.assets"
            class="overflow-y-hidden px-4"
            :recipe="displayedRecipe"
            :scale="scale"
          />
        </v-col>
      </v-row>
    </v-sheet>
    <v-sheet v-show="isCookMode && hasLinkedIngredients">
      <div class="mt-2 px-2 px-md-4">
        <RecipePageScale v-model:scale="scale" v-model:unit-system="unitSystem" v-model:temperature-unit="temperatureUnit" :recipe="recipe" />
      </div>
      <RecipePageInstructions
        v-model="instructionsModel"
        v-model:assets="recipe.assets"
        class="overflow-y-hidden mt-n5 px-2 px-md-4"
        :recipe="displayedRecipe"
        :scale="scale"
      />

      <div v-if="notLinkedIngredients.length > 0" class="px-2 px-md-4 pb-4">
        <v-divider />
        <v-card flat>
          <v-card-title>{{ $t("recipe.not-linked-ingredients") }}</v-card-title>
          <RecipeIngredients
            :value="notLinkedIngredients"
            :scale="scale"
            :is-cook-mode="isCookMode"
          />
        </v-card>
      </div>
    </v-sheet>
    <v-btn
      v-if="isCookMode"
      icon
      color="primary"
      style="position: fixed; right: 12px; top: 60px"
      @click="toggleCookMode()"
    >
      <v-icon>{{ $globals.icons.close }}</v-icon>
    </v-btn>
  </div>
</template>

<script setup lang="ts">
import type { ComponentPublicInstance } from "vue";
import { invoke, until } from "@vueuse/core";
import type { RouteLocationNormalized } from "vue-router";
import RecipeIngredients from "../RecipeIngredients.vue";
import RecipePageEditorToolbar from "./RecipePageParts/RecipePageEditorToolbar.vue";
import RecipePageFooter from "./RecipePageParts/RecipePageFooter.vue";
import RecipePageHeader from "./RecipePageParts/RecipePageHeader.vue";
import RecipePageIngredientEditor from "./RecipePageParts/RecipePageIngredientEditor.vue";
import RecipePageIngredientToolsView from "./RecipePageParts/RecipePageIngredientToolsView.vue";
import RecipePageInstructions from "./RecipePageParts/RecipePageInstructions.vue";
import RecipePageOrganizers from "./RecipePageParts/RecipePageOrganizers.vue";
import RecipePageParseDialog from "./RecipePageParts/RecipePageParseDialog.vue";
import RecipePageScale from "./RecipePageParts/RecipePageScale.vue";
import RecipePageInfoEditor from "./RecipePageParts/RecipePageInfoEditor.vue";
import RecipePageComments from "./RecipePageParts/RecipePageComments.vue";
import RecipePrintContainer from "~/components/Domain/Recipe/RecipePrintContainer.vue";
import {
  clearPageState,
  PageMode,
  usePageState,
} from "~/composables/recipe-page/shared-state";
import { useCookModeQuery, type BooleanString } from "~/composables/recipe-page/use-cook-mode-query";
import type { NoUndefinedField } from "~/lib/api/types/non-generated";
import type { Recipe, RecipeCategory, RecipeIngredient, RecipeStep, RecipeTag, RecipeTool } from "~/lib/api/types/recipe";
import type { TemperatureUnit, UnitSystem } from "~/lib/api/types/user";
import { useUnitConversion, useUnitSystem } from "~/composables/recipes";
import { useRouteQuery } from "~/composables/use-router";
import { useUserApi } from "~/composables/api";
import { uuid4, deepCopy } from "~/composables/use-utils";
import RecipeDialogBulkAdd from "~/components/Domain/Recipe/RecipeDialogBulkAdd.vue";
import RecipeNotes from "~/components/Domain/Recipe/RecipeNotes.vue";
import { useLoggedInState } from "~/composables/use-logged-in-state";
import { useNavigationWarning } from "~/composables/use-navigation-warning";

const recipe = defineModel<NoUndefinedField<Recipe>>({ required: true });

const display = useDisplay();
const auth = useMealieAuth();
const route = useRoute();
const { isOwnGroup } = useLoggedInState();

const groupSlug = computed(() => (route.params.groupSlug as string) || auth.user?.value?.groupSlug || "");

const router = useRouter();
const api = useUserApi();
const { pageMode, setMode, isEditForm, isEditJSON, isCookMode, isEditMode, isParsing, toggleCookMode, toggleIsParsing }
  = usePageState(recipe.value.slug);
const { deactivateNavigationWarning } = useNavigationWarning();
const notLinkedIngredients = computed(() => {
  // Reads the displayed recipe so this list matches the ingredient list above it; conversion
  // keeps referenceId, so the linking check is unaffected.
  return displayedRecipe.value.recipeIngredient.filter((ingredient) => {
    return !displayedRecipe.value.recipeInstructions.some(step =>
      step.ingredientReferences?.map(ref => ref.referenceId).includes(ingredient.referenceId),
    );
  });
});

/** =============================================================
 * Floating save button — track toolbar visibility
 */
const recipeToolbar = ref<ComponentPublicInstance | null>(null);
const toolbarVisible = ref(true);
let toolbarObserver: IntersectionObserver | undefined;

onMounted(async () => {
  await nextTick();
  const el = recipeToolbar.value?.$el as HTMLElement | undefined;
  if (!el) return;
  toolbarObserver = new IntersectionObserver(
    ([entry]) => { toolbarVisible.value = entry.isIntersecting; },
    { threshold: 0 },
  );
  toolbarObserver.observe(el);
});

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
const hasLinkedIngredients = computed(() => {
  return recipe.value.recipeInstructions.some(
    step => step.ingredientReferences && step.ingredientReferences.length > 0,
  );
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
  const { data, error } = await api.recipes.updateOne(recipe.value.slug, recipe.value);
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
  recipe.value.recipeIngredient = ingredients;
  await saveRecipe();
  toggleIsParsing(false);
}

async function deleteRecipe() {
  const { data } = await api.recipes.deleteOne(recipe.value.slug);
  if (data?.slug) {
    router.push(`/g/${groupSlug.value}`);
  }
}

/** =============================================================
 * View Preferences
 */
const landscape = computed(() => {
  const preferLandscape = recipe.value.settings?.landscapeView;
  const smallScreen = !display.smAndUp.value;

  if (preferLandscape) {
    return true;
  }
  else if (smallScreen) {
    return true;
  }

  return false;
});

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
      return { id: uuid4(), text: step, title: "", summary: "", ingredientReferences: [] };
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

const scale = ref(1);

/** =============================================================
 * Unit system (display only)
 *
 * The recipe in the database always keeps what its author wrote. The toggle in
 * RecipePageScale re-expresses quantities and oven temperatures on the way to the screen,
 * seeded from the user's (or their household's) preference. Substituting a single
 * `displayedRecipe` here means cook mode, the print container and the ingredient list all
 * pick the conversion up without threading the setting through every component.
 *
 * Edit mode always shows the canonical recipe, so what gets saved is what was typed.
 */
const { unitSystem: preferredUnitSystem, temperatureUnit: preferredTemperatureUnit } = useUnitSystem();
const { convertIngredients, convertInstructions } = useUnitConversion();

const unitSystem = ref<UnitSystem>(preferredUnitSystem.value);
const temperatureUnit = ref<TemperatureUnit>(preferredTemperatureUnit.value);

// The household fetch can land after this component mounts, so the preference is followed
// as it arrives — but only while the reader is still sitting on the value we last applied.
// Once they pick something in the toggle, their choice stands for the rest of the visit.
let lastApplied = { system: unitSystem.value, temperature: temperatureUnit.value };
watch([preferredUnitSystem, preferredTemperatureUnit], ([system, temperature]) => {
  if (unitSystem.value === lastApplied.system) {
    unitSystem.value = system;
  }
  if (temperatureUnit.value === lastApplied.temperature) {
    temperatureUnit.value = temperature;
  }
  lastApplied = { system, temperature };
});

const isConverted = computed(() =>
  !isEditForm.value && (unitSystem.value !== "original" || temperatureUnit.value !== "system"),
);

const displayedRecipe = computed<NoUndefinedField<Recipe>>(() => {
  if (!isConverted.value) {
    return recipe.value;
  }

  return {
    ...recipe.value,
    recipeIngredient: convertIngredients(recipe.value.recipeIngredient, unitSystem.value, scale.value),
    recipeInstructions: convertInstructions(recipe.value.recipeInstructions, unitSystem.value, temperatureUnit.value),
  } as NoUndefinedField<Recipe>;
});

/**
 * Instruction steps for RecipePageInstructions. Reads converted text in view mode and
 * writes to the canonical recipe — which is the same object whenever editing is possible,
 * since conversion is off in edit mode.
 */
const instructionsModel = computed<RecipeStep[]>({
  get: () => displayedRecipe.value.recipeInstructions,
  set: (steps) => {
    if (isConverted.value) {
      // Defensive: a write while a converted view is on screen would persist converted
      // text back into the recipe. Nothing does this today because the editor is only
      // reachable in edit mode, where isConverted is false.
      return;
    }
    recipe.value.recipeInstructions = steps;
  },
});

// expose to template
// (all variables used in template are top-level in <script setup>)
</script>

<style lang="css">
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
