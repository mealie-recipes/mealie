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
      <slot v-bind="{ submitEvent: () => emit('submit') }" />
    </div>

    <v-spacer />
    <v-divider />
    <v-card-actions :class="$vuetify.display.mdAndUp ? 'grid-large' : 'pb-4 grid-small'">
      <slot name="card-actions">
        <v-btn
          variant="text"
          color="grey"
          class="place-start"
          @click="emit('cancel')"
        >
          {{ cancelText }}
        </v-btn>
        <v-spacer v-if="$vuetify.display.mdAndUp" />
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
          {{ submitText }}
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
import { useNuxtApp } from "#app";

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
withDefaults(defineProps<DialogProps>(), {
  color: "primary",
  title: "Modal Title",
  icon: null,
  loading: false,

  // submit
  submitIcon: null,
  submitText: () => useNuxtApp().$i18n.t("general.create"),
  submitDisabled: false,

  // cancel
  cancelText: () => useNuxtApp().$i18n.t("general.cancel"),

  // actions
  canDelete: false,
  canConfirm: false,
  canSubmit: false,
});
const emit = defineEmits<DialogEmits>();
</script>

<style lang="css">
.grid-small {
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: minmax(min-content, 1fr);
}
.grid-large {
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: min-content 1fr min-content;

  .place-start {
    place-self: start;
  }

  .place-end {
    place-self: end;
  }
}
</style>
