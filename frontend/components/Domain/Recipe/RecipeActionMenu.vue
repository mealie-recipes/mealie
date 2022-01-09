<template>
  <v-toolbar
    rounded
    height="0"
    class="fixed-bar mt-0"
    color="rgb(255, 0, 0, 0.0)"
    flat
    style="z-index: 2; position: sticky"
  >
    <BaseDialog
      v-model="deleteDialog"
      :title="$t('recipe.delete-recipe')"
      color="error"
      :icon="$globals.icons.alertCircle"
      @confirm="emitDelete()"
    >
      <v-card-text>
        {{ $t("recipe.delete-confirmation") }}
      </v-card-text>
    </BaseDialog>

    <v-spacer></v-spacer>
    <div v-if="!value" class="custom-btn-group ma-1">
      <RecipeFavoriteBadge v-if="loggedIn" class="mx-1" color="info" button-style :slug="slug" show-always />
      <v-tooltip v-if="!locked" bottom color="info">
        <template #activator="{ on, attrs }">
          <v-btn
            fab
            small
            class="mx-1"
            color="info"
            v-bind="attrs"
            v-on="on"
            @click="$emit('input', true)"
          >
            <v-icon> {{ $globals.icons.edit }} </v-icon>
          </v-btn>
        </template>
        <span>{{ $t("general.edit") }}</span>
      </v-tooltip>
      <v-tooltip v-else bottom color="info">
        <template #activator="{ on, attrs }">
          <v-btn
            fab
            small
            class="mx-1"
            color="info"
            v-bind="attrs"
            v-on="on"
          >
            <v-icon> {{ $globals.icons.lock }} </v-icon>
          </v-btn>
        </template>
        <span> Locked by Owner </span>
      </v-tooltip>

      <RecipeContextMenu
        show-print
        :menu-top="false"
        :slug="slug"
        :name="name"
        :menu-icon="$globals.icons.mdiDotsHorizontal"
        fab
        color="info"
        :card-menu="false"
        :recipe-id="recipeId"
        :use-items="{
          delete: false,
          edit: false,
          download: true,
          mealplanner: true,
          print: true,
          share: true,
        }"
        @print="$emit('print')"
      />
    </div>
    <div v-if="value" class="custom-btn-group mb-">
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

<script lang="ts">
import {defineComponent, ref, useContext} from "@nuxtjs/composition-api";
import RecipeContextMenu from "./RecipeContextMenu.vue";
import RecipeFavoriteBadge from "./RecipeFavoriteBadge.vue";

const SAVE_EVENT = "save";
const DELETE_EVENT = "delete";
const CLOSE_EVENT = "close";
const JSON_EVENT = "json";

export default defineComponent({
  components: { RecipeContextMenu, RecipeFavoriteBadge },
  props: {
    slug: {
      required: true,
      type: String,
    },
    name: {
      required: true,
      type: String,
    },
    value: {
      type: Boolean,
      default: false,
    },
    loggedIn: {
      type: Boolean,
      default: false,
    },
    recipeId: {
      required: true,
      type: Number,
    },
    locked: {
      type: Boolean,
      default: false,
    },
  },
  setup(_, context) {
    const deleteDialog = ref(false);

    const { i18n, $globals } = useContext();
    const editorButtons = [
      {
        text: i18n.t("general.delete"),
        icon: $globals.icons.delete,
        event: DELETE_EVENT,
        color: "error",
      },
      {
        text: i18n.t("general.json"),
        icon: $globals.icons.codeBraces,
        event: JSON_EVENT,
        color: "accent",
      },
      {
        text: i18n.t("general.close"),
        icon: $globals.icons.close,
        event: CLOSE_EVENT,
        color: "",
      },
      {
        text: i18n.t("general.save"),
        icon: $globals.icons.save,
        event: SAVE_EVENT,
        color: "success",
      },
    ];

    function emitHandler(event: string) {
      switch (event) {
        case CLOSE_EVENT:
          context.emit(CLOSE_EVENT);
          context.emit("input", false);
          break;
        case SAVE_EVENT:
          context.emit(SAVE_EVENT);
          break;
        case JSON_EVENT:
          context.emit(JSON_EVENT);
          break;
        case DELETE_EVENT:
          deleteDialog.value = true;
          break;
        default:
          break;
      }
    }

    function emitDelete() {
      context.emit(DELETE_EVENT);
      context.emit("input", false);
    }

    return {
      deleteDialog,
      editorButtons,
      emitHandler,
      emitDelete,
    }
  },
});
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
