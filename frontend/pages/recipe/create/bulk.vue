<template>
  <div>
    <v-card flat>
      <v-card-title class="headline"> Recipe Bulk Importer </v-card-title>
      <v-card-text>
        The Bulk recipe importer allows you to import multiple recipes at once by queing the sites on the backend and
        running the task in the background. This can be useful when initially migrating to Mealie, or when you want to
        import a large number of recipes.
      </v-card-text>
    </v-card>
    <section class="mt-2">
      <v-row v-for="(bulkUrl, idx) in bulkUrls" :key="'bulk-url' + idx" class="my-1" dense>
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
              <v-btn color="error" icon x-small @click="bulkUrls.splice(idx, 1)">
                <v-icon>
                  {{ $globals.icons.delete }}
                </v-icon>
              </v-btn>
            </template>
          </v-text-field>
        </v-col>
        <v-col cols="12" xs="12" sm="6">
          <RecipeOrganizerSelector
            v-model="bulkUrls[idx].categories"
            :items="allCategories || []"
            selector-type="category"
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
            :items="allTags || []"
            selector-type="tag"
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
      </v-row>
      <v-card-actions class="justify-end">
        <BaseButton
          delete
          @click="
            bulkUrls = [];
            lockBulkImport = false;
          "
        >
          Clear
        </BaseButton>
        <v-spacer></v-spacer>
        <BaseButton color="info" @click="bulkUrls.push({ url: '', categories: [], tags: [] })">
          <template #icon> {{ $globals.icons.createAlt }} </template> New
        </BaseButton>
        <BaseButton :disabled="bulkUrls.length === 0 || lockBulkImport" @click="bulkCreate">
          <template #icon> {{ $globals.icons.check }} </template> Submit
        </BaseButton>
      </v-card-actions>
    </section>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, ref } from "@nuxtjs/composition-api";
import { useUserApi } from "~/composables/api";
import { alert } from "~/composables/use-toast";
import RecipeOrganizerSelector from "~/components/Domain/Recipe/RecipeOrganizerSelector.vue";
import { useCategories, useTags } from "~/composables/recipes";

export default defineComponent({
  components: { RecipeOrganizerSelector },
  setup() {
    const state = reactive({
      error: false,
      loading: false,
    });

    const api = useUserApi();

    const bulkUrls = ref([{ url: "", categories: [], tags: [] }]);
    const lockBulkImport = ref(false);

    async function bulkCreate() {
      if (bulkUrls.value.length === 0) {
        return;
      }

      const { response } = await api.recipes.createManyByUrl({ imports: bulkUrls.value });

      if (response?.status === 202) {
        alert.success("Bulk Import process has started");
        lockBulkImport.value = true;
      } else {
        alert.error("Bulk import process has failed");
      }
    }

    const { allTags, useAsyncGetAll: getAllTags } = useTags();
    const { allCategories, useAsyncGetAll: getAllCategories } = useCategories();

    getAllTags();
    getAllCategories();

    return {
      allTags,
      allCategories,
      bulkCreate,
      bulkUrls,
      lockBulkImport,
      ...toRefs(state),
    };
  },
});
</script>
