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
      ref="deleteRecipieConfirm"
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
      <v-tooltip bottom color="info">
        <template #activator="{ on, attrs }">
          <v-btn
            v-if="loggedIn"
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
      <RecipeContextMenu
        show-print
        :menu-top="false"
        :slug="slug"
        :name="name"
        :menu-icon="$globals.icons.mdiDotsHorizontal"
        fab
        color="info"
        :card-menu="false"
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

<script>
import RecipeContextMenu from "./RecipeContextMenu.vue";
import RecipeFavoriteBadge from "./RecipeFavoriteBadge.vue";

const SAVE_EVENT = "save";
const DELETE_EVENT = "delete";
const CLOSE_EVENT = "close";
const JSON_EVENT = "json";

export default {
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
  },
  data() {
    return {
      edit: false,
    };
  },

  computed: {
    editorButtons() {
      return [
        {
          text: this.$t("general.delete"),
          icon: this.$globals.icons.delete,
          event: DELETE_EVENT,
          color: "error",
        },
        {
          text: this.$t("general.json"),
          icon: this.$globals.icons.codeBraces,
          event: JSON_EVENT,
          color: "accent",
        },
        {
          text: this.$t("general.close"),
          icon: this.$globals.icons.close,
          event: CLOSE_EVENT,
          color: "",
        },
        {
          text: this.$t("general.save"),
          icon: this.$globals.icons.save,
          event: SAVE_EVENT,
          color: "success",
        },
      ];
    },
  },
  methods: {
    emitHandler(event) {
      switch (event) {
        case CLOSE_EVENT:
          this.$emit(CLOSE_EVENT);
          this.$emit("input", false);
          break;
        case SAVE_EVENT:
          this.$emit(SAVE_EVENT);
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
      this.$emit("input", false);
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
