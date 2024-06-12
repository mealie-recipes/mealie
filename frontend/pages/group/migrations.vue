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
      <template #title> {{ $t('migration.recipe-data-migrations') }}</template>
      {{ $t('migration.recipe-data-migrations-explanation') }}
    </BasePageTitle>
    <v-container>
      <BaseCardSectionTitle :title="$i18n.tc('migration.new-migration')"> </BaseCardSectionTitle>
      <v-card outlined :loading="loading">
        <v-card-title> {{ $t('migration.choose-migration-type') }} </v-card-title>
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

        <v-card-title class="mt-0"> {{ $t('general.upload-file') }} </v-card-title>
        <v-card-text>
          <AppButtonUpload
            :accept="content.acceptedFileType || '.zip'"
            class="mb-2"
            :post="false"
            file-name="file"
            :text-btn="false"
            @uploaded="setFileObject"
          />
          {{ fileObject.name || $i18n.tc('migration.no-file-selected') }}
        </v-card-text>

        <v-card-text>
          <v-checkbox v-model="addMigrationTag">
            <template #label>
          <i18n path="migration.tag-all-recipes">
            <template #tag-name>
              <b class="mx-1"> {{ migrationType }} </b>
            </template>
          </i18n>
            </template>
          </v-checkbox>
        </v-card-text>

        <v-card-actions class="justify-end">
          <BaseButton :disabled="!fileObject.name" submit @click="startMigration">
            {{ $t("general.submit") }}</BaseButton
          >
        </v-card-actions>
      </v-card>
    </v-container>
    <v-container>
      <BaseCardSectionTitle :title="$i18n.tc('migration.previous-migrations')"> </BaseCardSectionTitle>
      <ReportTable :items="reports" @delete="deleteReport" />
    </v-container>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, useContext, computed, onMounted } from "@nuxtjs/composition-api";
import { ReportSummary } from "~/lib/api/types/reports";
import { MenuItem } from "~/components/global/BaseOverflowButton.vue";
import { useUserApi } from "~/composables/api";
import { SupportedMigrations } from "~/lib/api/types/group";

const MIGRATIONS = {
  mealie: "mealie_alpha",
  chowdown: "chowdown",
  copymethat: "copymethat",
  myrecipebox: "myrecipebox",
  nextcloud: "nextcloud",
  paprika: "paprika",
  plantoeat: "plantoeat",
  recipekeeper: "recipekeeper",
  tandoor: "tandoor",
};

export default defineComponent({
  middleware: ["auth", "advanced-only"],
  setup() {
    const { $globals, i18n } = useContext();

    const api = useUserApi();

    const state = reactive({
      addMigrationTag: false,
      loading: false,
      treeState: true,
      migrationType: MIGRATIONS.mealie as SupportedMigrations,
      fileObject: {} as File,
      reports: [] as ReportSummary[],
    });

    const items: MenuItem[] = [
      {
        text: i18n.tc("migration.mealie-pre-v1.title"),
        value: MIGRATIONS.mealie,
        divider: true,
      },
      {
        text: i18n.tc("migration.chowdown.title"),
        value: MIGRATIONS.chowdown,
      },
      {
        text: i18n.tc("migration.copymethat.title"),
        value: MIGRATIONS.copymethat,
      },
      {
        text: i18n.tc("migration.myrecipebox.title"),
        value: MIGRATIONS.myrecipebox,
      },
      {
        text: i18n.tc("migration.nextcloud.title"),
        value: MIGRATIONS.nextcloud,
      },
      {
        text: i18n.tc("migration.paprika.title"),
        value: MIGRATIONS.paprika,
      },
      {
        text: i18n.tc("migration.plantoeat.title"),
        value: MIGRATIONS.plantoeat,
      },
      {
        text: i18n.tc("migration.recipekeeper.title"),
        value: MIGRATIONS.recipekeeper,
      },
      {
        text: i18n.tc("migration.tandoor.title"),
        value: MIGRATIONS.tandoor,
      },
    ];
    const _content = {
      [MIGRATIONS.mealie]: {
        text: i18n.tc("migration.mealie-pre-v1.description-long"),
        acceptedFileType: ".zip",
        tree: [
          {
            id: 1,
            icon: $globals.icons.zip,
            name: "mealie.zip",
            children: [
              {
                id: 2,
                name: "recipes",
                icon: $globals.icons.folderOutline,
                children: [
                  {
                    id: 3,
                    name: "recipe-name",
                    icon: $globals.icons.folderOutline,
                    children: [
                      { id: 4, name: "recipe-name.json", icon: $globals.icons.codeJson },
                      {
                        id: 5,
                        name: "images",
                        icon: $globals.icons.folderOutline,
                        children: [
                          { id: 6, name: "original.webp", icon: $globals.icons.codeJson },
                          { id: 7, name: "full.jpg", icon: $globals.icons.fileImage },
                          { id: 8, name: "thumb.jpg", icon: $globals.icons.fileImage },
                        ],
                      },
                    ],
                  },
                  {
                    id: 9,
                    name: "recipe-name-1",
                    icon: $globals.icons.folderOutline,
                    children: [
                      { id: 10, name: "recipe-name-1.json", icon: $globals.icons.codeJson },
                      {
                        id: 11,
                        name: "images",
                        icon: $globals.icons.folderOutline,
                        children: [
                          { id: 12, name: "original.webp", icon: $globals.icons.codeJson },
                          { id: 13, name: "full.jpg", icon: $globals.icons.fileImage },
                          { id: 14, name: "thumb.jpg", icon: $globals.icons.fileImage },
                        ],
                      },
                    ],
                  },
                ],
              },
            ],
          },
        ],
      },
      [MIGRATIONS.chowdown]: {
        text: i18n.tc("migration.chowdown.description-long"),
        acceptedFileType: ".zip",
        tree: [
          {
            id: 1,
            icon: $globals.icons.zip,
            name: "nextcloud.zip",
            children: [
              {
                id: 2,
                name: i18n.t("migration.recipe-1"),
                icon: $globals.icons.folderOutline,
                children: [
                  { id: 3, name: "recipe.json", icon: $globals.icons.codeJson },
                  { id: 4, name: "full.jpg", icon: $globals.icons.fileImage },
                  { id: 5, name: "thumb.jpg", icon: $globals.icons.fileImage },
                ],
              },
              {
                id: 6,
                name: i18n.t("migration.recipe-2"),
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
      [MIGRATIONS.copymethat]: {
        text: i18n.tc("migration.copymethat.description-long"),
        acceptedFileType: ".zip",
        tree: [
          {
            id: 1,
            icon: $globals.icons.zip,
            name: "Copy_Me_That_20230306.zip",
            children: [
              {
                id: 2,
                name: "images",
                icon: $globals.icons.folderOutline,
                children: [
                  { id: 3, name: "recipe_1_an5zy.jpg", icon: $globals.icons.fileImage },
                  { id: 4, name: "recipe_2_82el8.jpg", icon: $globals.icons.fileImage },
                  { id: 5, name: "recipe_3_j75qg.jpg", icon: $globals.icons.fileImage },
                ],
              },
              { id: 6, name: "recipes.html", icon: $globals.icons.codeJson }
            ]
          }
        ],
      },
      [MIGRATIONS.myrecipebox]: {
        text: i18n.tc("migration.myrecipebox.description-long"),
        acceptedFileType: ".csv",
        tree: false,
      },
      [MIGRATIONS.nextcloud]: {
        text: i18n.tc("migration.nextcloud.description-long"),
        acceptedFileType: ".zip",
        tree: [
          {
            id: 1,
            icon: $globals.icons.zip,
            name: "nextcloud.zip",
            children: [
              {
                id: 2,
                name: i18n.t("migration.recipe-1"),
                icon: $globals.icons.folderOutline,
                children: [
                  { id: 3, name: "recipe.json", icon: $globals.icons.codeJson },
                  { id: 4, name: "full.jpg", icon: $globals.icons.fileImage },
                  { id: 5, name: "thumb.jpg", icon: $globals.icons.fileImage },
                ],
              },
              {
                id: 6,
                name: i18n.t("migration.recipe-2"),
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
      [MIGRATIONS.paprika]: {
        text: i18n.tc("migration.paprika.description-long"),
        acceptedFileType: ".zip",
        tree: false,
      },
      [MIGRATIONS.plantoeat]: {
        text: i18n.tc("migration.plantoeat.description-long"),
        acceptedFileType: ".zip",
        tree: [
          {
            id: 1,
            icon: $globals.icons.zip,
            name: "plantoeat-recipes-508318_10-13-2023.zip",
            children: [
                  { id: 9, name: "plantoeat-recipes-508318_10-13-2023.csv", icon: $globals.icons.codeJson },
            ],
          }
        ],
      },
      [MIGRATIONS.recipekeeper]: {
        text: i18n.tc("migration.recipekeeper.description-long"),
        acceptedFileType: ".zip",
        tree: [
          {
            id: 1,
            icon: $globals.icons.zip,
            name: "recipekeeperhtml.zip",
            children: [
                  { id: 2, name: "recipes.html", icon: $globals.icons.codeJson },
                  { id: 3, name: "images", icon: $globals.icons.folderOutline,
                    children: [
                    { id: 4, name: "image1.jpg", icon: $globals.icons.fileImage },
                    { id: 5, name: "image2.jpg", icon: $globals.icons.fileImage },
                    ]
                   },
            ],
          }
        ],
      },
      [MIGRATIONS.tandoor]: {
        text: i18n.tc("migration.tandoor.description-long"),
        acceptedFileType: ".zip",
        tree: [
          {
            id: 1,
            icon: $globals.icons.zip,
            name: "tandoor_default_export_full_2023-06-29.zip",
            children: [
              {
                id: 2,
                name: "1.zip",
                icon: $globals.icons.zip,
                children: [
                  { id: 3, name: "image.jpeg", icon: $globals.icons.fileImage },
                  { id: 4, name: "recipe.json", icon: $globals.icons.codeJson },
                ]
              },
              {
                id: 5,
                name: "2.zip",
                icon: $globals.icons.zip,
                children: [
                  { id: 6, name: "image.jpeg", icon: $globals.icons.fileImage },
                  { id: 7, name: "recipe.json", icon: $globals.icons.codeJson },
                ]
              },
              {
                id: 8,
                name: "3.zip",
                icon: $globals.icons.zip,
                children: [
                  { id: 9, name: "image.jpeg", icon: $globals.icons.fileImage },
                  { id: 10, name: "recipe.json", icon: $globals.icons.codeJson },
                ]
              }
            ]
          }
        ],
      },
    };

    function setFileObject(fileObject: File) {
      state.fileObject = fileObject;
    }

    async function startMigration() {
      state.loading = true;
      const payload = {
        addMigrationTag: state.addMigrationTag,
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
          acceptedFileType: ".zip",
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
  head() {
    return {
      title: this.$tc("settings.migrations"),
    };
  },
});
</script>

<style lang="scss" scoped></style>
