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
    :prepend-inner-icon="selectorType === Organizer.Tool ? $globals.icons.potSteam : $globals.icons.tags"
    return-object
    v-bind="inputAttrs"
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
import { defineComponent, ref, useContext } from "@nuxtjs/composition-api";
import { computed, onMounted } from "vue-demi";
import RecipeOrganizerDialog from "./RecipeOrganizerDialog.vue";
import { RecipeCategory, RecipeTag } from "~/lib/api/types/user";
import { RecipeTool } from "~/lib/api/types/admin";
import { useTagStore } from "~/composables/store/use-tag-store";
import { useCategoryStore, useToolStore } from "~/composables/store";
import { Organizer, RecipeOrganizer } from "~/types/recipe/organizers";

export default defineComponent({
  components: {
    RecipeOrganizerDialog,
  },
  props: {
    value: {
      type: Array as () => (RecipeTag | RecipeCategory | RecipeTool | string)[] | undefined,
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

    const { i18n } = useContext();

    const label = computed(() => {
      switch (props.selectorType) {
        case Organizer.Tag:
          return i18n.t("tag.tags");
        case Organizer.Category:
          return i18n.t("category.categories");
        case Organizer.Tool:
          return i18n.t("tool.tools");
        default:
          return i18n.t("general.organizer");
      }
    });

    // ===========================================================================
    // Store & Items Setup

    const store = (() => {
      switch (props.selectorType) {
        case Organizer.Tag:
          return useTagStore();
        case Organizer.Tool:
          return useToolStore();
        default:
          return useCategoryStore();
      }
    })();

    const items = computed(() => {
      if (!props.returnObject) {
        return store.items.value.map((item) => item.name);
      }
      return store.items.value;
    });

    function removeByIndex(index: number) {
      if (selected.value === undefined) {
        return;
      }
      const newSelected = selected.value.filter((_, i) => i !== index);
      selected.value = [...newSelected];
    }

    function appendCreated(item: RecipeTag | RecipeCategory | RecipeTool) {
      console.log(item);
      if (selected.value === undefined) {
        return;
      }

      selected.value = [...selected.value, item];
    }

    const dialog = ref(false);

    return {
      Organizer,
      appendCreated,
      dialog,
      storeItem: items,
      label,
      selected,
      removeByIndex,
    };
  },
});
</script>
