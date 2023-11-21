<template>
  <div>
    <!-- Create Dialog -->
    <BaseDialog
      v-model="state.createDialog"
      :title="$t('data-pages.tags.new-tag')"
      :icon="$globals.icons.tags"
      @submit="createTag"
    >
      <v-card-text>
        <v-form ref="domNewTagForm">
          <v-text-field
            v-model="createTarget.name"
            autofocus
            :label="$t('general.name')"
            :rules="[validators.required]"
          ></v-text-field>
        </v-form>
      </v-card-text>

    </BaseDialog>

    <!-- Edit Dialog -->
    <BaseDialog
      v-model="state.editDialog"
      :icon="$globals.icons.tags"
      :title="$t('data-pages.tags.edit-tag')"
      :submit-text="$tc('general.save')"
      @submit="editSaveTag"
    >
      <v-card-text v-if="editTarget">
        <div class="mt-4">
          <v-text-field v-model="editTarget.name" :label="$t('general.name')"> </v-text-field>
        </div>
      </v-card-text>
    </BaseDialog>

    <!-- Delete Dialog -->
    <BaseDialog
      v-model="state.deleteDialog"
      :title="$tc('general.confirm')"
      :icon="$globals.icons.alertCircle"
      color="error"
      @confirm="deleteTag"
    >
      <v-card-text>
        {{ $t("general.confirm-delete-generic") }}
      </v-card-text>
    </BaseDialog>

    <!-- Recipe Data Table -->
    <BaseCardSectionTitle :icon="$globals.icons.tags" section :title="$tc('data-pages.tags.tag-data')"> </BaseCardSectionTitle>
    <CrudTable
      :table-config="tableConfig"
      :headers.sync="tableHeaders"
      :data="tags || []"
      :bulk-actions="[]"
      @delete-one="deleteEventHandler"
      @edit-one="editEventHandler"
    >
      <template #button-row>
        <BaseButton create @click="state.createDialog = true">{{ $t("general.create") }}</BaseButton>
      </template>
    </CrudTable>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, ref, useContext } from "@nuxtjs/composition-api";
import { validators } from "~/composables/use-validators";
import { useTagStore, useTagData } from "~/composables/store";
import { RecipeTag } from "~/lib/api/types/admin";

export default defineComponent({
  setup() {
    const { i18n } = useContext();
    const tableConfig = {
      hideColumns: true,
      canExport: true,
    };
    const tableHeaders = [
      {
        text: i18n.t("general.id"),
        value: "id",
        show: false,
      },
      {
        text: i18n.t("general.name"),
        value: "name",
        show: true,
      },
    ];

    const state = reactive({
      createDialog: false,
      editDialog: false,
      deleteDialog: false,
    });

    const tagData = useTagData();
    const tagStore = useTagStore();


    // ============================================================
    // Create Tag

    async function createTag() {
      // @ts-ignore - only property really required is the name (RecipeOrganizerPage)
      await tagStore.actions.createOne({ name: tagData.data.name });
      tagData.reset();
      state.createDialog = false;
    }


    // ============================================================
    // Edit Tag

    const editTarget = ref<RecipeTag | null>(null);

    function editEventHandler(item: RecipeTag) {
      state.editDialog = true;
      editTarget.value = item;
    }

    async function editSaveTag() {
      if (!editTarget.value) {
        return;
      }
      await tagStore.actions.updateOne(editTarget.value);
      state.editDialog = false;
    }


    // ============================================================
    // Delete Tag

    const deleteTarget = ref<RecipeTag | null>(null);

    function deleteEventHandler(item: RecipeTag) {
      state.deleteDialog = true;
      deleteTarget.value = item;
    }

    async function deleteTag() {
      if (!deleteTarget.value || deleteTarget.value.id === undefined) {
        return;
      }
      await tagStore.actions.deleteOne(deleteTarget.value.id);
      state.deleteDialog = false;
    }

    return {
      state,
      tableConfig,
      tableHeaders,
      tags: tagStore.items,
      validators,

      // create
      createTarget: tagData.data,
      createTag,

      // edit
      editTarget,
      editEventHandler,
      editSaveTag,

      // delete
      deleteTarget,
      deleteEventHandler,
      deleteTag
    };
  },
});
</script>
