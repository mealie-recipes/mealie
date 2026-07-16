<template>
  <div>
    <slot
      name="activator"
      v-bind="{ open }"
    />
    <v-dialog
      v-model="dialog"
      :width="width"
      :max-width="maxWidth ?? undefined"
      :content-class="top ? 'top-dialog' : undefined"
      :fullscreen="$vuetify.display.xs"
      @keydown.enter="submitOnEnter"
      @click:outside="emit('cancel')"
      @keydown.esc="emit('cancel')"
    >
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
          <slot v-bind="{ submitEvent }" />
        </div>

        <v-spacer />
        <v-divider />

        <v-card-actions :class="$vuetify.display.xs ? 'pb-4' : 'undefined'">
          <slot name="card-actions">
            <v-btn
              variant="text"
              color="grey"
              @click="
                dialog = false;
                emit('cancel');
              "
            >
              {{ cancelText }}
            </v-btn>
            <v-spacer />

            <slot name="custom-card-action" />
            <BaseButton
              v-if="canDelete"
              delete
              @click="deleteEvent"
            />
            <BaseButton
              v-if="canConfirm"
              :color="color"
              type="submit"
              :disabled="submitDisabled"
              @click="
                emit('confirm');
                dialog = false;
              "
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
              @click="submitEvent"
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
  logDeprecatedProp("open");
}

/* function close() {
  dialog.value = false;
  logDeprecatedProp("close");
} */

function logDeprecatedProp(val: string) {
  console.warn(
    `[BaseDialog] The method '${val}' is deprecated. Please use v-model="value" to manage state instead.`,
  );
}
</script>

<style>
.top-dialog {
  position: fixed;
  top: 0;
}
</style>
