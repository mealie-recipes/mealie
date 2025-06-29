<template>
  <div>
    <v-menu
      v-model="state.menu"
      offset-y
      bottom
      nudge-bottom="3"
      :close-on-content-click="false"
    >
      <template #activator="{ props }">
        <v-badge
          :model-value="selected.length > 0"
          size="small"
          color="primary"
          :content="selected.length"
        >
          <v-btn
            size="small"
            color="accent"
            dark
            v-bind="props"
          >
            <slot />
          </v-btn>
        </v-badge>
      </template>
      <v-card width="400">
        <v-card-text>
          <v-text-field
            v-model="state.search"
            class="mb-2"
            hide-details
            density="comfortable"
            :variant="'underlined'"
            :label="$t('search.search')"
            clearable
          />
          <div class="d-flex py-4 px-1">
            <v-switch
              v-if="requireAll != undefined"
              v-model="requireAllValue"
              density="compact"
              size="small"
              hide-details
              class="my-auto"
              color="primary"
              :label="`${requireAll ? $t('search.has-all') : $t('search.has-any')}`"
            />
            <v-spacer />
            <v-btn
              size="small"
              color="accent"
              class="mr-2 my-auto"
              @click="clearSelection"
            >
              {{ $t("search.clear-selection") }}
            </v-btn>
          </div>
          <v-card
            v-if="filtered.length > 0"
            flat
            variant="text"
          >
            <!-- radio filters -->
            <v-radio-group
              v-if="radio"
              v-model="selectedRadio"
              class="ma-0 pa-0"
            >
              <v-virtual-scroll
                :items="filtered"
                height="300"
                item-height="51"
              >
                <template #default="{ item }">
                  <v-list-item
                    :key="item.id"
                    :value="item"
                    :title="item.name"
                  >
                    <template #prepend>
                      <v-list-item-action start>
                        <v-radio
                          v-if="radio"
                          :value="item"
                          color="primary"
                          @click="handleRadioClick(item)"
                        />
                      </v-list-item-action>
                    </template>
                  </v-list-item>
                  <v-divider />
                </template>
              </v-virtual-scroll>
            </v-radio-group>
            <!-- checkbox filters -->
            <v-row v-else class="mt-1">
              <v-virtual-scroll
                :items="filtered"
                height="300"
                item-height="51"
              >
                <template #default="{ item }">
                  <v-list-item
                    :key="item.id"
                    :value="item"
                    :title="item.name"
                  >
                    <template #prepend>
                      <v-list-item-action start>
                        <v-checkbox-btn
                          v-model="selected"
                          :value="item"
                          color="primary"
                        />
                      </v-list-item-action>
                    </template>
                  </v-list-item>
                  <v-divider />
                </template>
              </v-virtual-scroll>
            </v-row>
          </v-card>
          <div v-else>
            <v-alert
              type="info"
              :text="$t('search.no-results')"
              class="mb-0"
            />
          </div>
        </v-card-text>
      </v-card>
    </v-menu>
  </div>
</template>

<script lang="ts">
export interface SelectableItem {
  id: string;
  name: string;
}

export default defineNuxtComponent({
  props: {
    items: {
      type: Array as () => SelectableItem[],
      required: true,
    },
    modelValue: {
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
  emits: ["update:requireAll", "update:modelValue"],
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
      get: () => props.modelValue as SelectableItem[],
      set: (value) => {
        context.emit("update:modelValue", value);
      },
    });

    const selectedRadio = computed({
      get: () => (selected.value.length > 0 ? selected.value[0] : null),
      set: (value) => {
        context.emit("update:modelValue", value ? [value] : []);
      },
    });

    const filtered = computed(() => {
      if (!state.search) {
        return props.items;
      }

      return props.items.filter(item => item.name.toLowerCase().includes(state.search.toLowerCase()));
    });

    const handleCheckboxClick = (item: SelectableItem) => {
      console.log(selected.value, item);
      if (selected.value.includes(item)) {
        selected.value = selected.value.filter(i => i !== item);
      }
      else {
        selected.value.push(item);
      }
    };

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
      handleCheckboxClick,
      handleRadioClick,
      clearSelection,
    };
  },
});
</script>
