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

<script lang="ts">
import { computed, defineComponent, useContext } from "@nuxtjs/composition-api";
import { useUserApi } from "~/composables/api";

export default defineComponent({
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
  setup(props) {
    const { $globals } = useContext();
    const buttonOptions = {
      create: {
        text: "Create",
        icon: $globals.icons.createAlt,
        color: "success",
      },
      update: {
        text: "Update",
        icon: $globals.icons.edit,
        color: "success",
      },
      save: {
        text: "Save",
        icon: $globals.icons.save,
        color: "success",
      },
      edit: {
        text: "Edit",
        icon: $globals.icons.edit,
        color: "info",
      },
      delete: {
        text: "Delete",
        icon: $globals.icons.delete,
        color: "error",
      },
      cancel: {
        text: "Cancel",
        icon: $globals.icons.close,
        color: "grey",
      },
      download: {
        text: "Download",
        icon: $globals.icons.download,
        color: "info",
      },
    };

    const btnAttrs = computed(() => {
      if (props.delete) {
        return buttonOptions.delete;
      } else if (props.update) {
        return buttonOptions.update;
      } else if (props.edit) {
        return buttonOptions.edit;
      } else if (props.cancel) {
        return buttonOptions.cancel;
      } else if (props.save) {
        return buttonOptions.save;
      } else if (props.download) {
        return buttonOptions.download;
      }
      return buttonOptions.create;
    });

    const buttonStyles = {
      defaults: {
        text: false,
        outlined: false,
      },
      secondary: {
        text: false,
        outlined: true,
      },
      minor: {
        text: true,
        outlined: false,
      },
    };

    const btnStyle = computed(() => {
      if (props.secondary) {
        return buttonStyles.secondary;
      } else if (props.minor || props.cancel) {
        return buttonStyles.minor;
      }
      return buttonStyles.defaults;
    });


    const api = useUserApi();
    function downloadFile() {
      api.utils.download(props.downloadUrl);
    }


    return {
      btnAttrs,
      btnStyle,
      downloadFile,
    };
  },
});
</script>
