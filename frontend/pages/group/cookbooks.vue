<template>
  <v-container class="narrow-container">
    <BasePageTitle divider>
      <template #header>
        <v-img max-height="100" max-width="100" :src="require('~/static/svgs/manage-cookbooks.svg')"></v-img>
      </template>
      <template #title> Cookbooks </template>
      Cookbooks are another way to organize recipes by creating cross sections of recipes and tags. Creating a cookbook
      will add an entry to the side-bar and all the recipes with the tags and categories chosen will be displayed in the
      cookbook.
    </BasePageTitle>

    <BaseButton create @click="actions.createOne()" />
    <v-expansion-panels class="mt-2">
      <draggable v-model="cookbooks" handle=".handle" style="width: 100%" @change="actions.updateOrder()">
        <v-expansion-panel v-for="(cookbook, index) in cookbooks" :key="index" class="my-2 left-border rounded">
          <v-expansion-panel-header disable-icon-rotate class="headline">
            <div class="d-flex align-center">
              <v-icon large left>
                {{ $globals.icons.pages }}
              </v-icon>
              {{ cookbook.name }}
            </div>
            <template #actions>
              <v-icon class="handle">
                {{ $globals.icons.arrowUpDown }}
              </v-icon>
              <v-btn icon small class="ml-2">
                <v-icon>
                  {{ $globals.icons.edit }}
                </v-icon>
              </v-btn>
            </template>
          </v-expansion-panel-header>
          <v-expansion-panel-content>
            <v-card-text v-if="cookbooks">
              <v-text-field v-model="cookbooks[index].name" label="Cookbook Name"></v-text-field>
              <v-textarea v-model="cookbooks[index].description" auto-grow :rows="2" label="Description"></v-textarea>
              <RecipeOrganizerSelector
                v-model="cookbooks[index].categories"
                :items="allCategories || []"
                selector-type="category"
              />
              <RecipeOrganizerSelector v-model="cookbooks[index].tags" :items="allTags || []" selector-type="tag" />
              <RecipeOrganizerSelector v-model="cookbooks[index].tools" :items="tools || []" selector-type="tool" />
              <v-switch v-model="cookbooks[index].public">
                <template #label>
                  Public Cookbook
                  <HelpIcon class="ml-4">
                    Public Cookbooks can be shared with non-mealie users and will be displayed on your groups page.
                  </HelpIcon>
                </template>
              </v-switch>
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <BaseButtonGroup
                :buttons="[
                  {
                    icon: $globals.icons.delete,
                    text: $tc('general.delete'),
                    event: 'delete',
                  },
                  {
                    icon: $globals.icons.save,
                    text: $tc('general.save'),
                    event: 'save',
                  },
                ]"
                @delete="actions.deleteOne(cookbook.id)"
                @save="actions.updateOne(cookbook)"
              />
            </v-card-actions>
          </v-expansion-panel-content>
        </v-expansion-panel>
      </draggable>
    </v-expansion-panels>
  </v-container>
</template>

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";
import draggable from "vuedraggable";
import { useCookbooks } from "@/composables/use-group-cookbooks";
import RecipeOrganizerSelector from "~/components/Domain/Recipe/RecipeOrganizerSelector.vue";
import { useCategories, useTags, useTools } from "~/composables/recipes";

export default defineComponent({
  components: { draggable, RecipeOrganizerSelector },
  setup() {
    const { cookbooks, actions } = useCookbooks();

    const { tools } = useTools();
    const { allCategories, useAsyncGetAll: getAllCategories } = useCategories();
    const { allTags, useAsyncGetAll: getAllTags } = useTags();

    getAllCategories();
    getAllTags();

    return {
      allCategories,
      allTags,
      cookbooks,
      actions,
      tools,
    };
  },
  head() {
    return {
      title: this.$t("settings.pages") as string,
    };
  },
});
</script>
