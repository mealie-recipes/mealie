<template>
  <v-container>
    <BasePageTitle divider>
      <template #header>
        <v-img
          max-height="200"
          max-width="200"
          class="mb-2"
          :src="require('~/static/svgs/manage-data-migrations.svg')"
        ></v-img>
      </template>
      <template #title> Recipe Data Migrations</template>
      Recipes can be migrated from another supported application to Mealie. This is a great way to get started with
      Mealie.
    </BasePageTitle>
    <v-container>
      <BaseCardSectionTitle title="New Migration"> </BaseCardSectionTitle>
      <v-card outlined :loading="loading">
        <v-card-title> Choose Migration Type </v-card-title>
        <v-card-text v-if="content" class="pb-0">
          <div class="mb-2">
            <BaseOverflowButton v-model="migrationType" mode="model" :items="items" />
          </div>
          {{ content.text }}
          <v-treeview v-if="content.tree" dense :items="content.tree">
            <template #prepend="{ item }">
              <v-icon> {{ item.icon }}</v-icon>
            </template>
          </v-treeview>
        </v-card-text>

        <v-card-title class="mt-0"> Upload File </v-card-title>
        <v-card-text>
          <AppButtonUpload
            accept=".zip"
            class="mb-2"
            :post="false"
            file-name="file"
            :text-btn="false"
            @uploaded="setFileObject"
          />
          {{ fileObject.name || "No file selected" }}
        </v-card-text>

        <v-card-actions class="justify-end">
          <BaseButton :disabled="!fileObject.name" submit @click="startMigration">
            {{ $t("general.submit") }}</BaseButton
          >
        </v-card-actions>
      </v-card>
    </v-container>
    <v-container>
      <BaseCardSectionTitle title="Previous Migrations"> </BaseCardSectionTitle>
      <ReportTable :items="reports" @delete="deleteReport" />
    </v-container>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, useContext, computed, onMounted } from "@nuxtjs/composition-api";
import { SupportedMigration } from "~/api/class-interfaces/group-migrations";
import { ReportSummary } from "~/api/class-interfaces/group-reports";
import { useUserApi } from "~/composables/api";

const MIGRATIONS = {
  nextcloud: "nextcloud",
  chowdown: "chowdown",
  paprika: "paprika",
};

export default defineComponent({
  setup() {
    // @ts-ignore
    const { $globals } = useContext();

    const api = useUserApi();

    const state = reactive({
      loading: false,
      treeState: true,
      migrationType: MIGRATIONS.nextcloud as SupportedMigration,
      fileObject: {} as File,
      reports: [] as ReportSummary[],
    });

    const items = [
      {
        text: "Nextcloud",
        value: MIGRATIONS.nextcloud,
      },
      {
        text: "Chowdown",
        value: MIGRATIONS.chowdown,
      },
      {
        text: "Paprika",
        value: MIGRATIONS.paprika,
      },
    ];

    const _content = {
      [MIGRATIONS.nextcloud]: {
        text: "Nextcloud recipes can be imported from a zip file that contains the data stored in Nextcloud. See the example folder structure below to ensure your recipes are able to be imported.",
        tree: [
          {
            id: 1,
            icon: $globals.icons.zip,
            name: "nextcloud.zip",
            children: [
              {
                id: 2,
                name: "Recipe 1",
                icon: $globals.icons.folderOutline,
                children: [
                  { id: 3, name: "recipe.json", icon: $globals.icons.codeJson },
                  { id: 4, name: "full.jpg", icon: $globals.icons.fileImage },
                  { id: 5, name: "thumb.jpg", icon: $globals.icons.fileImage },
                ],
              },
              {
                id: 6,
                name: "Recipe 2",
                icon: $globals.icons.folderOutline,
                children: [
                  { id: 7, name: "recipe.json", icon: $globals.icons.codeJson },
                  { id: 8, name: "full.jpg", icon: $globals.icons.fileImage },
                  { id: 9, name: "thumb.jpg", icon: $globals.icons.fileImage },
                ],
              },
            ],
          },
        ],
      },
      [MIGRATIONS.chowdown]: {
        text: "Mealie natively supports the chowdown repository format. Download the code repository as a .zip file and upload it below",
        tree: false,
      },
      [MIGRATIONS.paprika]: {
        text: "Mealie can import recipes from the Paprika application. Export your recipes from paprika and upload the `.paprikaexprot` file below",
        tree: false,
      },
    };

    function setFileObject(fileObject: File) {
      state.fileObject = fileObject;
    }

    async function startMigration() {
      state.loading = true;
      const payload = {
        migrationType: state.migrationType,
        archive: state.fileObject,
      };

      const { data } = await api.groupMigration.startMigration(payload);

      state.loading = false;

      if (data) {
        state.reports.unshift(data);
      }
    }

    async function getMigrationReports() {
      const { data } = await api.groupReports.getAll("migration");

      if (data) {
        state.reports = data;
      }
    }

    async function deleteReport(id: string) {
      await api.groupReports.deleteOne(id);
      getMigrationReports();
    }

    onMounted(() => {
      getMigrationReports();
    });

    const content = computed(() => {
      const data = _content[state.migrationType];

      if (data) {
        return data;
      } else {
        return {
          text: "",
          tree: false,
        };
      }
    });

    return {
      ...toRefs(state),
      items,
      content,
      setFileObject,
      deleteReport,
      startMigration,
      getMigrationReports,
    };
  },
});
</script>

<style lang="scss" scoped>
</style>