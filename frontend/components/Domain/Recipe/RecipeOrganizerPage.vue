<template>
  <div v-if="items">
    <RecipeOrganizerDialog v-model="dialogs.organizer" :item-type="itemType" />

    <BaseDialog
      v-if="deleteTarget"
      v-model="dialogs.delete"
      :title="$t('general.delete-with-name', { name: $t(translationKey) })"
      color="error"
      :icon="$globals.icons.alertCircle"
      @confirm="deleteOne()"
    >
      <v-card-text>
<p>{{ $t("general.confirm-delete-generic-with-name", { name: $t(translationKey) }) }}</p>
        <p class="mt-4 mb-0 ml-4">{{ deleteTarget.name }}</p>
      </v-card-text>
    </BaseDialog>

    <BaseDialog v-if="updateTarget" v-model="dialogs.update" :title="$t('general.update')" @confirm="updateOne()">
      <v-card-text>
        <v-text-field v-model="updateTarget.name" :label="$t('general.name')"> </v-text-field>
        <v-checkbox v-if="itemType === Organizer.Tool" v-model="updateTarget.onHand" :label="$t('tool.on-hand')"></v-checkbox>
      </v-card-text>
    </BaseDialog>

    <v-row dense>
      <v-col>
        <v-text-field
          v-model="searchString"
          outlined
          autofocus
          color="primary accent-3"
          :placeholder="$t('search.search-placeholder')"
          :prepend-inner-icon="$globals.icons.search"
          clearable
        >
        </v-text-field>
      </v-col>
    </v-row>

    <v-app-bar color="transparent" flat class="mt-n1 rounded align-center">
      <v-icon large left>
        {{ icon }}
      </v-icon>
      <v-toolbar-title class="headline">
        <slot name="title"> </slot>
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <BaseButton create @click="dialogs.organizer = true" />
    </v-app-bar>
    <section v-for="(itms, key, idx) in itemsSorted" :key="'header' + idx" :class="idx === 1 ? null : 'my-4'">
      <BaseCardSectionTitle v-if="isTitle(key)" :title="key" />
      <v-row>
        <v-col v-for="(item, index) in itms" :key="'cat' + index" cols="12" :sm="12" :md="6" :lg="4" :xl="3">
          <v-card v-if="item" class="left-border" hover :to="`/g/${groupSlug}?${itemType}=${item.id}`">
            <v-card-actions>
              <v-icon>
                {{ icon }}
              </v-icon>
              <v-card-title class="py-1">
                {{ item.name }}
              </v-card-title>
              <v-spacer></v-spacer>
              <ContextMenu
                :items="[presets.delete, presets.edit]"
                @delete="confirmDelete(item)"
                @edit="openUpdateDialog(item)"
              />
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </section>
  </div>
</template>

<script lang="ts">
import Fuse from "fuse.js";
import { defineComponent, computed, ref, reactive, useContext, useRoute } from "@nuxtjs/composition-api";
import { useContextPresets } from "~/composables/use-context-presents";
import RecipeOrganizerDialog from "~/components/Domain/Recipe/RecipeOrganizerDialog.vue";
import { Organizer, RecipeOrganizer } from "~/lib/api/types/non-generated";
import { useRouteQuery } from "~/composables/use-router";
import { deepCopy } from "~/composables/use-utils";

interface GenericItem {
  id: string;
  name: string;
  slug: string;
  onHand: boolean;
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
    const state = reactive({
      // Search Options
      options: {
        ignoreLocation: true,
        shouldSort: true,
        threshold: 0.2,
        location: 0,
        distance: 20,
        findAllMatches: true,
        maxPatternLength: 32,
        minMatchCharLength: 1,
        keys: ["name"],
      },
    });

    const { $auth } = useContext();
    const route = useRoute();
    const groupSlug = computed(() => route.value.params.groupSlug || $auth.user?.groupSlug || "");

    // =================================================================
    // Context Menu

    const dialogs = ref({
      organizer: false,
      update: false,
      delete: false,
    });

    const presets = useContextPresets();

    const translationKey = computed<string>(() => {
      const typeMap = {
        "categories": "category.category",
        "tags": "tag.tag",
        "tools": "tool.tool",
        "foods": "shopping-list.food",
        "households": "household.household",
      };
      return typeMap[props.itemType] || "";
    });

    const deleteTarget = ref<GenericItem | null>(null);
    const updateTarget = ref<GenericItem | null>(null);

    function confirmDelete(item: GenericItem) {
      deleteTarget.value = item;
      dialogs.value.delete = true;
    }

    function deleteOne() {
      if (!deleteTarget.value) {
        return;
      }

      emit("delete", deleteTarget.value.id);
    }

    function openUpdateDialog(item: GenericItem) {
      updateTarget.value = deepCopy(item);
      dialogs.value.update = true;
    }

    function updateOne() {
      if (!updateTarget.value) {
        return;
      }

      emit("update", updateTarget.value);
    }

    // ================================================================
    // Search Functions

    const searchString = useRouteQuery("q", "");

    const fuse = computed(() => {
      return new Fuse(props.items, state.options);
    });

    const fuzzyItems = computed<GenericItem[]>(() => {
      if (searchString.value.trim() === "") {
        return props.items;
      }
      const result = fuse.value.search(searchString.value.trim() as string);
      return result.map((x) => x.item);
    });

    // =================================================================
    // Sorted Items

    const itemsSorted = computed(() => {
      const byLetter: { [key: string]: Array<GenericItem> } = {};

      if (!fuzzyItems.value) {
        return byLetter;
      }

      fuzzyItems.value
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

    function isTitle(str: number | string) {
      return typeof str === "string" && str.length === 1;
    }

    return {
      groupSlug,
      isTitle,
      dialogs,
      confirmDelete,
      openUpdateDialog,
      updateOne,
      updateTarget,
      deleteOne,
      deleteTarget,
      Organizer,
      presets,
      itemsSorted,
      searchString,
      translationKey,
    };
  },
  // Needed for useMeta
  head: {},
});
</script>
