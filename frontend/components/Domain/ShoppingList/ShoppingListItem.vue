<template>
  <v-container v-if="!edit" class="pa-0">
    <v-row no-gutters class="flex-nowrap align-center">
      <v-col :cols="itemLabelCols">
        <v-checkbox
          v-model="listItem.checked"
          class="mt-0"
          color="null"
          hide-details
          dense
          :label="listItem.note"
          @change="$emit('checked', listItem)"
        >
          <template #label>
            <div :class="listItem.checked ? 'strike-through' : ''">
              {{ listItem.display }}
            </div>
          </template>
        </v-checkbox>
      </v-col>
      <v-spacer />
      <v-col v-if="label && showLabel" cols="3" class="text-right">
        <MultiPurposeLabel :label="label" small />
      </v-col>
      <v-col cols="auto" class="text-right">
        <div v-if="!listItem.checked" style="min-width: 72px">
          <v-menu offset-x left min-width="125px">
            <template #activator="{ on, attrs }">
              <v-btn small class="ml-2 handle" icon v-bind="attrs" v-on="on">
                <v-icon>
                  {{ $globals.icons.arrowUpDown }}
                </v-icon>
              </v-btn>
            </template>
            <v-list dense>
              <v-list-item v-for="action in contextMenu" :key="action.event" dense @click="contextHandler(action.event)">
                <v-list-item-title>{{ action.text }}</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
          <v-btn small class="ml-2" icon @click="toggleEdit(true)">
            <v-icon>
              {{ $globals.icons.edit }}
            </v-icon>
          </v-btn>
        </div>
      </v-col>
    </v-row>
    <v-row v-if="listItem.checked" no-gutters class="mb-2">
      <v-col cols="auto">
        <div class="text-caption font-weight-light font-italic">
          {{ $t("shopping-list.completed-on", {date: new Date(listItem.updateAt+"Z").toLocaleDateString($i18n.locale)}) }}
        </div>
      </v-col>
    </v-row>
  </v-container>
  <div v-else class="mb-1 mt-6">
    <ShoppingListItemEditor
      v-model="localListItem"
      :labels="labels"
      :units="units"
      :foods="foods"
      @save="save"
      @cancel="toggleEdit(false)"
      @delete="$emit('delete')"
      @toggle-foods="localListItem.isFood = !localListItem.isFood"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent, computed, ref, useContext } from "@nuxtjs/composition-api";
import ShoppingListItemEditor from "./ShoppingListItemEditor.vue";
import MultiPurposeLabel from "./MultiPurposeLabel.vue";
import { ShoppingListItemOut } from "~/lib/api/types/group";
import { MultiPurposeLabelOut, MultiPurposeLabelSummary } from "~/lib/api/types/labels";
import { IngredientFood, IngredientUnit } from "~/lib/api/types/recipe";

interface actions {
  text: string;
  event: string;
}

export default defineComponent({
  components: { ShoppingListItemEditor, MultiPurposeLabel },
  props: {
    value: {
      type: Object as () => ShoppingListItemOut,
      required: true,
    },
    showLabel: {
      type: Boolean,
      default: false,
    },
    labels: {
      type: Array as () => MultiPurposeLabelOut[],
      required: true,
    },
    units: {
      type: Array as () => IngredientUnit[],
      required: true,
    },
    foods: {
      type: Array as () => IngredientFood[],
      required: true,
    },
  },
  setup(props, context) {
    const { i18n } = useContext();
    const itemLabelCols = ref<string>(props.value.checked ? "auto" : props.showLabel ? "6" : "8");

    const contextMenu: actions[] = [
      {
        text: i18n.t("general.edit") as string,
        event: "edit",
      },
      {
        text: i18n.t("general.delete") as string,
        event: "delete",
      },
      {
        text: i18n.t("general.transfer") as string,
        event: "transfer",
      },
    ];

    // copy prop value so a refresh doesn't interrupt the user
    const localListItem = ref(Object.assign({}, props.value));
    const listItem = computed({
      get: () => {
        return props.value;
      },
      set: (val) => {
        // keep local copy in sync
        localListItem.value = val;
        context.emit("input", val);
      },
    });
    const edit = ref(false);
    function toggleEdit(val = !edit.value) {
      if (val) {
        // update local copy of item with the current value
        localListItem.value = props.value;
      }

      edit.value = val;
    }

    function contextHandler(event: string) {
      if (event === "edit") {
        toggleEdit(true);
      } else {
        context.emit(event);
      }
    }
    function save() {
      context.emit("save", localListItem.value);
      edit.value = false;
    }

    const updatedLabels = computed(() => {
      return props.labels.map((label) => {
        return {
          id: label.id,
          text: label.name,
        };
      });
    });

    /**
     * Gets the label for the shopping list item. Either the label assign to the item
     * or the label of the food applied.
     */
    const label = computed<MultiPurposeLabelSummary | undefined>(() => {
      // @ts-ignore - it _might_ exists
      if (listItem.value.label) {
        // @ts-ignore - it _might_ exists
        return listItem.value.label as MultiPurposeLabelSummary;
      }

      if (listItem.value.food?.label) {
        return listItem.value.food.label;
      }

      return undefined;
    });

    return {
      updatedLabels,
      save,
      contextHandler,
      edit,
      contextMenu,
      itemLabelCols,
      listItem,
      localListItem,
      label,
      toggleEdit,
    };
  },
});
</script>

<style lang="css">
.strike-through {
  text-decoration: line-through !important;
}
</style>
