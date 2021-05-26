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
    <template v-slot:activator="{ on }">
      <v-btn
        icon
        :color="color"
        @click="
          on.click;
          textToClipboard();
        "
        @blur="on.blur"
        retain-focus-on-click
      >
        <v-icon>mdi-content-copy</v-icon>
      </v-btn>
    </template>
    <span>
      <v-icon left dark>
        mdi-clipboard-check
      </v-icon>
      <slot> {{ $t("general.coppied") }}! </slot>
    </span>
  </v-tooltip>
</template>

<script>
export default {
  props: {
    copyText: {
      default: "Default Copy Text",
    },
    color: {
      default: "primary",
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
        () => console.log("Copied", copyText),
        () => console.log("Copied Failed", copyText)
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