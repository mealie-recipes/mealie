//TODO: Prevent fetching Categories/Tags multiple time when selector is on page multiple times

<template>
  <v-autocomplete
    v-model="selected"
    :items="activeItems"
    :value="value"
    :label="inputLabel"
    chips
    deletable-chips
    :dense="dense"
    item-text="name"
    persistent-hint
    multiple
    :hide-details="hideDetails"
    :hint="hint"
    :solo="solo"
    :return-object="returnObject"
    :prepend-inner-icon="$globals.icons.tags"
    v-bind="$attrs"
    @input="emitChange"
  >
    <template #selection="data">
      <v-chip
        v-if="showSelected"
        :key="data.index"
        :small="dense"
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
    <template #append-outer>
      <RecipeCategoryTagDialog v-if="showAdd" :tag-dialog="tagSelector" @created-item="pushToItem" />
    </template>
  </v-autocomplete>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, reactive, toRefs, useContext, watch } from "@nuxtjs/composition-api";
import RecipeCategoryTagDialog from "./RecipeCategoryTagDialog.vue";
import { useTags, useCategories } from "~/composables/recipes";
import { RecipeCategory, RecipeTag } from "~/types/api-types/user";

const MOUNTED_EVENT = "mounted";

export default defineComponent({
  components: {
    RecipeCategoryTagDialog,
  },
  props: {
    value: {
      type: Array as () => (RecipeTag | RecipeCategory | string)[],
      required: true,
    },
    solo: {
      type: Boolean,
      default: false,
    },
    dense: {
      type: Boolean,
      default: true,
    },
    returnObject: {
      type: Boolean,
      default: true,
    },
    tagSelector: {
      type: Boolean,
      default: false,
    },
    hint: {
      type: String,
      default: null,
    },
    showAdd: {
      type: Boolean,
      default: false,
    },
    showLabel: {
      type: Boolean,
      default: true,
    },
    showSelected: {
      type: Boolean,
      default: true,
    },
    hideDetails: {
      type: Boolean,
      default: false,
    },
  },

  setup(props, context) {
    const { allTags, useAsyncGetAll: getAllTags } = useTags();
    const { allCategories, useAsyncGetAll: getAllCategories } = useCategories();
    getAllCategories();
    getAllTags();

    const state = reactive({
      selected: props.value,
    });
    watch(
      () => props.value,
      (val) => {
        state.selected = val;
      }
    );

    const { i18n } = useContext();
    const inputLabel = computed(() => {
      if (!props.showLabel) return null;
      return props.tagSelector ? i18n.t("tag.tags") : i18n.t("recipe.categories");
    });

    const activeItems = computed(() => {
      let itemObjects: RecipeTag[] | RecipeCategory[] | null;
      if (props.tagSelector) itemObjects = allTags.value;
      else {
        itemObjects = allCategories.value;
      }
      if (props.returnObject) return itemObjects;
      else {
        return itemObjects?.map((x: RecipeTag | RecipeCategory) => x.name);
      }
    });

    function emitChange() {
      context.emit("input", state.selected);
    }

    // TODO Is this needed?
    onMounted(() => {
      context.emit(MOUNTED_EVENT);
    });

    function removeByIndex(index: number) {
      state.selected.splice(index, 1);
    }

    function pushToItem(createdItem: RecipeTag | RecipeCategory) {
      // TODO: Remove excessive get calls
      getAllCategories();
      getAllTags();
      state.selected.push(createdItem);
    }

    return {
      ...toRefs(state),
      inputLabel,
      activeItems,
      emitChange,
      removeByIndex,
      pushToItem,
    };
  },
});
</script>
