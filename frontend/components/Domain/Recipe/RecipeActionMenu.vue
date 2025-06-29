<template>
  <v-toolbar
    class="fixed-bar mt-0"
    style="z-index: 2; position: sticky; background: transparent; box-shadow: none;"
    density="compact"
    elevation="0"
  >
    <BaseDialog v-model="deleteDialog" :title="$t('recipe.delete-recipe')" color="error"
      :icon="$globals.icons.alertCircle" can-confirm @confirm="emitDelete()">
      <v-card-text>
        {{ $t("recipe.delete-confirmation") }}
      </v-card-text>
    </BaseDialog>

    <v-spacer />
    <div v-if="!open" class="custom-btn-group ma-1">
      <RecipeFavoriteBadge v-if="loggedIn" color="info" button-style :recipe-id="recipe.id!" show-always />
      <RecipeTimelineBadge v-if="loggedIn" class="ml-1" color="info" button-style :slug="recipe.slug" :recipe-name="recipe.name!" />
      <div v-if="loggedIn">
        <v-tooltip v-if="canEdit" bottom color="info">
          <template #activator="{ props }">
            <v-btn
              icon
              variant="flat"
              rounded="circle"
              size="small"
              color="info"
              class="ml-1"
              v-bind="props"
              @click="$emit('edit', true)"
            >
              <v-icon size="x-large">
                {{ $globals.icons.edit }}
              </v-icon>
            </v-btn>
          </template>
          <span>{{ $t("general.edit") }}</span>
        </v-tooltip>
      </div>

      <RecipeContextMenu
        show-print
        :menu-top="false"
        :name="recipe.name!"
        :slug="recipe.slug!"
        :menu-icon="$globals.icons.dotsVertical"
        fab
        color="info"
        :card-menu="false"
        :recipe="recipe"
        :recipe-id="recipe.id!"
        :recipe-scale="recipeScale"
        :use-items="{
          edit: false,
          download: loggedIn,
          duplicate: loggedIn,
          mealplanner: loggedIn,
          shoppingList: loggedIn,
          print: true,
          printPreferences: true,
          share: loggedIn,
          recipeActions: true,
          delete: loggedIn,
        }"
        class="ml-1"
        @print="$emit('print')"
      />
    </div>
    <div v-if="open" class="custom-btn-group gapped">
      <v-btn
        v-for="(btn, index) in editorButtons"
        :key="index"
        :class="{ 'rounded-circle': $vuetify.display.xs }"
        :size="$vuetify.display.xs ? 'small' : undefined"
        :color="btn.color"
        variant="elevated"
        :icon="$vuetify.display.xs"
        @click="emitHandler(btn.event)"
      >
        <v-icon :left="!$vuetify.display.xs">
          {{ btn.icon }}
        </v-icon>
        {{ $vuetify.display.xs ? "" : btn.text }}
      </v-btn>
    </div>
  </v-toolbar>
</template>

<script lang="ts">
import RecipeContextMenu from "./RecipeContextMenu.vue";
import RecipeFavoriteBadge from "./RecipeFavoriteBadge.vue";
import RecipeTimelineBadge from "./RecipeTimelineBadge.vue";
import type { Recipe } from "~/lib/api/types/recipe";

const SAVE_EVENT = "save";
const DELETE_EVENT = "delete";
const CLOSE_EVENT = "close";
const JSON_EVENT = "json";

export default defineNuxtComponent({
  components: { RecipeContextMenu, RecipeFavoriteBadge, RecipeTimelineBadge },
  props: {
    recipe: {
      required: true,
      type: Object as () => Recipe,
    },
    slug: {
      required: true,
      type: String,
    },
    recipeScale: {
      type: Number,
      default: 1,
    },
    open: {
      required: true,
      type: Boolean,
    },
    name: {
      required: true,
      type: String,
    },
    loggedIn: {
      type: Boolean,
      default: false,
    },
    recipeId: {
      required: true,
      type: String,
    },
    canEdit: {
      type: Boolean,
      default: false,
    },
  },
  emits: ["print", "input", "delete", "close", "edit"],
  setup(_, context) {
    const deleteDialog = ref(false);

    const i18n = useI18n();
    const { $globals } = useNuxtApp();
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
        case DELETE_EVENT:
          deleteDialog.value = true;
          break;
        default:
          context.emit(event);
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
    };
  },
});
</script>

<style scoped>
.custom-btn-group {
  flex: 0, 1, auto;
  display: inline-flex;
}

.gapped {
  gap: 0.25rem;
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
  top: 4.5em;
  z-index: 2;
  background: transparent !important;
  box-shadow: none !important;
  min-height: 0 !important;
  height: 48px;
  padding: 0 8px;
}

.fixed-bar-mobile {
  top: 1.5em !important;
}
</style>
