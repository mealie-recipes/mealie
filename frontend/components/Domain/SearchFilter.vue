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
          <v-switch
            v-if="requireAll != undefined"
            v-model="requireAllValue"
            dense
            small
            :label="`${requireAll ? $tc('search.has-all') : $tc('search.has-any')}`"
          >
          </v-switch>
          <v-card v-if="filtered.length > 0" flat outlined>
            <v-virtual-scroll :items="filtered" height="300" item-height="51">
              <template #default="{ item }">
                <v-list-item :key="item.id" dense :value="item">
                  <v-list-item-action>
                    <v-checkbox v-model="selected" :value="item"></v-checkbox>
                  </v-list-item-action>
                  <v-list-item-content>
                    <v-list-item-title> {{ item.name }}</v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
                <v-divider></v-divider>
              </template>
            </v-virtual-scroll>
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

    const filtered = computed(() => {
      if (!state.search) {
        return props.items;
      }

      return props.items.filter((item) => item.name.toLowerCase().includes(state.search.toLowerCase()));
    });

    return {
      requireAllValue,
      state,
      selected,
      filtered,
    };
  },
});
</script>
