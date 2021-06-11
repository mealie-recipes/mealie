<template>
  <v-toolbar
    rounded
    height="0"
    class="fixed-bar mt-0"
    color="rgb(255, 0, 0, 0.0)"
    flat
    style="z-index: 2; position: sticky"
    :class="{ 'fixed-bar-mobile': $vuetify.breakpoint.xs }"
  >
    <ConfirmationDialog
      :title="$t('recipe.delete-recipe')"
      :message="$t('recipe.delete-confirmation')"
      color="error"
      icon="mdi-alert-circle"
      ref="deleteRecipieConfirm"
      v-on:confirm="emitDelete()"
    />
    <v-spacer></v-spacer>
    <div v-if="!edit" class="custom-btn-group ma-1">
      <v-btn
        fab
        small
        class="mx-1"
        color="info"
        @click="
          edit = true;
          $emit('edit');
        "
      >
        <v-icon> {{ $globals.icons.edit }} </v-icon>
      </v-btn>
      <ContextMenu
        :menu-top="false"
        :slug="slug"
        :name="name"
        menu-icon="mdi-dots-horizontal"
        fab
        color="info"
        :card-menu="false"
      />
    </div>
    <div v-if="edit" class="custom-btn-group mb-">
      <v-btn
        v-for="(btn, index) in editorButtons"
        :key="index"
        :fab="$vuetify.breakpoint.xs"
        :small="$vuetify.breakpoint.xs"
        class="mx-1"
        :color="btn.color"
        @click="emitHandler(btn.event)"
      >
        <v-icon :left="!$vuetify.breakpoint.xs">{{ btn.icon }}</v-icon>
        {{ $vuetify.breakpoint.xs ? "" : btn.text }}
      </v-btn>
    </div>
  </v-toolbar>
</template>

<script>
import ConfirmationDialog from "@/components/UI/Dialogs/ConfirmationDialog.vue";
import ContextMenu from "@/components/Recipe/ContextMenu.vue";
const SAVE_EVENT = "save";
const DELETE_EVENT = "delete";
const CLOSE_EVENT = "close";
const JSON_EVENT = "json";

export default {
  components: { ConfirmationDialog, ContextMenu },
  props: {
    slug: {
      type: String,
    },
    name: {
      type: String,
    },
  },
  data() {
    return {
      edit: false,
      editorButtons: [
        {
          text: "Delete",
          icon: this.$globals.icons.delete,
          event: DELETE_EVENT,
          color: "error",
        },
        {
          text: "JSON",
          icon: "mdi-code-braces",
          event: JSON_EVENT,
          color: "accent",
        },
        {
          text: "Close",
          icon: "mdi-close",
          event: CLOSE_EVENT,
          color: undefined,
        },
        {
          text: "Save",
          icon: this.$globals.icons.save,
          event: SAVE_EVENT,
          color: "success",
        },
      ],
    };
  },
  methods: {
    emitHandler(event) {
      switch (event) {
        case CLOSE_EVENT:
          this.$emit(CLOSE_EVENT);
          this.edit = false;
          break;
        case SAVE_EVENT:
          this.$emit(SAVE_EVENT);
          this.edit = false;
          break;
        case JSON_EVENT:
          this.$emit(JSON_EVENT);
          break;
        case DELETE_EVENT:
          this.$refs.deleteRecipieConfirm.open();
          break;
        default:
          break;
      }
    },
    emitDelete() {
      this.$emit(DELETE_EVENT);
      this.edit = false;
    },
  },
};
</script>

<style scoped>
.custom-btn-group {
  flex: 0, 1, auto;
  display: inline-flex;
}

.vertical {
  flex-direction: column !important;
}

.sticky {
  margin-left: auto;
  position: fixed !important;
  margin-top: 4.25rem;
}

.fixed-bar {
  position: sticky;
  position: -webkit-sticky; /* for Safari */
  top: 4.5em;
  z-index: 2;
}

.fixed-bar-mobile {
  top: 1.5em !important;
}
</style>