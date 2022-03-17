<template>
  <div>
    <v-card-actions>
      <v-menu v-if="tableConfig.hideColumns" offset-y bottom nudge-bottom="6" :close-on-content-click="false">
        <template #activator="{ on, attrs }">
          <v-btn color="accent" class="mr-1" dark v-bind="attrs" v-on="on">
            <v-icon>
              {{ $globals.icons.cog }}
            </v-icon>
          </v-btn>
        </template>
        <v-card>
          <v-card-text>
            <v-checkbox
              v-for="itemValue in headers"
              :key="itemValue.text + itemValue.show"
              v-model="filteredHeaders"
              :value="itemValue.value"
              dense
              flat
              inset
              :label="itemValue.text"
              hide-details
            ></v-checkbox>
          </v-card-text>
        </v-card>
      </v-menu>
      <BaseOverflowButton
        v-if="bulkActions.length > 0"
        :disabled="selected.length < 1"
        mode="event"
        color="info"
        :items="bulkActions"
        v-on="bulkActionListener"
      >
      </BaseOverflowButton>
      <slot name="button-row"> </slot>
    </v-card-actions>
    <div class="mx-2 clip-width">
      <v-text-field v-model="search" :label="$tc('search.search')"></v-text-field>
    </div>
    <v-data-table
      v-model="selected"
      item-key="id"
      show-select
      :headers="activeHeaders"
      :items="data || []"
      :items-per-page="15"
      :search="search"
      class="elevation-0"
    >
      <template v-for="header in activeHeaders" #[`item.${header.value}`]="{ item }">
        <slot :name="'item.' + header.value" v-bind="{ item }"> {{ item[header.value] }}</slot>
      </template>
      <template #item.actions="{ item }">
        <BaseButtonGroup
          :buttons="[
            {
              icon: $globals.icons.edit,
              text: 'Edit',
              event: 'edit',
            },
            {
              icon: $globals.icons.delete,
              text: 'Delete',
              event: 'delete',
            },
          ]"
          @delete="$emit('delete-one', item)"
          @edit="$emit('edit-one', item)"
        />
      </template>
    </v-data-table>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, ref } from "@nuxtjs/composition-api";

export interface TableConfig {
  hideColumns: boolean;
}

export interface TableHeaders {
  text: string;
  value: string;
  show: boolean;
  align?: string;
}

export interface BulkAction {
  icon: string;
  text: string;
  event: string;
}

export default defineComponent({
  props: {
    tableConfig: {
      type: Object as () => TableConfig,
      default: () => ({
        hideColumns: false,
      }),
    },
    headers: {
      type: Array as () => TableHeaders[],
      required: true,
    },
    data: {
      type: Array as () => any[],
      required: true,
    },
    bulkActions: {
      type: Array as () => BulkAction[],
      default: () => [],
    },
  },
  setup(props, context) {
    // ===========================================================
    // Reactive Headers
    const filteredHeaders = ref<string[]>([]);

    // Set default filtered
    filteredHeaders.value = (() => {
      const filtered: string[] = [];
      props.headers.forEach((element) => {
        if (element.show) {
          filtered.push(element.value);
        }
      });
      return filtered;
    })();

    const activeHeaders = computed(() => {
      const filtered = props.headers.filter((header) => filteredHeaders.value.includes(header.value));
      filtered.push({ text: "", value: "actions", show: true, align: "right" });
      return filtered;
    });

    const selected = ref<any[]>([]);

    // ===========================================================
    // Bulk Action Event Handler

    const bulkActionListener = computed(() => {
      const handlers: { [key: string]: () => void } = {};

      props.bulkActions.forEach((action) => {
        handlers[action.event] = () => {
          context.emit(action.event, selected.value);
        };
      });

      return handlers;
    });

    const search = ref("");

    return {
      selected,
      filteredHeaders,
      activeHeaders,
      bulkActionListener,
      search,
    };
  },
});
</script>

<style>
.clip-width {
  max-width: 400px;
}
</style>
