<template>
  <v-btn
    :color="color || btnAttrs.color"
    :small="small"
    :x-small="xSmall"
    :loading="loading"
    :disabled="disabled"
    :outlined="btnStyle.outlined"
    :text="btnStyle.text"
    :to="to"
    @click="$emit('click')"
  >
    <v-icon left>
      <slot name="icon">
        {{ btnAttrs.icon }}
      </slot>
    </v-icon>
    <slot name="default">
      {{ btnAttrs.text }}
    </slot>
  </v-btn>
</template>

<script>
export default {
  name: "BaseButton",
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
    to: {
      type: String,
      default: null,
    },
    color: {
      type: String,
      default: null,
    },
  },
  data() {
    return {
      buttonOptions: {
        create: {
          text: "Create",
          icon: "mdi-plus",
          color: "success",
        },
        update: {
          text: "Update",
          icon: "mdi-edit",
          color: "success",
        },
        save: {
          text: "Save",
          icon: "mdi-save",
          color: "success",
        },
        edit: {
          text: "Edit",
          icon: "mdi-square-edit-outline",
          color: "info",
        },
        delete: {
          text: "Delete",
          icon: "mdi-delete",
          color: "error",
        },
        cancel: {
          text: "Cancel",
          icon: "mdi-close",
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
