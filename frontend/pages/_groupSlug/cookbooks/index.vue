<template>
  <v-container class="narrow-container">
    <BasePageTitle divider>
      <template #header>
        <v-img max-height="100" max-width="100" :src="require('~/static/svgs/manage-cookbooks.svg')"></v-img>
      </template>
      <template #title> {{ $t('cookbook.cookbooks') }} </template>
      {{ $t('cookbook.description') }}
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
              <v-text-field v-model="cookbooks[index].name" :label="$t('cookbook.cookbook-name')"></v-text-field>
              <v-textarea v-model="cookbooks[index].description" auto-grow :rows="2" :label="$t('recipe.description')"></v-textarea>
              <RecipeOrganizerSelector v-model="cookbooks[index].categories" selector-type="categories" />
              <RecipeOrganizerSelector v-model="cookbooks[index].tags" selector-type="tags" />
              <RecipeOrganizerSelector v-model="cookbooks[index].tools" selector-type="tools" />
              <v-switch v-model="cookbooks[index].public" hide-details single-line>
                <template #label>
                  {{ $t('cookbook.public-cookbook') }}
                  <HelpIcon small right class="ml-2">
                    {{ $t('cookbook.public-cookbook-description') }}
                  </HelpIcon>
                </template>
              </v-switch>
              <div class="mt-4">
                <h3 class="text-subtitle-1 d-flex align-center mb-0 pb-0">
                  {{ $t('cookbook.filter-options') }}
                  <HelpIcon right small class="ml-2">
                    {{ $t('cookbook.filter-options-description') }}
                  </HelpIcon>
                </h3>
                <v-switch v-model="cookbooks[index].requireAllCategories" class="mt-0" hide-details single-line>
                  <template #label> {{ $t('cookbook.require-all-categories') }} </template>
                </v-switch>
                <v-switch v-model="cookbooks[index].requireAllTags" hide-details single-line>
                  <template #label> {{ $t('cookbook.require-all-tags') }} </template>
                </v-switch>
                <v-switch v-model="cookbooks[index].requireAllTools" hide-details single-line>
                  <template #label> {{ $t('cookbook.require-all-tools') }} </template>
                </v-switch>
              </div>
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

export default defineComponent({
  components: { draggable, RecipeOrganizerSelector },
  setup() {
    const { cookbooks, actions } = useCookbooks();

    return {
      cookbooks,
      actions,
    };
  },
  head() {
    return {
      title: this.$t("settings.pages") as string,
    };
  },
});
</script>
