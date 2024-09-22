<template>
  <div>
    <v-menu v-model="state.menu" offset-y bottom nudge-bottom="3" :close-on-content-click="false">
      <template #activator="{ on, attrs }">
        <v-badge :value="selected.length > 0" small overlap color="primary" :content="selected.length">
          <v-btn small color="accent" dark v-bind="attrs" v-on="on">
            <slot></slot>
          </v-btn>
        </v-badge>
      </template>
      <v-card width="400">
        <v-card-text>
          <v-text-field v-model="state.search" class="mb-2" hide-details dense :label="$tc('search.search')" clearable />
          <div class="d-flex py-4">
            <v-switch
              v-if="requireAll != undefined"
              v-model="requireAllValue"
              dense
              small
              hide-details
              class="my-auto"
              :label="`${requireAll ? $tc('search.has-all') : $tc('search.has-any')}`"
            />
            <v-spacer />
            <v-btn
              small
              color="accent"
              class="mr-2 my-auto"
              @click="clearSelection"
            >
              {{ $tc("search.clear-selection") }}
            </v-btn>
          </div>
          <v-card v-if="filtered.length > 0" flat outlined>
            <v-radio-group v-model="selectedRadio" class="ma-0 pa-0">
            <v-virtual-scroll :items="filtered" height="300" item-height="51">
              <template #default="{ item }">
                  <v-list-item :key="item.id" dense :value="item">
                    <v-list-item-action>
                      <v-radio v-if="radio" :value="item" @click="handleRadioClick(item)" />
                      <v-checkbox v-else v-model="selected" :value="item" />
                    </v-list-item-action>
                    <v-list-item-content>
                      <v-list-item-title> {{ item.name }} </v-list-item-title>
                    </v-list-item-content>
                  </v-list-item>
                <v-divider></v-divider>
              </template>
            </v-virtual-scroll>
            </v-radio-group>
          </v-card>
          <div v-else>
            <v-alert type="info" text> {{ $tc('search.no-results') }} </v-alert>
          </div>
        </v-card-text>
      </v-card>
    </v-menu>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, computed } from "@nuxtjs/composition-api";

export interface SelectableItem {
  id: string;
  name: string;
}

export default defineComponent({
  props: {
    items: {
      type: Array as () => SelectableItem[],
      required: true,
    },
    value: {
      type: Array as () => any[],
      required: true,
    },
    requireAll: {
      type: Boolean,
      default: undefined,
    },
    radio: {
      type: Boolean,
      default: false,
    },
  },
  setup(props, context) {
    const state = reactive({
      search: "",
      menu: false,
    });

    const requireAllValue = computed({
      get: () => props.requireAll,
      set: (value) => {
        context.emit("update:requireAll", value);
      },
    });

    const selected = computed({
      get: () => props.value as SelectableItem[],
      set: (value) => {
        context.emit("input", value);
      },
    });

    const selectedRadio = computed({
      get: () => (selected.value.length > 0 ? selected.value[0] : null),
      set: (value) => {
        context.emit("input", value ? [value] : []);
      },
    });

    const filtered = computed(() => {
      if (!state.search) {
        return props.items;
      }

      return props.items.filter((item) => item.name.toLowerCase().includes(state.search.toLowerCase()));
    });

    const handleRadioClick = (item: SelectableItem) => {
      if (selectedRadio.value === item) {
        selectedRadio.value = null;
      }
    };

    function clearSelection() {
      selected.value = [];
      selectedRadio.value = null;
      state.search = "";
    }

    return {
      requireAllValue,
      state,
      selected,
      selectedRadio,
      filtered,
      handleRadioClick,
      clearSelection,
    };
  },
});
</script>
