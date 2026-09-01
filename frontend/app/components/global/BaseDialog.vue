<template>
  <div>
    <slot
      name="activator"
      v-bind="{ open }"
    />
    <v-bottom-sheet
      v-if="bottomSheet && $vuetify.display.xs"
      v-model="dialog"
      content-class="rounded-t-xl"
      :content-props="{
        style: 'overflow: hidden',
      }"
      :max-width="maxWidth ?? undefined"
      @keydown.enter="submitOnEnter"
      @click:outside="emit('cancel')"
      @keydown.esc="emit('cancel')"
    >
      <BaseDialogContent v-bind="bindings">
        <template #default>
          <slot />
        </template>
        <template #card-actions>
          <slot name="card-actions" />
        </template>
        <template #custom-card-action>
          <slot name="custom-card-action" />
        </template>
      </BaseDialogContent>
    </v-bottom-sheet>
    <v-dialog
      v-else
      v-model="dialog"
      :width="width"
      :max-width="maxWidth ?? undefined"
      :content-class="top ? 'top-dialog' : undefined"
      :fullscreen="$vuetify.display.xs"
      @keydown.enter="submitOnEnter"
      @click:outside="emit('cancel')"
      @keydown.esc="emit('cancel')"
    >
      <BaseDialogContent v-bind="bindings">
        <template #default>
          <slot />
        </template>
        <template #card-actions>
          <slot name="card-actions" />
        </template>
        <template #custom-card-action>
          <slot name="custom-card-action" />
        </template>
      </BaseDialogContent>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { useNuxtApp } from "#app";

interface DialogProps {
  modelValue: boolean;
  color?: string;
  title?: string;
  icon?: string | null;
  width?: number | string;
  maxWidth?: number | string | null;
  loading?: boolean;
  top?: boolean | null;
  keepOpen?: boolean;
  bottomSheet?: boolean;

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
const props = withDefaults(defineProps<DialogProps>(), {
  color: "primary",
  title: "Modal Title",
  icon: null,
  width: "500",
  maxWidth: null,
  loading: false,
  top: null,
  keepOpen: false,
  bottomSheet: false,

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

const dialog = computed({
  get: () => props.modelValue,
  set: val => emit("update:modelValue", val),
});

const submitted = ref(false);

const determineClose = computed(() => {
  return submitted.value && !props.loading && !props.keepOpen;
});

watch(determineClose, (shouldClose) => {
  if (shouldClose) {
    submitted.value = false;
    dialog.value = false;
  }
});

watch(dialog, (val) => {
  if (val) submitted.value = false;
  if (!val) emit("close");
});

function submitEvent() {
  emit("submit");
  submitted.value = true;
}

function submitOnEnter() {
  if (props.disableSubmitOnEnter) {
    return;
  }

  if (props.canConfirm) {
    if (!props.submitDisabled) {
      emit("confirm");
      dialog.value = false;
    }
    return;
  }

  submitEvent();
}

function deleteEvent() {
  emit("delete");
  submitted.value = true;
}

function open() {
  dialog.value = true;
}

const bindings = computed(() => ({
  color: props.color,
  title: props.title,
  icon: props.icon,
  loading: props.loading,
  submitIcon: props.submitIcon,
  submitText: props.submitText,
  submitDisabled: props.submitDisabled,
  cancelText: props.cancelText,
  canDelete: props.canDelete,
  canConfirm: props.canConfirm,
  canSubmit: props.canSubmit,
  onCancel: () => {
    emit("cancel");
    dialog.value = false;
  },
  onConfirm: () => {
    emit("confirm");
    dialog.value = false;
  },
  onSubmit: submitEvent,
  onDelete: deleteEvent,
}));
</script>

<style>
.top-dialog {
  position: fixed;
  top: 0;
}
</style>
