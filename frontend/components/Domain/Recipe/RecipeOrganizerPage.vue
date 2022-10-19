<template>
  <div v-if="items">
    <RecipeOrganizerDialog v-model="dialog" :item-type="itemType" />

    <BaseDialog
      v-if="deleteTarget"
      v-model="deleteDialog"
      :title="$t('general.delete-with-name', { name: deleteTarget.name })"
      color="error"
      :icon="$globals.icons.alertCircle"
      @confirm="deleteOne()"
    >
      <v-card-text> {{ $t("general.confirm-delete-generic-with-name", { name: deleteTarget.name }) }} </v-card-text>
    </BaseDialog>
    <v-app-bar color="transparent" flat class="mt-n1 rounded align-center">
      <v-icon large left>
        {{ icon }}
      </v-icon>
      <v-toolbar-title class="headline">
        <slot name="title">
          {{ headline }}
        </slot>
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <BaseButton create @click="dialog = true" />
    </v-app-bar>
    <section v-for="(itms, key, idx) in itemsSorted" :key="'header' + idx" :class="idx === 1 ? null : 'my-4'">
      <BaseCardSectionTitle :title="key"> </BaseCardSectionTitle>
      <v-row>
        <v-col v-for="(item, index) in itms" :key="'cat' + index" cols="12" :sm="12" :md="6" :lg="4" :xl="3">
          <v-card class="left-border" hover :to="`/recipes/${itemType}/${item.slug}`">
            <v-card-actions>
              <v-icon>
                {{ icon }}
              </v-icon>
              <v-card-title class="py-1">
                {{ item.name }}
              </v-card-title>
              <v-spacer></v-spacer>
              <ContextMenu :items="[presets.delete]" @delete="confirmDelete(item)" />
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </section>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed, ref } from "@nuxtjs/composition-api";
import { useContextPresets } from "~/composables/use-context-presents";
import RecipeOrganizerDialog from "~/components/Domain/Recipe/RecipeOrganizerDialog.vue";
import { RecipeOrganizer } from "~/lib/api/types/non-generated";

interface GenericItem {
  id?: string;
  name: string;
  slug: string;
}

export default defineComponent({
  components: {
    RecipeOrganizerDialog,
  },
  props: {
    items: {
      type: Array as () => GenericItem[],
      required: true,
    },
    icon: {
      type: String,
      required: true,
    },
    itemType: {
      type: String as () => RecipeOrganizer,
      required: true,
    },
  },
  setup(props, { emit }) {
    // =================================================================
    // Sorted Items
    const itemsSorted = computed(() => {
      const byLetter: { [key: string]: Array<GenericItem> } = {};

      if (!props.items) return byLetter;

      props.items
        .sort((a, b) => a.name.localeCompare(b.name))
        .forEach((item) => {
          const letter = item.name[0].toUpperCase();
          if (!byLetter[letter]) {
            byLetter[letter] = [];
          }
          byLetter[letter].push(item);
        });

      return byLetter;
    });

    // =================================================================
    // Context Menu
    const presets = useContextPresets();

    const deleteTarget = ref<GenericItem | null>(null);
    const deleteDialog = ref(false);

    function confirmDelete(item: GenericItem) {
      deleteTarget.value = item;
      deleteDialog.value = true;
    }

    function deleteOne() {
      if (!deleteTarget.value) {
        return;
      }

      emit("delete", deleteTarget.value.id);
    }

    const dialog = ref(false);

    return {
      dialog,
      confirmDelete,
      deleteOne,
      deleteDialog,
      deleteTarget,
      presets,
      itemsSorted,
    };
  },
  // Needed for useMeta
  head: {},
});
</script>
