<template>
  <div>
    <BaseDialog
      v-model="dialog"
      :title="$t('data-pages.foods.manage-substitutions')"
      :icon="$globals.icons.swapHorizontal"
      :submit-icon="$globals.icons.check"
      :submit-text="$t('general.confirm')"
      can-submit
      @submit="saveSubstitutions"
      @cancel="$emit('cancel')"
    >
      <v-card-text>
        <p class="text-body-2 pb-3">
          {{ $t("data-pages.foods.substitution-dialog-text", { food: data.name }) }}
        </p>
        <RecipeIngredientSubstitutionEditor
          :substitutions="substitutions"
          :foods="foodOptions"
          @add="createSubstitution"
          @delete="deleteSubstitution"
          @food-changed="resetReverse"
        >
          <!-- spelled out rather than tooltipped: this has to read on a phone, where nothing hovers -->
          <template #after-row="{ index }">
            <v-checkbox
              v-if="substitutions[index]?.substituteFoodId"
              :model-value="reverseChecked(index)"
              :label="reverseLabel(index)"
              density="compact"
              hide-details
              class="ml-2"
              @update:model-value="setReverse(index, !!$event)"
            />
          </template>
        </RecipeIngredientSubstitutionEditor>
      </v-card-text>
    </BaseDialog>
  </div>
</template>

<script setup lang="ts">
import { whenever } from "@vueuse/core";
import { useI18n } from "vue-i18n";
import RecipeIngredientSubstitutionEditor from "~/components/Domain/Recipe/RecipeIngredientSubstitutionEditor.vue";
import { useFoodStore } from "~/composables/store";
import type { IngredientFood, IngredientFoodSubstitution } from "~/lib/api/types/recipe";

interface SubstitutionRow {
  substituteFoodId: string | null;
  note: string;
  // null means "whatever the other food currently says"; a boolean is an explicit choice
  addReverse: boolean | null;
}

export interface ReverseSubstitutionChanges {
  add: string[];
  remove: string[];
}

interface Props {
  data: IngredientFood;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  // reverse substitutions live on the other food, so the page writes them separately
  submit: [substitutions: IngredientFoodSubstitution[], reverseChanges: ReverseSubstitutionChanges];
  cancel: [];
}>();

// V-Model Support
const dialog = defineModel<boolean>({ default: false });

const i18n = useI18n();
const foodStore = useFoodStore();
// a food cannot substitute for itself, so it is never offered
const foodOptions = computed(() => foodStore.store.value.filter(food => food.id !== props.data.id));

const substitutions = ref<SubstitutionRow[]>([]);

function substituteFood(substituteFoodId: string | null) {
  return substituteFoodId ? foodStore.store.value.find(food => food.id === substituteFoodId) : undefined;
}

// the reverse substitution lives on the other food, so it is read back off that food
function reverseExists(substituteFoodId: string | null) {
  return !!substituteFood(substituteFoodId)?.substitutions?.some(sub => sub.substituteFoodId === props.data.id);
}

// the control is per-row because the dialog mixes saved and unsaved rows; a single checkbox
// at the bottom couldn't say which of them it meant
function reverseChecked(index: number) {
  const substitution = substitutions.value[index];
  return substitution ? (substitution.addReverse ?? reverseExists(substitution.substituteFoodId)) : false;
}

// echoes the "in place of" wording of the intro line, read backwards; the checkbox itself
// carries whether the reverse is already there
function reverseLabel(index: number) {
  const substitute = substituteFood(substitutions.value[index]?.substituteFoodId ?? null)?.name || "";
  return i18n.t("data-pages.foods.reverse-substitution-add", { food: props.data.name, substitute });
}

function setReverse(index: number, addReverse: boolean | null) {
  const substitution = substitutions.value[index];
  if (substitution) {
    substitution.addReverse = addReverse;
  }
}

function createSubstitution() {
  substitutions.value.push({
    substituteFoodId: null,
    note: "",
    addReverse: null,
  });
}

function deleteSubstitution(index: number) {
  substitutions.value.splice(index, 1);
}

// a row pointed at a different food has a different reverse to report on, so the choice made
// about the previous one is dropped rather than carried over
function resetReverse(index: number) {
  setReverse(index, null);
}

function initSubstitutions() {
  substitutions.value = (props.data.substitutions || []).map(substitution => ({
    substituteFoodId: substitution.substituteFoodId || null,
    note: substitution.note || "",
    addReverse: null,
  }));

  if (!substitutions.value.length) {
    createSubstitution();
  }
}

initSubstitutions();
whenever(
  () => dialog.value,
  () => {
    initSubstitutions();
  },
);

function saveSubstitutions() {
  const seenFoodIds: string[] = [];
  const keepRows: SubstitutionRow[] = [];
  const keepSubstitutions: IngredientFoodSubstitution[] = [];
  const reverseChanges: ReverseSubstitutionChanges = { add: [], remove: [] };

  substitutions.value.forEach((substitution) => {
    const substituteFoodId = substitution.substituteFoodId || null;
    const note = (substitution.note || "").trim() || null;

    // an empty row is a UI artifact rather than something to save, matching the alias dialog
    if (!substituteFoodId && !note) {
      return;
    }

    if (substituteFoodId) {
      if (substituteFoodId === props.data.id || seenFoodIds.includes(substituteFoodId)) {
        return;
      }
      seenFoodIds.push(substituteFoodId);

      // only a row whose reverse differs from what the other food already has needs a write
      const exists = reverseExists(substituteFoodId);
      const wanted = substitution.addReverse ?? exists;
      if (wanted !== exists) {
        (wanted ? reverseChanges.add : reverseChanges.remove).push(substituteFoodId);
      }
    }

    keepRows.push({ substituteFoodId, note: note || "", addReverse: substitution.addReverse });
    keepSubstitutions.push({ substituteFoodId, note });
  });

  substitutions.value = keepRows;
  emit("submit", keepSubstitutions, reverseChanges);
}
</script>
