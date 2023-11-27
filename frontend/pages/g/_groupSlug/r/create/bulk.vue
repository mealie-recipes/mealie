<template>
  <div>
    <div>
      <v-card-title class="headline"> {{ $t('recipe.recipe-bulk-importer') }} </v-card-title>
      <v-card-text>
        {{ $t('recipe.recipe-bulk-importer-description') }}
      </v-card-text>
    </div>
    <section class="mt-2">
      <v-row v-for="(_, idx) in bulkUrls" :key="'bulk-url' + idx" class="my-1" dense>
        <v-col cols="12" xs="12" sm="12" md="12">
          <v-text-field
            v-model="bulkUrls[idx].url"
            :label="$t('new-recipe.recipe-url')"
            dense
            single-line
            validate-on-blur
            autofocus
            filled
            hide-details
            clearable
            :prepend-inner-icon="$globals.icons.link"
            rounded
            class="rounded-lg"
          >
            <template #append>
              <v-btn style="margin-top: -2px" icon small @click="bulkUrls.splice(idx, 1)">
                <v-icon>
                  {{ $globals.icons.delete }}
                </v-icon>
              </v-btn>
            </template>
          </v-text-field>
        </v-col>
        <template v-if="showCatTags">
          <v-col cols="12" xs="12" sm="6">
            <RecipeOrganizerSelector
              v-model="bulkUrls[idx].categories"
              selector-type="categories"
              :input-attrs="{
                filled: true,
                singleLine: true,
                dense: true,
                rounded: true,
                class: 'rounded-lg',
                hideDetails: true,
                clearable: true,
              }"
            />
          </v-col>
          <v-col cols="12" xs="12" sm="6">
            <RecipeOrganizerSelector
              v-model="bulkUrls[idx].tags"
              selector-type="tags"
              :input-attrs="{
                filled: true,
                singleLine: true,
                dense: true,
                rounded: true,
                class: 'rounded-lg',
                hideDetails: true,
                clearable: true,
              }"
            />
          </v-col>
        </template>
      </v-row>
      <v-card-actions class="justify-end flex-wrap mb-1">
        <BaseButton
          delete
          @click="
            bulkUrls = [];
            lockBulkImport = false;
          "
        >
          {{ $t('general.clear') }}
        </BaseButton>
        <v-spacer></v-spacer>
        <BaseButton class="mr-1 mb-1" color="info" @click="bulkUrls.push({ url: '', categories: [], tags: [] })">
          <template #icon> {{ $globals.icons.createAlt }} </template>
          {{ $t('general.new') }}
        </BaseButton>
        <RecipeDialogBulkAdd v-model="bulkDialog" class="mr-1 mr-sm-0 mb-1" @bulk-data="assignUrls" />
      </v-card-actions>
      <div class="px-1">
        <v-checkbox v-model="showCatTags" hide-details :label="$t('recipe.set-categories-and-tags')" />
      </div>
      <v-card-actions class="justify-end">
        <BaseButton :disabled="bulkUrls.length === 0 || lockBulkImport" @click="bulkCreate">
          <template #icon> {{ $globals.icons.check }} </template>
          {{ $t('general.submit') }}
        </BaseButton>
      </v-card-actions>
    </section>
    <section class="mt-12">
      <BaseCardSectionTitle :title="$tc('recipe.bulk-imports')"> </BaseCardSectionTitle>
      <ReportTable :items="reports" @delete="deleteReport" />
    </section>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, ref, useContext } from "@nuxtjs/composition-api";
import { whenever } from "@vueuse/shared";
import { useUserApi } from "~/composables/api";
import { alert } from "~/composables/use-toast";
import RecipeOrganizerSelector from "~/components/Domain/Recipe/RecipeOrganizerSelector.vue";
import { ReportSummary } from "~/lib/api/types/reports";
import RecipeDialogBulkAdd from "~/components/Domain/Recipe/RecipeDialogBulkAdd.vue";

export default defineComponent({
  components: { RecipeOrganizerSelector, RecipeDialogBulkAdd },
  setup() {
    const state = reactive({
      error: false,
      loading: false,
      showCatTags: false,
      bulkDialog: false,
    });

    whenever(
      () => !state.showCatTags,
      () => {
        console.log("showCatTags changed");
      }
    );

    const api = useUserApi();
    const { i18n } = useContext();

    const bulkUrls = ref([{ url: "", categories: [], tags: [] }]);
    const lockBulkImport = ref(false);

    async function bulkCreate() {
      if (bulkUrls.value.length === 0) {
        return;
      }

      const { response } = await api.recipes.createManyByUrl({ imports: bulkUrls.value });

      if (response?.status === 202) {
        alert.success(i18n.tc("recipe.bulk-import-process-has-started"));
        lockBulkImport.value = true;
      } else {
        alert.error(i18n.tc("recipe.bulk-import-process-has-failed"));
      }

      fetchReports();
    }

    // =========================================================
    // Reports

    const reports = ref<ReportSummary[]>([]);

    async function fetchReports() {
      const { data } = await api.groupReports.getAll("bulk_import");
      reports.value = data ?? [];
    }

    async function deleteReport(id: string) {
      console.log(id);
      const { response } = await api.groupReports.deleteOne(id);

      if (response?.status === 200) {
        fetchReports();
      } else {
        alert.error(i18n.tc("recipe.report-deletion-failed"));
      }
    }

    fetchReports();

    function assignUrls(urls: string[]) {
      bulkUrls.value = urls.map((url) => ({ url, categories: [], tags: [] }));
    }

    return {
      assignUrls,
      reports,
      deleteReport,
      bulkCreate,
      bulkUrls,
      lockBulkImport,
      ...toRefs(state),
    };
  },
});
</script>
