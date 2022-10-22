<template>
  <div>
    <!-- Create New Dialog -->
    <BaseDialog v-model="state.createDialog" title="New Label" :icon="$globals.icons.tags" @submit="createLabel">
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
      title="Edit Label"
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
          label="Select Language"
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

    <!-- Recipe Data Table -->
    <BaseCardSectionTitle :icon="$globals.icons.tags" section title="Labels"> </BaseCardSectionTitle>
    <CrudTable
      :table-config="tableConfig"
      :headers.sync="tableHeaders"
      :data="labels || []"
      :bulk-actions="[]"
      @delete-one="deleteEventHandler"
      @edit-one="editEventHandler"
    >
      <template #button-row>
        <BaseButton create @click="state.createDialog = true">
          <template #icon> {{ $globals.icons.tags }} </template>
          {{ $t("general.create") }}
        </BaseButton>
      </template>
      <template #item.name="{ item }">
        <MultiPurposeLabel v-if="item" :label="item">
          {{ item.name }}
        </MultiPurposeLabel>
      </template>
      <template #button-bottom>
        <BaseButton @click="seedDialog = true">
          <template #icon> {{ $globals.icons.database }} </template>
          Seed
        </BaseButton>
      </template>
    </CrudTable>
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted, reactive, ref } from "@nuxtjs/composition-api";
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
    const tableConfig = {
      hideColumns: true,
      canExport: true,
    };
    const tableHeaders = [
      {
        text: "Id",
        value: "id",
        show: false,
      },
      {
        text: "Name",
        value: "name",
        show: true,
      },
    ];

    const state = reactive({
      createDialog: false,
      editDialog: false,
      deleteDialog: false,
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

    // Edit

    const editLabel = ref<MultiPurposeLabelSummary | null>(null);

    function editEventHandler(item: MultiPurposeLabelSummary) {
      state.editDialog = true;
      editLabel.value = item;

      if (!editLabel.value.color) {
        editLabel.value.color = "#E0E0E0";
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

    const { locales: LOCALES, locale: currentLocale, i18n } = useLocales();

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
      labels: labelStore.labels,
      validators,

      deleteEventHandler,
      deleteLabel,
      editLabel,
      editEventHandler,
      editSaveLabel,
      createLabel,
      createLabelData: labelData.data,

      // Seed
      seedDatabase,
      locales,
      locale,
      seedDialog,
    };
  },
});
</script>
