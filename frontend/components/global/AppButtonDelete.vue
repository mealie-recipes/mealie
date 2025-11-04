<template>
  <BaseDialog
    v-model="deleteDialog"
    :title="confirmTitleI8n"
    color="error"
    :icon="$globals.icons.alertCircle"
    can-confirm
    @confirm="deleteElem()"
  >
    <v-card-text>
      {{ confirmTextI8n }}
    </v-card-text>
  </BaseDialog>

  <slot v-bind="{ onButtonClick }">
    <v-btn
      :small="small"
      :color="color"
      :variant="textBtn ? 'text' : 'elevated'"
      :disabled="disabled"
      :class="props.class"
      @click="onButtonClick"
    >
      <v-icon start>
        {{ effIcon }}
      </v-icon>
      {{ text ? text : defaultText }}
    </v-btn>
  </slot>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";

const DELETE_EVENT = "delete";

const props = withDefaults(
  defineProps<{
    small?: boolean;
    url?: string;
    text?: string;
    icon?: string | null;
    textBtn?: boolean;
    color?: string;
    disabled?: boolean;
    class?: string;
    confirmType?: string;
    confirmTitle?: string;
    confirmText?: string;
  }>(),
  {
    small: false,
    url: "",
    text: "",
    icon: null,
    textBtn: true,
    color: "error",
    disabled: false,
    class: "mx-1",
  },
);

const emit = defineEmits<{
  (e: typeof DELETE_EVENT): void;
}>();

const deleteDialog = ref(false);
const { $globals } = useNuxtApp();
const i18n = useI18n();

const effIcon = props.icon ?? $globals.icons.delete;
const defaultText = i18n.t("general.delete");
const confirmTextI8n = props.confirmText
  ? props.confirmText
  : i18n.t("general.confirm-delete-generic-with-name", {
      name: props.confirmType ? props.confirmType : "",
    });
const confirmTitleI8n = props.confirmTitle
  ? props.confirmTitle
  : i18n.t("general.delete");

async function deleteElem() {
  try {
    emit(DELETE_EVENT);
  }
  catch (e) {
    console.error(e);
  }
}

function onButtonClick() {
  deleteDialog.value = true;
}
</script>

<style></style>
