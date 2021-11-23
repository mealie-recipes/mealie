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

<script>
export default {
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
  data() {
    return {
      show: false,
    };
  },

  methods: {
    toggleBlur() {
      this.$refs.copyToolTip.deactivate();
    },
    textToClipboard() {
      this.show = true;
      const copyText = this.copyText;
      navigator.clipboard.writeText(copyText).then(
        () => console.log(`Copied\n${copyText}`),
        () => console.log(`Copied Failed\n${copyText}`)
      );
      setTimeout(() => {
        this.toggleBlur();
      }, 500);
    },
  },
};
</script>

<style lang="scss" scoped>
</style>