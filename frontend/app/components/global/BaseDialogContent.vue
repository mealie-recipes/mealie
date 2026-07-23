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

    <v-card-actions class="pb-4">
      <slot name="card-actions">
        <v-btn
          class="flex-1-1-0"
          variant="text"
          color="grey"
          @click="emit('cancel')"
        >
          {{ cancelText }}
        </v-btn>

        <slot name="custom-card-action" />
        <BaseButton
          v-if="canDelete"
          class="flex-1-1-0"
          delete
          @click="emit('delete')"
        />
        <BaseButton
          v-if="canConfirm"
          :color="color"
          class="flex-1-1-0"
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
          class="flex-1-1-0"
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
  width?: number | string;
  maxWidth?: number | string | null;
  loading?: boolean;
  top?: boolean | null;
  keepOpen?: boolean;

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
  disableSubmitOnEnter?: boolean;
}

interface DialogEmits {
  (e: "update:modelValue", value: boolean): void;
  (e: "submit" | "cancel" | "confirm" | "delete" | "close"): void;
}

// Using TypeScript interface with withDefaults for props
withDefaults(defineProps<DialogProps>(), {
  color: "primary",
  title: "Modal Title",
  icon: null,
  width: "500",
  maxWidth: null,
  loading: false,
  top: null,
  keepOpen: false,

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
  disableSubmitOnEnter: false,
});
const emit = defineEmits<DialogEmits>();
</script>
