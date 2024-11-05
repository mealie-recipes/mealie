<template>
  <div>
    <!-- Merge Dialog -->
    <BaseDialog v-model="mergeDialog" :icon="$globals.icons.units" :title="$t('data-pages.units.combine-unit')" @confirm="mergeUnits">
      <v-card-text>
      <i18n path="data-pages.units.combine-unit-description">
        <template #source-unit-will-be-deleted>
          <strong> {{ $t('data-pages.recipes.source-unit-will-be-deleted') }} </strong>
        </template>
      </i18n>

        <v-autocomplete v-model="fromUnit" return-object :items="store" item-text="id" :label="$t('data-pages.units.source-unit')">
          <template #selection="{ item }"> {{ item.name }}</template>
          <template #item="{ item }"> {{ item.name }} </template>
        </v-autocomplete>
        <v-autocomplete v-model="toUnit" return-object :items="store" item-text="id" :label="$t('data-pages.units.target-unit')">
          <template #selection="{ item }"> {{ item.name }}</template>
          <template #item="{ item }"> {{ item.name }} </template>
        </v-autocomplete>

        <template v-if="canMerge && fromUnit && toUnit">
          <div class="text-center">{{ $t('data-pages.units.merging-unit-into-unit', [fromUnit.name, toUnit.name]) }}</div>
        </template>
      </v-card-text>
    </BaseDialog>

    <!-- Create Dialog -->
    <BaseDialog
      v-model="createDialog"
      :icon="$globals.icons.units"
      :title="$t('data-pages.units.create-unit')"
      :submit-icon="$globals.icons.save"
      :submit-text="$tc('general.save')"
      @submit="createUnit"
    >
      <v-card-text>
        <v-form ref="domNewUnitForm">
          <v-text-field
            v-model="createTarget.name"
            autofocus
            :label="$t('general.name')"
            :hint="$t('data-pages.units.example-unit-singular')"
            :rules="[validators.required]"
          ></v-text-field>
          <v-text-field
            v-model="createTarget.pluralName"
            :label="$t('general.plural-name')"
            :hint="$t('data-pages.units.example-unit-plural')"
          ></v-text-field>
          <v-text-field
            v-model="createTarget.abbreviation"
            :label="$t('data-pages.units.abbreviation')"
            :hint="$t('data-pages.units.example-unit-abbreviation-singular')"
          ></v-text-field>
          <v-text-field
            v-model="createTarget.pluralAbbreviation"
            :label="$t('data-pages.units.plural-abbreviation')"
            :hint="$t('data-pages.units.example-unit-abbreviation-plural')"
          ></v-text-field>
          <v-text-field v-model="createTarget.description" :label="$t('data-pages.units.description')"></v-text-field>
          <v-checkbox v-model="createTarget.fraction" hide-details :label="$t('data-pages.units.display-as-fraction')"></v-checkbox>
          <v-checkbox v-model="createTarget.useAbbreviation" hide-details :label="$t('data-pages.units.use-abbreviation')"></v-checkbox>
        </v-form>
      </v-card-text>
    </BaseDialog>

    <!-- Alias Sub-Dialog -->
    <RecipeDataAliasManagerDialog
      v-if="editTarget"
      :value="aliasManagerDialog"
      :data="editTarget"
      @submit="updateUnitAlias"
      @cancel="aliasManagerDialog = false"
    />

    <!-- Edit Dialog -->
    <BaseDialog
      v-model="editDialog"
      :icon="$globals.icons.units"
      :title="$t('data-pages.units.edit-unit')"
      :submit-icon="$globals.icons.save"
      :submit-text="$tc('general.save')"
      @submit="editSaveUnit"
    >
      <v-card-text v-if="editTarget">
        <v-form ref="domEditUnitForm">
          <v-text-field
            v-model="editTarget.name"
            :label="$t('general.name')"
            :hint="$t('data-pages.units.example-unit-singular')"
            :rules="[validators.required]"
          ></v-text-field>
          <v-text-field
            v-model="editTarget.pluralName"
            :label="$t('general.plural-name')"
            :hint="$t('data-pages.units.example-unit-plural')"
          ></v-text-field>
          <v-text-field
            v-model="editTarget.abbreviation"
            :label="$t('data-pages.units.abbreviation')"
            :hint="$t('data-pages.units.example-unit-abbreviation-singular')"
          ></v-text-field>
          <v-text-field
            v-model="editTarget.pluralAbbreviation"
            :label="$t('data-pages.units.plural-abbreviation')"
            :hint="$t('data-pages.units.example-unit-abbreviation-plural')"
          ></v-text-field>
          <v-text-field v-model="editTarget.description" :label="$t('data-pages.units.description')"></v-text-field>
          <v-checkbox v-model="editTarget.fraction" hide-details :label="$t('data-pages.units.display-as-fraction')"></v-checkbox>
          <v-checkbox v-model="editTarget.useAbbreviation" hide-details :label="$t('data-pages.units.use-abbreviation')"></v-checkbox>
        </v-form>
      </v-card-text>
      <template #custom-card-action>
        <BaseButton edit @click="aliasManagerEventHandler">{{ $t('data-pages.manage-aliases') }}</BaseButton>
      </template>
    </BaseDialog>

    <!-- Delete Dialog -->
    <BaseDialog
      v-model="deleteDialog"
      :title="$tc('general.confirm')"
      :icon="$globals.icons.alertCircle"
      color="error"
      @confirm="deleteUnit"
    >
      <v-card-text>
        {{ $t("general.confirm-delete-generic") }}
        <p v-if="deleteTarget" class="mt-4 ml-4">{{ deleteTarget.name }}</p>
      </v-card-text>
    </BaseDialog>

    <!-- Bulk Delete Dialog -->
    <BaseDialog
      v-model="bulkDeleteDialog"
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
          {{ $t("data-pages.units.seed-dialog-text") }}
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

        <v-alert v-if="store && store.length > 0" type="error" class="mb-0 text-body-2">
          {{ $t("data-pages.foods.seed-dialog-warning") }}
        </v-alert>
      </v-card-text>
    </BaseDialog>

    <!-- Data Table -->
    <BaseCardSectionTitle :icon="$globals.icons.units" section :title="$tc('data-pages.units.unit-data')"> </BaseCardSectionTitle>
    <CrudTable
      :table-config="tableConfig"
      :headers.sync="tableHeaders"
      :data="store"
      :bulk-actions="[{icon: $globals.icons.delete, text: $tc('general.delete'), event: 'delete-selected'}]"
      initial-sort="createdAt"
      initial-sort-desc
      @delete-one="deleteEventHandler"
      @edit-one="editEventHandler"
      @create-one="createEventHandler"
      @delete-selected="bulkDeleteEventHandler"
    >
      <template #button-row>
        <BaseButton create @click="createDialog = true" />

        <BaseButton @click="mergeDialog = true">
          <template #icon> {{ $globals.icons.externalLink }} </template>
          {{ $t('data-pages.combine') }}
        </BaseButton>
      </template>
      <template #item.useAbbreviation="{ item }">
        <v-icon :color="item.useAbbreviation ? 'success' : undefined">
          {{ item.useAbbreviation ? $globals.icons.check : $globals.icons.close }}
        </v-icon>
      </template>
      <template #item.fraction="{ item }">
        <v-icon :color="item.fraction ? 'success' : undefined">
          {{ item.fraction ? $globals.icons.check : $globals.icons.close }}
        </v-icon>
      </template>
      <template #item.createdAt="{ item }">
        {{ formatDate(item.createdAt) }}
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
import { computed, defineComponent, onMounted, ref, useContext } from "@nuxtjs/composition-api";
import type { LocaleObject } from "@nuxtjs/i18n";
import RecipeDataAliasManagerDialog from "~/components/Domain/Recipe/RecipeDataAliasManagerDialog.vue";
import { validators } from "~/composables/use-validators";
import { useUserApi } from "~/composables/api";
import { CreateIngredientUnit, IngredientUnit, IngredientUnitAlias } from "~/lib/api/types/recipe";
import { useLocales } from "~/composables/use-locales";
import { useUnitStore } from "~/composables/store";
import { VForm } from "~/types/vuetify";

export default defineComponent({
  components: { RecipeDataAliasManagerDialog },
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
      {
        text: i18n.t("general.plural-name"),
        value: "pluralName",
        show: true,
      },
      {
        text: i18n.t("data-pages.units.abbreviation"),
        value: "abbreviation",
        show: true,
      },
      {
        text: i18n.t("data-pages.units.plural-abbreviation"),
        value: "pluralAbbreviation",
        show: true,
      },
      {
        text: i18n.t("data-pages.units.use-abbv"),
        value: "useAbbreviation",
        show: true,
      },
      {
        text: i18n.t("data-pages.units.description"),
        value: "description",
        show: false,
      },
      {
        text: i18n.t("data-pages.units.fraction"),
        value: "fraction",
        show: true,
      },
      {
        text: i18n.tc("general.date-added"),
        value: "createdAt",
        show: false,
      },
    ];

    function formatDate(date: string) {
      try {
        return i18n.d(Date.parse(date), "medium");
      } catch {
        return "";
      }
    }

    const { store, actions: unitActions } = useUnitStore();

    // ============================================================
    // Create Units

    const createDialog = ref(false);
    const domNewUnitForm = ref<VForm>();

    // we explicitly set booleans to false since forms don't POST unchecked boxes
    const createTarget = ref<CreateIngredientUnit>({
      name: "",
      fraction: true,
      useAbbreviation: false,
    });

    function createEventHandler() {
      createDialog.value = true;
    }

    async function createUnit() {
      if (!createTarget.value || !createTarget.value.name) {
        return;
      }

      // @ts-expect-error the createOne function erroneously expects an id because it uses the IngredientUnit type
      await unitActions.createOne(createTarget.value);
      createDialog.value = false;

      domNewUnitForm.value?.reset();
      createTarget.value = {
        name: "",
        fraction: false,
        useAbbreviation: false,
      };
    }

    // ============================================================
    // Edit Units
    const editDialog = ref(false);
    const editTarget = ref<IngredientUnit | null>(null);
    function editEventHandler(item: IngredientUnit) {
      editTarget.value = item;
      editDialog.value = true;
    }

    async function editSaveUnit() {
      if (!editTarget.value) {
        return;
      }

      await unitActions.updateOne(editTarget.value);
      editDialog.value = false;
    }

    // ============================================================
    // Delete Units
    const deleteDialog = ref(false);
    const deleteTarget = ref<IngredientUnit | null>(null);
    function deleteEventHandler(item: IngredientUnit) {
      deleteTarget.value = item;
      deleteDialog.value = true;
    }

    async function deleteUnit() {
      if (!deleteTarget.value) {
        return;
      }
      await unitActions.deleteOne(deleteTarget.value.id);
      deleteDialog.value = false;
    }

    // ============================================================
    // Bulk Delete Units
    const bulkDeleteDialog = ref(false);
    const bulkDeleteTarget = ref<IngredientUnit[]>([]);
    function bulkDeleteEventHandler(selection: IngredientUnit[]) {
      bulkDeleteTarget.value = selection;
      bulkDeleteDialog.value = true;
    }

    async function deleteSelected() {
      for (const item of bulkDeleteTarget.value) {
        await unitActions.deleteOne(item.id);
      }
      bulkDeleteTarget.value = [];
    }

    // ============================================================
    // Alias Manager

    const aliasManagerDialog = ref(false);
    function aliasManagerEventHandler() {
      aliasManagerDialog.value = true;
    }

    function updateUnitAlias(newAliases: IngredientUnitAlias[]) {
      if (!editTarget.value) {
        return;
      }
      editTarget.value.aliases = newAliases;
      aliasManagerDialog.value = false;
    }

    // ============================================================
    // Merge Units

    const mergeDialog = ref(false);
    const fromUnit = ref<IngredientUnit | null>(null);
    const toUnit = ref<IngredientUnit | null>(null);

    const canMerge = computed(() => {
      return fromUnit.value && toUnit.value && fromUnit.value.id !== toUnit.value.id;
    });

    async function mergeUnits() {
      if (!canMerge.value || !fromUnit.value || !toUnit.value) {
        return;
      }

      const { data } = await userApi.units.merge(fromUnit.value.id, toUnit.value.id);

      if (data) {
        unitActions.refresh();
      }
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
      const { data } = await userApi.seeders.units({ locale: locale.value });

      if (data) {
        unitActions.refresh();
      }
    }

    return {
      tableConfig,
      tableHeaders,
      store,
      validators,
      formatDate,
      // Create
      createDialog,
      domNewUnitForm,
      createEventHandler,
      createUnit,
      createTarget,
      // Edit
      editDialog,
      editEventHandler,
      editSaveUnit,
      editTarget,
      // Delete
      deleteEventHandler,
      deleteDialog,
      deleteUnit,
      deleteTarget,
      // Bulk Delete
      bulkDeleteDialog,
      bulkDeleteEventHandler,
      bulkDeleteTarget,
      deleteSelected,
      // Alias Manager
      aliasManagerDialog,
      aliasManagerEventHandler,
      updateUnitAlias,
      // Merge
      canMerge,
      mergeUnits,
      mergeDialog,
      fromUnit,
      toUnit,
      // Seed
      seedDatabase,
      locales,
      locale,
      seedDialog,
    };
  },
});
</script>
