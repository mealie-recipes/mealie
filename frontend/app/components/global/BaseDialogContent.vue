<template>
  <v-card height="100%" :loading="loading">
    <template #loader="{ isActive }">
      <v-progress-linear
        :active="isActive"
        indeterminate
      />
    </template>
    <v-toolbar
      dark
      density="comfortable"
      :color="color"
      class="px-3 position-relative top-0 left-0 w-100"
    >
      <v-icon size="large">
        {{ icon }}
      </v-icon>
      <v-toolbar-title class="headline">
        {{ title }}
      </v-toolbar-title>
    </v-toolbar>

    <div style="flex: 1 1 auto; min-height: 0; overflow: auto">
      <slot />
    </div>

    <v-spacer />
    <v-divider />
    <v-card-actions :class="$vuetify.display.xs ? 'pb-4 grid-small' : undefined">
      <slot name="card-actions">
        <v-btn
          variant="text"
          color="grey"
          @click="emit('cancel')"
        >
          {{ cancelLabel }}
        </v-btn>
        <v-spacer v-if="!$vuetify.display.xs" />
        <slot name="custom-card-action" />
        <BaseButton
          v-if="canDelete"
          delete
          @click="emit('delete')"
        />
        <BaseButton
          v-if="canConfirm"
          :color="color"
          type="submit"
          :disabled="submitDisabled"
          @click="emit('confirm')"
        >
          <template #icon>
            {{ $globals.icons.check }}
          </template>
          {{ $t("general.confirm") }}
        </BaseButton>
        <BaseButton
          v-if="canSubmit"
          type="submit"
          :disabled="submitDisabled || loading"
          @click="emit('submit')"
        >
          {{ submitLabel }}
          <template
            v-if="submitIcon"
            #icon
          >
            {{ submitIcon }}
          </template>
        </BaseButton>
      </slot>
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { useGlobalI18n } from "~/composables/use-global-i18n";

interface DialogProps {
  color?: string;
  title?: string;
  icon?: string | null;
  loading?: boolean;

  // submit
  submitIcon?: string | null;
  submitText?: string;
  submitDisabled?: boolean;

  // cancel
  cancelText?: string;

  // actions
  canDelete?: boolean;
  canConfirm?: boolean;
  canSubmit?: boolean;
}

interface DialogEmits {
  (e: "submit" | "cancel" | "confirm" | "delete"): void;
}

// Using TypeScript interface with withDefaults for props
const props = withDefaults(defineProps<DialogProps>(), {
  color: "primary",
  title: "Modal Title",
  icon: null,
  loading: false,

  // submit
  submitIcon: null,
  submitDisabled: false,

  // actions
  canDelete: false,
  canConfirm: false,
  canSubmit: false,
});
const emit = defineEmits<DialogEmits>();

const i18n = useGlobalI18n();

const submitLabel = computed(() => props.submitText ?? i18n.t("general.create"));
const cancelLabel = computed(() => props.cancelText ?? i18n.t("general.cancel"));
</script>

<style scoped>
/* On extra-small displays the dialog is a bottom sheet or fullscreen, so the
   actions stretch evenly across the full width. Larger displays keep the
   default v-card-actions flex row, where the spacer pushes the actions right. */
.grid-small {
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: minmax(min-content, 1fr);
}
</style>
