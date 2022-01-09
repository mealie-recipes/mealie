<template>
  <v-tooltip
    ref="copyToolTip"
    v-model="show"
    color="success lighten-1"
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
        @click="
          on.click;
          textToClipboard();
        "
        @blur="on.blur"
      >
        <v-icon>{{ $globals.icons.contentCopy }}</v-icon>
        {{ icon ? "" : "Copy" }}
      </v-btn>
    </template>
    <span>
      <v-icon left dark>
        {{ $globals.icons.clipboardCheck }}
      </v-icon>
      <slot> {{ $t("general.copied") }}! </slot>
    </span>
  </v-tooltip>
</template>

<script lang="ts">
import { defineComponent, ref } from "@nuxtjs/composition-api";
import { VTooltip } from "~/types/vuetify";

export default defineComponent({
  props: {
    copyText: {
      type: String,
      default: "Default Copy Text",
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
    const show = ref(false);
    const copyToolTip = ref<VTooltip | null>(null);

    function toggleBlur() {
      copyToolTip.value?.deactivate();
    }

    function textToClipboard() {
      show.value = true;
      const copyText = props.copyText;
      navigator.clipboard.writeText(copyText).then(
        () => console.log(`Copied\n${copyText}`),
        () => console.log(`Copied Failed\n${copyText}`)
      );
      setTimeout(() => {
        toggleBlur();
      }, 500);
    }

    return {
      show,
      copyToolTip,
      textToClipboard,
    }
  },
});
</script>

<style lang="scss" scoped>
</style>
