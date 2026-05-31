<template>
  <v-tooltip
    ref="copyToolTip"
    v-model="show"
    location="top"
    :open-on-hover="false"
    :open-on-click="true"
    close-delay="500"
    transition="slide-y-transition"
  >
    <template #activator="{ props: hoverProps }">
      <v-btn
        variant="flat"
        :icon="icon"
        :color="color"
        retain-focus-on-click
        :class="btnClass"
        :disabled="copyText !== '' ? false : true"
        v-bind="hoverProps"
        @click="textToClipboard()"
      >
        <v-icon>{{ $globals.icons.contentCopy }}</v-icon>
        {{ icon ? "" : $t("general.copy") }}
      </v-btn>
    </template>
    <span v-if="!isSupported || copiedSuccess !== null">
      <v-icon start>
        {{ $globals.icons.clipboardCheck }}
      </v-icon>
      <slot v-if="!isSupported"> {{ $t("general.your-browser-does-not-support-clipboard") }} </slot>
      <slot v-else> {{ copiedSuccess ? $t("general.copied_message") : $t("general.clipboard-copy-failure") }} </slot>
    </span>
  </v-tooltip>
</template>

<script setup lang="ts">
import { useClipboard } from "@vueuse/core";

const props = defineProps({
  copyText: {
    type: String,
    required: true,
  },
  color: {
    type: String,
    default: "",
  },
  icon: {
    type: Boolean,
    default: true,
  },
  btnClass: {
    type: String,
    default: "",
  },
});

const { copy, copied, isSupported } = useClipboard();
const show = ref(false);
const copiedSuccess = ref<boolean | null>(null);

async function textToClipboard() {
  if (isSupported.value) {
    await copy(props.copyText);
    if (copied.value) {
      copiedSuccess.value = true;
      console.info(`Copied\n${props.copyText}`);
    }
    else {
      copiedSuccess.value = false;
      console.error("Copy failed: ", copied.value);
    }
  }
  else {
    console.warn("Clipboard is currently not supported by your browser. Ensure you're on a secure (https) site.");
  }

  show.value = true;
  setTimeout(() => {
    show.value = false;
  }, 3000);
}
</script>

<style lang="scss" scoped></style>
