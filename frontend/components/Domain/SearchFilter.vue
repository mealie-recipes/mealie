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
          v-memo="[selectedCount]"
          :model-value="selectedCount > 0"
          size="small"
          color="primary"
          :content="selectedCount"
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
            v-model="searchInput"
            v-memo="[searchInput]"
            class="mb-2"
            hide-details
            density="comfortable"
            :variant="'underlined'"
            :label="$t('search.search')"
            clearable
          />
          <div />
          <div class="d-flex flex-wrap py-4 px-1 align-center">
            <v-btn-toggle
              v-if="requireAll != undefined"
              v-model="combinator"
              mandatory
              density="compact"
              variant="outlined"
              color="primary"
              class="my-1"
            >
              <v-btn value="hasAll">
                {{ $t('search.has-all') }}
              </v-btn>
              <v-btn value="hasAny">
                {{ $t('search.has-any') }}
              </v-btn>
            </v-btn-toggle>
            <v-spacer />
            <v-btn
              size="small"
              color="accent"
              class="my-1"
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
                    :key="`radio-${item.id}`"
                    v-memo="[item.id, item.name, selectedRadio?.id]"
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
                    :key="`checkbox-${item.id}`"
                    v-memo="[item.id, item.name, selectedIds.has(item.id)]"
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
import type { ISearchableItem } from "~/composables/use-search";
import { useSearch } from "~/composables/use-search";

export default defineNuxtComponent({
  props: {
    items: {
      type: Array as () => ISearchableItem[],
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
      menu: false,
    });

    // Use the search composable
    const { search: searchInput, filtered } = useSearch(computed(() => props.items));

    const combinator = computed({
      get: () => (props.requireAll ? "hasAll" : "hasAny"),
      set: (value) => {
        context.emit("update:requireAll", value === "hasAll");
      },
    });

    // Use shallowRef to prevent deep reactivity on large arrays
    const selected = computed({
      get: () => props.modelValue as ISearchableItem[],
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

    const selectedCount = computed(() => selected.value.length);
    const selectedIds = computed(() => {
      return new Set(selected.value.map(item => item.id));
    });

    const handleRadioClick = (item: ISearchableItem) => {
      if (selectedRadio.value === item) {
        selectedRadio.value = null;
      }
    };

    function clearSelection() {
      selected.value = [];
      selectedRadio.value = null;
      searchInput.value = "";
    }

    return {
      combinator,
      state,
      searchInput,
      selected,
      selectedRadio,
      selectedCount,
      selectedIds,
      filtered,
      handleRadioClick,
      clearSelection,
    };
  },
});
</script>
