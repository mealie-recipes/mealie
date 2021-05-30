<template>
  <v-btn
    :color="btnAttrs.color"
    :small="small"
    :x-small="xSmall"
    :loading="loading"
    :disabled="disabled"
    @click="$emit('click')"
    :outlined="btnStyle.outlined"
    :text="btnStyle.text"
  >
    <v-icon left>
      <slot name="icon">
        {{ btnAttrs.icon }}
      </slot>
    </v-icon>
    <slot>
      {{ btnAttrs.text }}
    </slot>
  </v-btn>
</template>

<script>
export default {
  name: "theButton",
  props: {
    // Types
    cancel: {
      type: Boolean,
      default: false,
    },
    create: {
      type: Boolean,
      default: false,
    },
    update: {
      type: Boolean,
      default: false,
    },
    edit: {
      type: Boolean,
      default: false,
    },
    delete: {
      type: Boolean,
      default: false,
    },
    // Property
    loading: {
      type: Boolean,
      default: false,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    // Styles
    small: {
      type: Boolean,
      default: false,
    },
    xSmall: {
      type: Boolean,
      default: false,
    },
    secondary: {
      type: Boolean,
      default: false,
    },
    minor: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      buttonOptions: {
        create: {
          text: this.$t("general.create"),
          icon: this.$globals.icons.create,
          color: "success",
        },
        update: {
          text: this.$t("general.update"),
          icon: this.$globals.icons.update,
          color: "success",
        },
        save: {
          text: this.$t("general.save"),
          icon: this.$globals.icons.save,
          color: "success",
        },
        edit: {
          text: this.$t("general.edit"),
          icon: this.$globals.icons.edit,
          color: "info",
        },
        delete: {
          text: this.$t("general.delete"),
          icon: this.$globals.icons.delete,
          color: "error",
        },
        cancel: {
          text: this.$t("general.cancel"),
          icon: this.$globals.icons.close,
          color: "grey",
        },
      },
      buttonStyles: {
        defaults: {
          text: false,
          outlined: false,
        },
        secondary: {
          text: false,
          outlined: true,
        },
        minor: {
          outlined: false,
          text: true,
        },
      },
    };
  },
  computed: {
    btnAttrs() {
      if (this.delete) {
        return this.buttonOptions.delete;
      } else if (this.update) {
        return this.buttonOptions.update;
      } else if (this.edit) {
        return this.buttonOptions.edit;
      } else if (this.cancel) {
        this.setMinor();
        return this.buttonOptions.cancel;
      } else if (this.save) {
        return this.buttonOptions.save;
      }

      return this.buttonOptions.create;
    },
    btnStyle() {
      if (this.secondary) {
        return this.buttonStyles.secondary;
      } else if (this.minor) {
        return this.buttonStyles.minor;
      }
      return this.buttonStyles.defaults;
    },
  },
  methods: {
    setMinor() {
      this.buttonStyles.defaults = this.buttonStyles.minor;
    },
    setSecondary() {
      this.buttonStyles.defaults = this.buttonStyles.secondary;
    },
  },
};
</script>

<style lang="scss" scoped>
</style>