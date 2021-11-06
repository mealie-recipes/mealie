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
    v-bind="$attrs"
    v-on="$listeners"
    @click="download ? downloadFile() : undefined"
  >
    <v-icon v-if="!iconRight" left>
      <slot name="icon">
        {{ btnAttrs.icon }}
      </slot>
    </v-icon>
    <slot name="default">
      {{ btnAttrs.text }}
    </slot>
    <v-icon v-if="iconRight" right>
      <slot name="icon">
        {{ btnAttrs.icon }}
      </slot>
    </v-icon>
  </v-btn>
</template>

<script>
import { useUserApi } from "~/composables/api";
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
    save: {
      type: Boolean,
      default: false,
    },
    delete: {
      type: Boolean,
      default: false,
    },
    // Download
    download: {
      type: Boolean,
      default: false,
    },
    downloadUrl: {
      type: String,
      default: "",
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
    iconRight: {
      type: Boolean,
      default: false,
    },
  },
  setup() {
    const api = useUserApi();

    return { api };
  },
  data() {
    return {
      buttonOptions: {
        create: {
          text: "Create",
          icon: this.$globals.icons.createAlt,
          color: "success",
        },
        update: {
          text: "Update",
          icon: this.$globals.icons.edit,
          color: "success",
        },
        save: {
          text: "Save",
          icon: this.$globals.icons.save,
          color: "success",
        },
        edit: {
          text: "Edit",
          icon: this.$globals.icons.edit,
          color: "info",
        },
        delete: {
          text: "Delete",
          icon: this.$globals.icons.delete,
          color: "error",
        },
        cancel: {
          text: "Cancel",
          icon: this.$globals.icons.close,
          color: "grey",
        },
        download: {
          text: "Download",
          icon: this.$globals.icons.download,
          color: "info",
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
      } else if (this.download) {
        return this.buttonOptions.download;
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
    downloadFile() {
      this.api.utils.download(this.downloadUrl);
    },
  },
};
</script>
