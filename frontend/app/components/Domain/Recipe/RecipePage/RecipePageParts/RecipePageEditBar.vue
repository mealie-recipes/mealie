<template>
  <div class="edit-bar d-print-none">
    <BaseDialog
      v-model="deleteDialog"
      bottom-sheet
      :title="$t('recipe.delete-recipe')"
      color="error"
      :icon="$globals.icons.alertCircle"
      can-confirm
      @confirm="$emit('delete')"
    >
      <v-card-text>
        {{ $t("recipe.delete-confirmation") }}
      </v-card-text>
    </BaseDialog>

    <button type="button" class="mealie-pill mealie-pill--sm" @click="$emit('close')">
      {{ $t("general.cancel") }}
    </button>

    <div class="edit-bar__title">
      <span class="edit-bar__eyebrow">{{ $t("recipe-edit.editing") }}</span>
      <span class="edit-bar__name">{{ recipe.name || $t("recipe.recipe-name") }}</span>
    </div>

    <div class="edit-bar__actions">
      <div class="mealie-segmented" role="group" :aria-label="$t('recipe-edit.editor')">
        <button
          type="button"
          class="mealie-segmented__item mealie-hit-target"
          :class="{ 'mealie-segmented__item--active': !isEditJSON }"
          :aria-pressed="!isEditJSON"
          @click="isEditJSON && toggleEditMode()"
        >
          {{ $t("recipe-edit.form") }}
        </button>
        <button
          type="button"
          class="mealie-segmented__item mealie-hit-target"
          :class="{ 'mealie-segmented__item--active': isEditJSON }"
          :aria-pressed="isEditJSON"
          @click="!isEditJSON && toggleEditMode()"
        >
          {{ $t("general.json") }}
        </button>
      </div>
      <button
        type="button"
        class="mealie-pill mealie-pill--sm mealie-pill--icon edit-bar__delete"
        :aria-label="$t('general.delete')"
        :title="$t('general.delete')"
        @click="deleteDialog = true"
      >
        <v-icon size="16">
          {{ $globals.icons.delete }}
        </v-icon>
      </button>
      <button type="button" class="mealie-pill mealie-pill--sm mealie-pill--primary" @click="$emit('save')">
        {{ $t("general.save") }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { usePageState } from "~/composables/recipe-page/shared-state";
import type { NoUndefinedField } from "~/lib/api/types/non-generated";
import type { Recipe } from "~/lib/api/types/recipe";

const props = defineProps<{ recipe: NoUndefinedField<Recipe> }>();

defineEmits<{
  save: [];
  delete: [];
  close: [];
}>();

const { isEditJSON, toggleEditMode } = usePageState(props.recipe.slug);
const deleteDialog = ref(false);
</script>

<style scoped>
.edit-bar {
  position: sticky;
  top: 0;
  z-index: 5;
  display: flex;
  align-items: center;
  gap: 16px;
  height: 60px;
  padding: 0 32px;
  background: color-mix(in srgb, var(--mealie-canvas) 85%, transparent);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-bottom: 1px solid var(--mealie-hairline);
  white-space: nowrap;
}

.edit-bar__title {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
}

.edit-bar__eyebrow {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--mealie-text-tertiary);
}

.edit-bar__name {
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 15px;
  font-weight: 600;
  color: var(--mealie-ink);
}

.edit-bar__actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.edit-bar__delete {
  color: rgb(var(--v-theme-error));
}

@media (max-width: 1279.98px) {
  /* below the large breakpoint the app bar is back, fixed above the page */
  .edit-bar {
    top: 48px;
    padding: 0 16px;
  }
}

@media (max-width: 600px) {
  .edit-bar__title {
    display: none;
  }

  .edit-bar__actions {
    margin-left: auto;
  }
}
</style>
