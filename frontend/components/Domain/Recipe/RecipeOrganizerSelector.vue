<template>
  <v-autocomplete
    v-model="selected"
    :items="items"
    :value="value"
    :label="label"
    chips
    deletable-chips
    item-text="name"
    multiple
    :prepend-inner-icon="$globals.icons.tags"
    return-object
    v-bind="inputAttrs"
  >
    <template #selection="data">
      <v-chip
        :key="data.index"
        class="ma-1"
        :input-value="data.selected"
        close
        label
        color="accent"
        dark
        @click:close="removeByIndex(data.index)"
      >
        {{ data.item.name || data.item }}
      </v-chip>
    </template>
  </v-autocomplete>
</template>

<script lang="ts">
import { defineComponent, useContext } from "@nuxtjs/composition-api";
import { computed, onMounted } from "vue-demi";
import { RecipeCategory, RecipeTag } from "~/types/api-types/user";
import { RecipeTool } from "~/types/api-types/admin";

type OrganizerType = "tag" | "category" | "tool";

export default defineComponent({
  props: {
    value: {
      type: Array as () => (RecipeTag | RecipeCategory | RecipeTool)[] | undefined,
      required: true,
    },
    /**
     * The type of organizer to use.
     */
    selectorType: {
      type: String as () => OrganizerType,
      required: true,
    },
    /**
     * List of items that are available to be chosen from
     */
    items: {
      type: Array as () => (RecipeTag | RecipeCategory | RecipeTool)[],
      required: true,
    },
    inputAttrs: {
      type: Object as () => Record<string, any>,
      default: () => ({}),
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
        case "tag":
          return i18n.t("tag.tags");
        case "category":
          return i18n.t("category.categories");
        case "tool":
          return "Tools";
        default:
          return "Organizer";
      }
    });

    function removeByIndex(index: number) {
      if (selected.value === undefined) {
        return;
      }

      const newSelected = selected.value.filter((_, i) => i !== index);
      selected.value = [...newSelected];
    }

    return {
      label,
      selected,
      removeByIndex,
    };
  },
});
</script>
