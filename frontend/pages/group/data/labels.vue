<template>
  <div>
    <!-- Seed Dialog -->
    <BaseDialog
      v-model="seedDialog"
      :icon="$globals.icons.foods"
      :title="$t('data-pages.seed-data')"
      can-confirm
      @confirm="seedDatabase"
    >
      <v-card-text>
        <div class="pb-2">
          {{ $t("data-pages.labels.seed-dialog-text") }}
        </div>
        <v-autocomplete
          v-model="locale"
          :items="locales"
          :custom-filter="normalizeFilter"
          item-title="name"
          :label="$t('data-pages.select-language')"
          class="my-3"
          hide-details
          variant="outlined"
          offset
        >
          <template #item="{ item, props }">
            <v-list-item v-bind="props">
              <v-list-item-subtitle>
                {{ item.raw.progress }}% {{ $t("language-dialog.translated") }}
              </v-list-item-subtitle>
            </v-list-item>
          </template>
        </v-autocomplete>

        <v-alert
          v-if="labels && labels.length > 0"
          type="error"
          class="mb-0 text-body-2"
        >
          {{ $t("data-pages.foods.seed-dialog-warning") }}
        </v-alert>
      </v-card-text>
    </BaseDialog>

    <GroupDataPage
      :icon="$globals.icons.tags"
      :title="$t('data-pages.labels.labels')"
      :table-headers="tableHeaders"
      :table-config="tableConfig"
      :data="labelStore.store.value || []"
      :bulk-actions="[{ icon: $globals.icons.delete, text: $t('general.delete'), event: 'delete-selected' }]"
      :create-form="createForm"
      :edit-form="editForm"
      @create-one="handleCreate"
      @edit-one="handleEdit"
      @delete-one="labelStore.actions.deleteOne"
      @delete-many="labelStore.actions.deleteMany"
    >
      <template #[`item.name`]="{ item }">
        <MultiPurposeLabel
          v-if="item"
          :label="item"
        >
          {{ item.name }}
        </MultiPurposeLabel>
      </template>

      <template #table-button-bottom>
        <BaseButton @click="seedDialog = true">
          <template #icon>
            {{ $globals.icons.database }}
          </template>
          {{ $t('data-pages.seed') }}
        </BaseButton>
      </template>
    </GroupDataPage>
  </div>
</template>

<script setup lang="ts">
import type { LocaleObject } from "@nuxtjs/i18n";
import { validators } from "~/composables/use-validators";
import { useUserApi } from "~/composables/api";
import MultiPurposeLabel from "~/components/Domain/ShoppingList/MultiPurposeLabel.vue";
import { fieldTypes } from "~/composables/forms";
import type { MultiPurposeLabelSummary } from "~/lib/api/types/labels";
import type { AutoFormItems } from "~/types/auto-forms";
import { useLocales } from "~/composables/use-locales";
import { normalizeFilter } from "~/composables/use-utils";
import { useLabelData, useLabelStore } from "~/composables/store";

const userApi = useUserApi();
const i18n = useI18n();

const tableConfig = {
  hideColumns: true,
  canExport: true,
};
const tableHeaders = [
  {
    text: i18n.t("general.id"),
    value: "id",
    show: false,
  },
  {
    text: i18n.t("general.name"),
    value: "name",
    show: true,
    sortable: true,
  },
];

const labelStore = useLabelStore();

// ============================================================
// Form items (shared)
const formItems = [
  {
    label: i18n.t("general.name"),
    varName: "name",
    type: fieldTypes.TEXT,
    rules: [validators.required],
  },
  {
    label: i18n.t("general.color"),
    varName: "color",
    type: fieldTypes.COLOR,
  },
] as AutoFormItems;

// ============================================================
// Create
const createForm = reactive({
  items: formItems,
  data: {
    name: "",
    color: "#7417BE",
  } as MultiPurposeLabelSummary,
});

// ============================================================
// Seed

const seedDialog = ref(false);
const locale = ref("");

const { locales: LOCALES, locale: currentLocale } = useLocales();

onMounted(() => {
  locale.value = currentLocale.value;
});

async function seedDatabase() {
  const { data } = await userApi.seeders.labels({ locale: locale.value });

  if (data) {
    labelStore.actions.refresh();
  }
}
</script>
