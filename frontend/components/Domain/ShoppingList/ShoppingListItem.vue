<template>
  <div v-if="!edit" class="small-checkboxes d-flex justify-space-between align-center">
    <v-checkbox v-model="listItem.checked" hide-details dense :label="listItem.note" @change="$emit('checked')">
      <template #label>
        <div>
          {{ listItem.quantity }} <v-icon size="16" class="mx-1"> {{ $globals.icons.close }} </v-icon>
          {{ listItem.note }}
        </div>
      </template>
    </v-checkbox>
    <v-chip v-if="listItem.label" class="ml-auto mt-2" small label>
      {{ listItem.label.name }}
    </v-chip>
    <v-menu offset-x left>
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
  </div>
  <div v-else class="my-1">
    <v-card outlined>
      <v-card-text>
        <v-textarea v-model="listItem.note" hide-details label="Note" rows="1" auto-grow></v-textarea>
        <div style="max-width: 300px" class="mt-3">
          <v-autocomplete
            v-model="listItem.labelId"
            name=""
            :items="labels"
            item-value="id"
            hide-details
            item-text="name"
            clearable
            :prepend-inner-icon="$globals.icons.tags"
          >
          </v-autocomplete>
        <v-checkbox  v-model="listItem.isFood" hide-details label="Treat list item as a recipe ingredient" />
        </div>
      </v-card-text>
      <v-card-actions class="ma-0 pt-0 pb-1 justify-end">
        <v-btn icon @click="save">
          <v-icon>
            {{ $globals.icons.save }}
          </v-icon>
        </v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed, ref } from "@nuxtjs/composition-api";
import { Label } from "~/api/class-interfaces/group-multiple-purpose-labels";
import { ShoppingListItemCreate } from "~/api/class-interfaces/group-shopping-lists";

interface actions {
  text: string;
  event: string;
}

const contextMenu: actions[] = [
  {
    text: "Edit",
    event: "edit",
  },
//   {
//     text: "Delete",
//     event: "delete",
//   },
//   {
//     text: "Move",
//     event: "move",
//   },
];

export default defineComponent({
  props: {
    value: {
      type: Object as () => ShoppingListItemCreate,
      required: true,
    },
    labels: {
      type: Array as () => Label[],
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

    return {
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
