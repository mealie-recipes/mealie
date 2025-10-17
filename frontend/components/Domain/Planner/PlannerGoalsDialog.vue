<template>
  <BaseDialog
    v-model="dialog"
    :icon="$globals.icons.cog"
    :title="$t('planner.goals.title')"
    max-width="600px"
  >
    <template #activator="{ open }">
      <slot
        name="activator"
        :open="open"
      />
    </template>

    <v-card-text>
      <p class="text-subtitle-2 mb-4">
        {{ $t("planner.goals.description") }}
      </p>

      <v-form ref="formRef">
        <v-text-field
          v-model.number="localGoals.calories"
          :label="$t('planner.goals.calories')"
          type="number"
          variant="outlined"
          suffix="kcal"
          :min="0"
          :step="50"
          class="mb-3"
          hide-details
        />

        <v-text-field
          v-model.number="localGoals.protein"
          :label="$t('planner.goals.protein')"
          type="number"
          variant="outlined"
          suffix="g"
          :min="0"
          :step="5"
          class="mb-3"
          hide-details
        />

        <v-text-field
          v-model.number="localGoals.carbohydrate"
          :label="$t('planner.goals.carbohydrate')"
          type="number"
          variant="outlined"
          suffix="g"
          :min="0"
          :step="5"
          class="mb-3"
          hide-details
        />

        <v-text-field
          v-model.number="localGoals.fat"
          :label="$t('planner.goals.fat')"
          type="number"
          variant="outlined"
          suffix="g"
          :min="0"
          :step="5"
          class="mb-3"
          hide-details
        />

        <v-text-field
          v-model.number="localGoals.toleranceKcal"
          :label="$t('planner.goals.tolerance-kcal')"
          type="number"
          variant="outlined"
          suffix="kcal"
          :min="0"
          :step="10"
          :hint="$t('planner.goals.tolerance-hint')"
          persistent-hint
        />
      </v-form>
    </v-card-text>

    <template #card-actions>
      <v-btn
        variant="text"
        color="grey"
        @click="dialog = false"
      >
        {{ $t("general.cancel") }}
      </v-btn>
      <v-btn
        variant="text"
        color="warning"
        @click="handleReset"
      >
        {{ $t("general.reset") }}
      </v-btn>
      <v-spacer />
      <BaseButton
        :color="'primary'"
        @click="handleSave"
      >
        {{ $t("general.save") }}
      </BaseButton>
    </template>
  </BaseDialog>
</template>

<script lang="ts" setup>
import { ref, watch } from "vue";
import { usePlannerGoals, type PlannerGoals } from "~/composables/use-planner-goals";

const props = defineProps<{
  modelValue: boolean;
}>();

const emit = defineEmits<{
  "update:modelValue": [value: boolean];
}>();

const dialog = computed({
  get: () => props.modelValue,
  set: (value: boolean) => emit("update:modelValue", value),
});

const { goals, setGoals, resetGoals } = usePlannerGoals();

// Local copy of goals for editing
const localGoals = ref<PlannerGoals>({ ...goals.value });

// Sync local goals when dialog opens
watch(dialog, (isOpen) => {
  if (isOpen) {
    localGoals.value = { ...goals.value };
  }
});

function handleSave() {
  setGoals(localGoals.value);
  dialog.value = false;
}

function handleReset() {
  resetGoals();
  localGoals.value = { ...goals.value };
}
</script>
