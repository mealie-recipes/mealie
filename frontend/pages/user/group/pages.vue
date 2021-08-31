<template>
  <v-container fluid>
    <BaseCardSectionTitle title="Cookbooks"> </BaseCardSectionTitle>
    <BaseButton create @click="actions.createOne()" />
    <v-expansion-panels class="mt-2">
      <draggable v-model="cookbooks" handle=".handle" style="width: 100%" @change="actions.updateOrder()">
        <v-expansion-panel v-for="(cookbook, index) in cookbooks" :key="index" class="my-2 my-border rounded">
          <v-expansion-panel-header disable-icon-rotate class="headline">
            {{ cookbook.name }}
            <template #actions>
              <v-btn color="info" fab small class="ml-auto mr-2">
                <v-icon color="white">
                  {{ $globals.icons.edit }}
                </v-icon>
              </v-btn>
              <v-icon class="handle">
                {{ $globals.icons.arrowUpDown }}
              </v-icon>
            </template>
          </v-expansion-panel-header>
          <v-expansion-panel-content>
            <v-card-text>
              <v-text-field v-model="cookbooks[index].name" label="Cookbook Name"></v-text-field>
              <DomainRecipeCategoryTagSelector v-model="cookbooks[index].categories" />
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <BaseButton delete @click="actions.deleteOne(cookbook.id)" />
              <BaseButton update @click="actions.updateOne(cookbook)"> </BaseButton>
            </v-card-actions>
          </v-expansion-panel-content>
        </v-expansion-panel>
      </draggable>
    </v-expansion-panels>
  </v-container>
</template>
    
<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";
import { useCookbooks } from "@/composables/use-cookbooks";
import draggable from "vuedraggable";

export default defineComponent({
  components: { draggable },
  layout: "admin",
  setup() {
    const { cookbooks, actions, workingCookbookData, deleteTargetId, validForm } = useCookbooks();

    return {
      cookbooks,
      actions,
      workingCookbookData,
      deleteTargetId,
      validForm,
    };
  },
});
</script>
    
<style scoped>
.my-border {
  border-left: 5px solid var(--v-primary-base);
}
</style>