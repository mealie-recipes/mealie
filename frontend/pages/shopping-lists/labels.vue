<template>
  <v-container class="narrow-container">
    <BaseDialog v-model="createDialog" title="New Label" :icon="$globals.icons.tags" @submit="createLabel">
      <v-card-text>
        <v-text-field v-model="createLabelData.name" :label="$t('general.name')"> </v-text-field>
      </v-card-text>
    </BaseDialog>

    <BaseDialog
      v-model="deleteDialog"
      :title="$t('general.confirm')"
      :icon="$globals.icons.alert"
      color="error"
      @confirm="confirmDelete"
    >
      <v-card-text>
        {{ $t("general.confirm-delete-generic") }}
      </v-card-text>
    </BaseDialog>

    <BasePageTitle divider>
      <template #header>
        <v-img max-height="100" max-width="100" :src="require('~/static/svgs/shopping-cart.svg')"></v-img>
      </template>
      <template #title> Shopping Lists Labels </template>
    </BasePageTitle>
    <BaseButton create @click="createDialog = true" />

    <section v-if="labels" class="mt-4">
      <v-text-field v-model="searchInput" :label="$t('sidebar.search')" clearable>
        <template #prepend>
          <v-icon>{{ $globals.icons.search }}</v-icon>
        </template>
      </v-text-field>

      <v-sheet v-for="(label, index) in results" :key="label.id">
        <div class="d-flex px-2 py-2 pt-3">
          <v-chip label :color="labels[index].color || undefined">
            {{ label.name }}
          </v-chip>
          <div class="ml-auto">
            <v-btn v-if="!isOpen[label.id]" class="mx-1" icon @click.prevent="deleteLabel(label.id)">
              <v-icon>
                {{ $globals.icons.delete }}
              </v-icon>
            </v-btn>
            <v-btn v-if="!isOpen[label.id]" class="mx-1" icon @click="toggleIsOpen(label.id)">
              <v-icon>
                {{ $globals.icons.edit }}
              </v-icon>
            </v-btn>
          </div>
        </div>
        <v-card-text v-if="isOpen[label.id]">
          <div class="d-md-flex" style="gap: 30px">
            <v-text-field v-model="labels[index].name" :label="$t('general.name')"> </v-text-field>
            <div style="max-width: 300px">
              <v-text-field v-model="labels[index].color" label="Color">
                <template #prepend>
                  <v-btn
                    class="elevation-0"
                    small
                    height="30px"
                    width="30px"
                    :color="labels[index].color || 'grey'"
                    @click="setRandomHex(index)"
                  >
                    <v-icon color="white">
                      {{ $globals.icons.refreshCircle }}
                    </v-icon>
                  </v-btn>
                </template>
              </v-text-field>
            </div>
          </div>
          <div class="d-flex justify-end">
            <BaseButtonGroup
              :buttons="[
                {
                  icon: $globals.icons.delete,
                  text: 'Delete',
                  event: 'delete',
                },
                {
                  icon: $globals.icons.close,
                  text: 'Cancel',
                  event: 'cancel',
                },
                {
                  icon: $globals.icons.save,
                  text: 'Save',
                  event: 'save',
                },
              ]"
              @cancel="toggleIsOpen(label.id)"
              @save="updateLabel(label)"
              @delete="deleteLabel(label.id)"
            />
          </div>
        </v-card-text>
        <v-divider></v-divider>
      </v-sheet>
    </section>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, ref, useAsync, computed } from "@nuxtjs/composition-api";
import Fuse from "fuse.js";
import { useUserApi } from "~/composables/api";
import { useAsyncKey } from "~/composables/use-utils";
import { MultiPurposeLabelOut } from "~/types/api-types/labels";
export default defineComponent({
  setup() {
    // ==========================================================
    // API Operations

    const api = useUserApi();

    const deleteDialog = ref(false);
    const deleteTargetId = ref("");

    async function confirmDelete() {
      await api.multiPurposeLabels.deleteOne(deleteTargetId.value);
      refreshLabels();
      deleteTargetId.value = "";
    }

    function deleteLabel(itemId: string) {
      deleteTargetId.value = itemId;
      deleteDialog.value = true;
    }

    const createDialog = ref(false);

    const createLabelData = ref({
      name: "",
      color: "",
    });

    async function createLabel() {
      createLabelData.value.color = getRandomHex();
      const { data } = await api.multiPurposeLabels.createOne(createLabelData.value);
      if (data) {
        refreshLabels();
      }
    }

    async function updateLabel(label: MultiPurposeLabelOut) {
      const { data } = await api.multiPurposeLabels.updateOne(label.id, label);
      if (data) {
        refreshLabels();
        toggleIsOpen(label.id);
      }
    }

    const labels = useAsync(async () => {
      const { data } = await api.multiPurposeLabels.getAll();
      return data;
    }, useAsyncKey());

    async function refreshLabels() {
      const { data } = await api.multiPurposeLabels.getAll();
      labels.value = data ?? [];
    }

    // ==========================================================
    // Component Helpers

    const isOpen = ref<{ [key: string]: boolean }>({});

    function toggleIsOpen(id: string) {
      isOpen.value[id] = !isOpen.value[id];
      isOpen.value = { ...isOpen.value };
    }

    // ==========================================================
    // Color Generators

    function getRandomHex() {
      const letters = "BCDEF".split("");
      let color = "#";
      for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * letters.length)];
      }

      return color;
    }

    function setRandomHex(labelIndex: number) {
      if (!labels.value) {
        return;
      }
      labels.value[labelIndex].color = getRandomHex();
      labels.value = [...labels.value];
    }

    // ==========================================================
    // Search / Filter

    const searchInput = ref("");

    const labelNames = computed(() => {
      return labels.value?.map((label) => label.name) ?? [];
    });

    const fuseOpts = {
      shouldSort: true,
      threshold: 0.5,
      location: 0,
      distance: 100,
      findAllMatches: true,
      maxPatternLength: 32,
      minMatchCharLength: 2,
      keys: ["name"],
    };

    const fuse = computed(() => {
      return new Fuse(labelNames.value, fuseOpts);
    });

    const results = computed(() => {
      if (!searchInput.value) {
        return labels.value;
      }

      const foundName = fuse.value.search(searchInput.value).map((result) => result.item);

      return labels.value?.filter((label) => foundName.includes(label.name)) ?? [];
    });

    return {
      deleteDialog,
      deleteTargetId,
      confirmDelete,
      createLabelData,
      createLabel,
      createDialog,
      results,
      searchInput,
      updateLabel,
      deleteLabel,
      setRandomHex,
      toggleIsOpen,
      isOpen,
      labels,
      refreshLabels,
    };
  },
  head: {
    title: "Shopping List Labels",
  },
});
</script>


