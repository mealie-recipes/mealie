<template>
  <div>
    <div v-for="substitution, i in substitutions" :key="i" class="mb-2">
      <!-- wraps rather than stacking: on a narrow screen the food takes its own line and the
           note keeps the delete button company, instead of stranding it on a line of its own -->
      <div class="d-flex ga-2 align-center flex-wrap">
        <v-autocomplete
          v-model="substitution.substituteFoodId"
          :items="foods"
          :custom-filter="normalizeFilter"
          item-value="id"
          item-title="name"
          :placeholder="$t('recipe.choose-substitute-food')"
          :style="$vuetify.display.mdAndDown ? 'flex: 1 1 100%;' : 'flex: 6 0 50px;'"
          :menu-props="{ attach: menuAttachTarget, maxHeight: '250px' }"
          density="compact"
          variant="filled"
          clearable
          hide-details
          @update:model-value="emit('food-changed', i)"
        />
        <v-text-field
          v-model="substitution.note"
          :placeholder="$t('recipe.note')"
          :style="$vuetify.display.mdAndDown ? 'flex: 1 1 0;' : 'flex: 4 0 50px;'"
          density="compact"
          variant="filled"
          hide-details
        />
        <!-- left at the default size: an icon button is a 36px touch target everywhere else in
             the app, and the smaller sizes fall under the 24px accessible minimum -->
        <v-btn
          icon
          variant="plain"
          :title="$t('general.delete')"
          @click="emit('delete', i)"
        >
          <v-icon>{{ $globals.icons.delete }}</v-icon>
        </v-btn>
      </div>
      <slot name="after-row" :substitution="substitution" :index="i" />
    </div>
    <v-btn
      variant="text"
      color="primary"
      @click="emit('add')"
    >
      <v-icon start>
        {{ $globals.icons.create }}
      </v-icon>
      {{ $t("general.add") }}
    </v-btn>
  </div>
</template>

<script setup lang="ts">
import { normalizeFilter } from "~/composables/use-utils";
import type { IngredientFood } from "~/lib/api/types/recipe";

/**
 * The shape both tiers share. Callers hold richer rows of their own -- the food dialog tracks a
 * reverse-substitution choice alongside each one -- so rows are mutated in place here and added
 * or removed by the caller, which is the only side that knows what a new row should contain.
 */
export interface EditableSubstitution {
  substituteFoodId?: string | null;
  note?: string | null;
}

interface Props {
  substitutions: EditableSubstitution[];
  foods: IngredientFood[];
  // left unset inside a dialog, so the menu stays in Vuetify's overlay stack rather than being
  // teleported to the body and risking a render behind the dialog
  menuAttachTarget?: string;
}

defineProps<Props>();

const emit = defineEmits<{
  "add": [];
  "delete": [index: number];
  "food-changed": [index: number];
}>();
</script>
