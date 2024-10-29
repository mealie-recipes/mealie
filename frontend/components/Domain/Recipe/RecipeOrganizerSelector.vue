<template>
  <v-autocomplete
    v-model="selected"
    :items="storeItem"
    :value="value"
    :label="label"
    chips
    deletable-chips
    item-text="name"
    multiple
    :prepend-inner-icon="icon"
    return-object
    v-bind="inputAttrs"
    auto-select-first
    :search-input.sync="searchInput"
    class="pa-0"
    @change="resetSearchInput"
  >
    <template #selection="data">
      <v-chip
        :key="data.index"
        class="ma-1"
        :input-value="data.selected"
        small
        close
        label
        color="accent"
        dark
        @click:close="removeByIndex(data.index)"
      >
        {{ data.item.name || data.item }}
      </v-chip>
    </template>
    <template v-if="showAdd" #append-outer>
      <v-btn icon @click="dialog = true">
        <v-icon>
          {{ $globals.icons.create }}
        </v-icon>
      </v-btn>
      <RecipeOrganizerDialog v-model="dialog" :item-type="selectorType" @created-item="appendCreated" />
    </template>
  </v-autocomplete>
</template>

<script lang="ts">
import { defineComponent, ref, useContext, computed, onMounted } from "@nuxtjs/composition-api";
import RecipeOrganizerDialog from "./RecipeOrganizerDialog.vue";
import { IngredientFood, RecipeCategory, RecipeTag } from "~/lib/api/types/recipe";
import { RecipeTool } from "~/lib/api/types/admin";
import { useCategoryStore, useFoodStore, useHouseholdStore, useTagStore, useToolStore } from "~/composables/store";
import { Organizer, RecipeOrganizer } from "~/lib/api/types/non-generated";
import { HouseholdSummary } from "~/lib/api/types/household";

export default defineComponent({
  components: {
    RecipeOrganizerDialog,
  },
  props: {
    value: {
      type: Array as () => (
        | HouseholdSummary
        | RecipeTag
        | RecipeCategory
        | RecipeTool
        | IngredientFood
        | string
      )[] | undefined,
      required: true,
    },
    /**
     * The type of organizer to use.
     */
    selectorType: {
      type: String as () => RecipeOrganizer,
      required: true,
    },
    inputAttrs: {
      type: Object as () => Record<string, any>,
      default: () => ({}),
    },
    returnObject: {
      type: Boolean,
      default: true,
    },
    showAdd: {
      type: Boolean,
      default: true,
    },
    showLabel: {
      type: Boolean,
      default: true,
    },
    showIcon: {
      type: Boolean,
      default: true,
    },
  },

  setup(props, context) {
    const selected = computed({
      get: () => props.value,
      set: (val) => {
        context.emit("input", val);
      },
    });

    onMounted(() => {
      if (selected.value === undefined) {
        selected.value = [];
      }
    });

    const { $globals, i18n } = useContext();

    const label = computed(() => {
      if (!props.showLabel) {
        return "";
      }

      switch (props.selectorType) {
        case Organizer.Tag:
          return i18n.t("tag.tags");
        case Organizer.Category:
          return i18n.t("category.categories");
        case Organizer.Tool:
          return i18n.t("tool.tools");
        case Organizer.Food:
          return i18n.t("general.foods");
        case Organizer.Household:
          return i18n.t("household.households");
        default:
          return i18n.t("general.organizer");
      }
    });

    const icon = computed(() => {
      if (!props.showIcon) {
        return "";
      }

      switch (props.selectorType) {
        case Organizer.Tag:
          return $globals.icons.tags;
        case Organizer.Category:
          return $globals.icons.categories;
        case Organizer.Tool:
          return $globals.icons.tools;
        case Organizer.Food:
          return $globals.icons.foods;
        case Organizer.Household:
          return $globals.icons.household;
        default:
          return $globals.icons.tags;
      }
    });

    // ===========================================================================
    // Store & Items Setup

    const storeMap = {
      [Organizer.Category]: useCategoryStore(),
      [Organizer.Tag]: useTagStore(),
      [Organizer.Tool]: useToolStore(),
      [Organizer.Food]: useFoodStore(),
      [Organizer.Household]: useHouseholdStore(),
    };

    const store = computed(() => {
      const { store } = storeMap[props.selectorType];
      return store.value;
    })

    const items = computed(() => {
      if (!props.returnObject) {
        return store.value.map((item) => item.name);
      }
      return store.value;
    });

    function removeByIndex(index: number) {
      if (selected.value === undefined) {
        return;
      }
      const newSelected = selected.value.filter((_, i) => i !== index);
      selected.value = [...newSelected];
    }

    function appendCreated(item: any) {
      if (selected.value === undefined) {
        return;
      }

      selected.value = [...selected.value, item];
    }

    const dialog = ref(false);

    const searchInput = ref("");

    function resetSearchInput() {
      searchInput.value = "";
    }

    return {
      Organizer,
      appendCreated,
      dialog,
      storeItem: items,
      label,
      icon,
      selected,
      removeByIndex,
      searchInput,
      resetSearchInput,
    };
  },
});
</script>

<style scoped>
.v-autocomplete {
  /* This aligns the input with other standard input fields */
  margin-top: 6px;
}
</style>
