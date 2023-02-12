<template>
  <div>
    <v-menu v-model="state.menu" offset-y bottom nudge-bottom="3" :close-on-content-click="false">
      <template #activator="{ on, attrs }">
        <v-btn small color="accent" dark v-bind="attrs" v-on="on">
          <slot></slot>
        </v-btn>
      </template>
      <v-card width="400">
        <v-card-text class="">
          <div>
            <v-text-field v-model="state.search" dense label="Search" clearable />
          </div>
          <div v-if="filtered.length > 0">
            <v-list-item-group v-model="selected" multiple>
              <v-virtual-scroll :items="filtered" height="300" item-height="50">
                <template #default="{ item }">
                  <v-list-item :key="item.id" dense :value="item">
                    <template #default="{ active }">
                      <v-list-item-action>
                        <v-checkbox :input-value="active"></v-checkbox>
                      </v-list-item-action>

                      <v-list-item-content>
                        <v-list-item-title> {{ item.name }}</v-list-item-title>
                      </v-list-item-content>
                    </template>
                  </v-list-item>
                  <v-divider></v-divider>
                </template>
              </v-virtual-scroll>
            </v-list-item-group>
          </div>
          <div v-else>
            <v-alert type="info" text> No results found </v-alert>
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
  },
  setup(props, context) {
    const state = reactive({
      search: "",
      menu: false,
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
      state,
      selected,
      filtered,
    };
  },
});
</script>
