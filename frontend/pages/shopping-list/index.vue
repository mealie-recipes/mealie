<template>
  <v-container class="narrow-container">
    <BasePageTitle divider>
      <template #title>Shopping Lists</template>
      View and manage your shopping lists here
    </BasePageTitle>

    <BaseButton create @click="actions.createOne()" />
    <v-expansion-panels class="mt-2">
      <draggable v-model="shoppingLists" handle=".handle" style="width: 100%" @change="actions.updateOrder()">
        <v-expansion-panel v-for="(shoppingList, index) in shoppingLists" :key="index" class="my-2 my-border rounded">
          <v-expansion-panel-header disable-icon-rotate class="headline">
            <div class="d-flex align-center">
              <v-icon large left>
                {{ $globals.icons.pages }}
              </v-icon>
              {{ shoppingList.name }}
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
              <v-text-field v-model="shoppingList.name" label="Shopping List Name"></v-text-field>
              <v-textarea v-model="shoppingList.description" auto-grow :rows="2" label="Description"></v-textarea>
              <DomainRecipeCategoryTagSelector v-model="shoppingList.categories" />
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <BaseButton delete @click="actions.deleteOne(shoppingList.id)" />
              <BaseButton save @click="actions.updateOne(shoppingList)"> </BaseButton>
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
import { useShoppingLists } from "@/composables/use-shopping-lists";

export default defineComponent({
  components: { draggable },
  setup() {
    const { shoppingLists, actions } = useShoppingLists();

    return {
      shoppingLists,
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