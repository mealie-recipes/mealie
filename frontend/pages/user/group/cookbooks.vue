<template>
  <v-container class="narrow-container">
    <BasePageTitle divider>
      <template #header>
        <v-img max-height="100" max-width="100" :src="require('~/static/svgs/manage-cookbooks.svg')"></v-img>
      </template>
      <template #title> Cookbooks </template>
      Arrange and edit your cookbooks here.
    </BasePageTitle>

    <BaseButton create @click="actions.createOne()" />
    <v-expansion-panels class="mt-2">
      <draggable v-model="cookbooks" handle=".handle" style="width: 100%" @change="actions.updateOrder()">
        <v-expansion-panel v-for="(cookbook, index) in cookbooks" :key="index" class="my-2 my-border rounded">
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
              <v-btn color="info" fab small class="ml-2">
                <v-icon color="white">
                  {{ $globals.icons.edit }}
                </v-icon>
              </v-btn>
            </template>
          </v-expansion-panel-header>
          <v-expansion-panel-content>
            <v-card-text>
              <v-text-field v-model="cookbooks[index].name" label="Cookbook Name"></v-text-field>
              <v-textarea v-model="cookbooks[index].description" auto-grow :rows="2" label="Description"></v-textarea>
              <DomainRecipeCategoryTagSelector v-model="cookbooks[index].categories" />
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <BaseButton delete @click="actions.deleteOne(cookbook.id)" />
              <BaseButton save @click="actions.updateOne(cookbook)"> </BaseButton>
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

export default defineComponent({
  components: { draggable },
  setup() {
    const { cookbooks, actions } = useCookbooks();

    return {
      cookbooks,
      actions,
    };
  },
});
</script>
    
<style>
.my-border {
  border-left: 5px solid var(--v-primary-base) !important;
}
</style>