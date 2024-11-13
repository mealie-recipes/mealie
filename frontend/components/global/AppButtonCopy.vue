<template>
  <v-tooltip
    ref="copyToolTip"
    v-model="show"
    :color="copied? 'success lighten-1' : 'red lighten-1'"
    top
    :open-on-hover="false"
    :open-on-click="true"
    close-delay="500"
    transition="slide-y-transition"
  >
    <template #activator="{ on }">
      <v-btn
        :icon="icon"
        :color="color"
        retain-focus-on-click
        :class="btnClass"
        :disabled="copyText !== '' ? false : true"
        @click="
          on.click;
          textToClipboard();
        "
        @blur="on.blur"
      >
        <v-icon>{{ $globals.icons.contentCopy }}</v-icon>
        {{ icon ? "" : $t("general.copy") }}
      </v-btn>
    </template>
    <span>
      <v-icon left dark>
        {{ $globals.icons.clipboardCheck }}
      </v-icon>
      <slot v-if="!isSupported"> {{ $t("general.your-browser-does-not-support-clipboard") }} </slot>
      <slot v-else> {{ copied ? $t("general.copied_message") : $t("general.clipboard-copy-failure") }} </slot>
    </span>
  </v-tooltip>
</template>

<script lang="ts">
import { useClipboard } from "@vueuse/core"
import { defineComponent, ref } from "@nuxtjs/composition-api";
import { VTooltip } from "~/types/vuetify";

export default defineComponent({
  props: {
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
  },
  setup(props) {
    const { copy, copied, isSupported } = useClipboard()
    const show = ref(false);
    const copyToolTip = ref<VTooltip | null>(null);

    function toggleBlur() {
      copyToolTip.value?.deactivate();
    }

    async function textToClipboard() {
      if (isSupported.value) {
        await copy(props.copyText);
        if (copied.value) {
          console.log(`Copied\n${props.copyText}`)
        }
        else {
          console.warn("Copy failed: ", copied.value);
        }
      }
      else {
        console.warn("Clipboard is currently not supported by your browser. Ensure you're on a secure (https) site.");
      }

      show.value = true;
      setTimeout(() => {
        toggleBlur();
      }, 500);
    }

    return {
      show,
      copyToolTip,
      textToClipboard,
      copied,
      isSupported,
    };
  },
});
</script>

<style lang="scss" scoped></style>
