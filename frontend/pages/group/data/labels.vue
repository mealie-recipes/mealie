<template>
  <div>
    <!-- Create New Dialog -->
    <BaseDialog v-model="state.createDialog" :title="$t('data-pages.labels.new-label')" :icon="$globals.icons.tags" @submit="createLabel">
      <v-card-text>
        <MultiPurposeLabel :label="createLabelData" />

        <div class="mt-4">
          <v-text-field v-model="createLabelData.name" :label="$t('general.name')"> </v-text-field>
          <InputColor v-model="createLabelData.color" />
        </div>
      </v-card-text>
    </BaseDialog>

    <!-- Edit Dialog -->
    <BaseDialog
      v-model="state.editDialog"
      :icon="$globals.icons.tags"
      :title="$t('data-pages.labels.edit-label')"
      :submit-icon="$globals.icons.save"
      :submit-text="$tc('general.save')"
      @submit="editSaveLabel"
    >
      <v-card-text v-if="editLabel">
        <MultiPurposeLabel :label="editLabel" />
        <div class="mt-4">
          <v-text-field v-model="editLabel.name" :label="$t('general.name')"> </v-text-field>
          <InputColor v-model="editLabel.color" />
        </div>
      </v-card-text>
    </BaseDialog>

    <!-- Delete Dialog -->
    <BaseDialog
      v-model="state.deleteDialog"
      :title="$tc('general.confirm')"
      :icon="$globals.icons.alertCircle"
      color="error"
      @confirm="deleteLabel"
    >
      <v-card-text>
        {{ $t("general.confirm-delete-generic") }}
        <v-row>
          <MultiPurposeLabel v-if="deleteTarget" class="mt-4 ml-4 mb-1" :label="deleteTarget" />
        </v-row>
      </v-card-text>
    </BaseDialog>

    <!-- Bulk Delete Dialog -->
    <BaseDialog
      v-model="state.bulkDeleteDialog"
      width="650px"
      :title="$tc('general.confirm')"
      :icon="$globals.icons.alertCircle"
      color="error"
      @confirm="deleteSelected"
    >
      <v-card-text>
        <p class="h4">{{ $t('general.confirm-delete-generic-items') }}</p>
        <v-card outlined>
          <v-virtual-scroll height="400" item-height="25" :items="bulkDeleteTarget">
            <template #default="{ item }">
              <v-list-item class="pb-2">
                <v-list-item-content>
                  <v-list-item-title>{{ item.name }}</v-list-item-title>
                </v-list-item-content>
              </v-list-item>
            </template>
          </v-virtual-scroll>
        </v-card>
      </v-card-text>
    </BaseDialog>

    <!-- Seed Dialog-->
    <BaseDialog
      v-model="seedDialog"
      :icon="$globals.icons.foods"
      :title="$tc('data-pages.seed-data')"
      @confirm="seedDatabase"
    >
      <v-card-text>
        <div class="pb-2">
          {{ $t("data-pages.labels.seed-dialog-text") }}
        </div>
        <v-autocomplete
          v-model="locale"
          :items="locales"
          item-text="name"
          :label="$t('data-pages.select-language')"
          class="my-3"
          hide-details
          outlined
          offset
        >
          <template #item="{ item }">
            <v-list-item-content>
              <v-list-item-title> {{ item.name }} </v-list-item-title>
              <v-list-item-subtitle>
                {{ item.progress }}% {{ $tc("language-dialog.translated") }}
              </v-list-item-subtitle>
            </v-list-item-content>
          </template>
        </v-autocomplete>

        <v-alert v-if="labels && labels.length > 0" type="error" class="mb-0 text-body-2">
          {{ $t("data-pages.foods.seed-dialog-warning") }}
        </v-alert>
      </v-card-text>
    </BaseDialog>

    <!-- Data Table -->
    <BaseCardSectionTitle :icon="$globals.icons.tags" section :title="$tc('data-pages.labels.labels')"> </BaseCardSectionTitle>
    <CrudTable
      :table-config="tableConfig"
      :headers.sync="tableHeaders"
      :data="labels || []"
      :bulk-actions="[{icon: $globals.icons.delete, text: $tc('general.delete'), event: 'delete-selected'}]"
      initial-sort="name"
      @delete-one="deleteEventHandler"
      @edit-one="editEventHandler"
      @delete-selected="bulkDeleteEventHandler"
    >
      <template #button-row>
        <BaseButton create @click="state.createDialog = true">{{ $t("general.create") }}</BaseButton>
      </template>
      <template #item.name="{ item }">
        <MultiPurposeLabel v-if="item" :label="item">
          {{ item.name }}
        </MultiPurposeLabel>
      </template>
      <template #button-bottom>
        <BaseButton @click="seedDialog = true">
          <template #icon> {{ $globals.icons.database }} </template>
          {{ $t('data-pages.seed') }}
        </BaseButton>
      </template>
    </CrudTable>
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted, reactive, ref, useContext } from "@nuxtjs/composition-api";
import type { LocaleObject } from "@nuxtjs/i18n";
import { validators } from "~/composables/use-validators";
import { useUserApi } from "~/composables/api";
import MultiPurposeLabel from "~/components/Domain/ShoppingList/MultiPurposeLabel.vue";
import { MultiPurposeLabelSummary } from "~/lib/api/types/labels";
import { useLocales } from "~/composables/use-locales";
import { useLabelData, useLabelStore } from "~/composables/store";

export default defineComponent({
  components: { MultiPurposeLabel },
  setup() {
    const userApi = useUserApi();
    const { i18n } = useContext();
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
      },
    ];

    const state = reactive({
      createDialog: false,
      editDialog: false,
      deleteDialog: false,
      bulkDeleteDialog: false,
    });

    // ============================================================
    // Labels

    const labelData = useLabelData();
    const labelStore = useLabelStore();

    // Create

    async function createLabel() {
      await labelStore.actions.createOne(labelData.data);
      labelData.reset();
      state.createDialog = false;
    }

    // Delete

    const deleteTarget = ref<MultiPurposeLabelSummary | null>(null);

    function deleteEventHandler(item: MultiPurposeLabelSummary) {
      state.deleteDialog = true;
      deleteTarget.value = item;
    }

    async function deleteLabel() {
      if (!deleteTarget.value) {
        return;
      }
      await labelStore.actions.deleteOne(deleteTarget.value.id);
      state.deleteDialog = false;
    }

    // Bulk Delete
    const bulkDeleteTarget = ref<MultiPurposeLabelSummary[]>([]);

    function bulkDeleteEventHandler(selection: MultiPurposeLabelSummary[]) {
      bulkDeleteTarget.value = selection;
      state.bulkDeleteDialog = true;
    }

    async function deleteSelected() {
      for (const item of bulkDeleteTarget.value) {
        await labelStore.actions.deleteOne(item.id);
      }
      bulkDeleteTarget.value = [];
    }

    // Edit

    const editLabel = ref<MultiPurposeLabelSummary | null>(null);

    function editEventHandler(item: MultiPurposeLabelSummary) {
      state.editDialog = true;
      editLabel.value = item;

      if (!editLabel.value.color) {
        editLabel.value.color = "#959595";
      }
    }

    async function editSaveLabel() {
      if (!editLabel.value) {
        return;
      }
      await labelStore.actions.updateOne(editLabel.value);
      state.editDialog = false;
    }

    // ============================================================
    // Seed

    const seedDialog = ref(false);
    const locale = ref("");

    const { locales: LOCALES, locale: currentLocale } = useLocales();

    onMounted(() => {
      locale.value = currentLocale.value;
    });

    const locales = LOCALES.filter((locale) =>
      (i18n.locales as LocaleObject[]).map((i18nLocale) => i18nLocale.code).includes(locale.value)
    );

    async function seedDatabase() {
      const { data } = await userApi.seeders.labels({ locale: locale.value });

      if (data) {
        labelStore.actions.refresh();
      }
    }

    return {
      state,
      tableConfig,
      tableHeaders,
      labels: labelStore.store,
      validators,

      // create
      createLabel,
      createLabelData: labelData.data,

      // edit
      editLabel,
      editEventHandler,
      editSaveLabel,

      // delete
      deleteEventHandler,
      deleteLabel,
      deleteTarget,
      bulkDeleteEventHandler,
      deleteSelected,
      bulkDeleteTarget,

      // Seed
      seedDatabase,
      locales,
      locale,
      seedDialog,
    };
  },
});
</script>
