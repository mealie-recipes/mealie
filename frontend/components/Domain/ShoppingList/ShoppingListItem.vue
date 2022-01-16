<template>
  <div v-if="!edit" class="d-flex justify-space-between align-center">
    <v-checkbox
      v-model="listItem.checked"
      color="null"
      hide-details
      dense
      :label="listItem.note"
      @change="$emit('checked')"
    >
      <template #label>
        <div :class="listItem.checked ? 'strike-through' : ''">
          {{ displayText }}
        </div>
      </template>
    </v-checkbox>
    <MultiPurposeLabel v-if="listItem.label" :label="listItem.label" class="ml-auto mt-2" small />
    <div style="min-width: 72px">
      <v-menu offset-x left min-width="125px">
        <template #activator="{ on, attrs }">
          <v-btn small class="ml-2 mt-2 handle" icon v-bind="attrs" v-on="on">
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
      <v-btn small class="ml-2 mt-2 handle" icon @click="edit = true">
        <v-icon>
          {{ $globals.icons.edit }}
        </v-icon>
      </v-btn>
    </div>
  </div>
  <div v-else class="mb-1 mt-6">
    <ShoppingListItemEditor
      v-model="listItem"
      :labels="labels"
      :units="units"
      :foods="foods"
      @save="save"
      @cancel="edit = !edit"
      @delete="$emit('delete')"
      @toggle-foods="listItem.isFood = !listItem.isFood"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent, computed, ref } from "@nuxtjs/composition-api";
import ShoppingListItemEditor from "./ShoppingListItemEditor.vue";
import MultiPurposeLabel from "./MultiPurposeLabel.vue";
import { ShoppingListItemCreate } from "~/types/api-types/group";
import { MultiPurposeLabelOut } from "~/types/api-types/labels";
import { IngredientFood, IngredientUnit } from "~/types/api-types/recipe";
import { getDisplayText } from "~/composables/use-display-text";

interface actions {
  text: string;
  event: string;
}

const contextMenu: actions[] = [
  {
    text: "Edit",
    event: "edit",
  },
  {
    text: "Delete",
    event: "delete",
  },
  {
    text: "Transfer",
    event: "transfer",
  },
];

export default defineComponent({
  components: { ShoppingListItemEditor, MultiPurposeLabel },
  props: {
    value: {
      type: Object as () => ShoppingListItemCreate,
      required: true,
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
    const listItem = computed({
      get: () => {
        return props.value;
      },
      set: (val) => {
        context.emit("input", val);
      },
    });
    const edit = ref(false);
    function contextHandler(event: string) {
      if (event === "edit") {
        edit.value = true;
      } else {
        context.emit(event);
      }
    }
    function save() {
      context.emit("save");
      edit.value = false;
    }

    function handle(event: string) {
      console.log(event);
    }

    const updatedLabels = computed(() => {
      return props.labels.map((label) => {
        return {
          id: label.id,
          text: label.name,
        };
      });
    });

    const displayText = computed(() =>
      getDisplayText(listItem.value.note, listItem.value.quantity, listItem.value.food, listItem.value.unit)
    );

    return {
      displayText,
      updatedLabels,
      handle,
      save,
      contextHandler,
      edit,
      contextMenu,
      listItem,
    };
  },
});
</script>

<style lang="css">
.strike-through {
  text-decoration: line-through !important;
}
</style>