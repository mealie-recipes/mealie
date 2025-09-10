<template>
  <v-container>
    <BasePageTitle divider>
      <template #header>
        <v-img
          width="100%"
          max-height="200"
          max-width="200"
          class="mb-2"
          src="/svgs/manage-data-migrations.svg"
        />
      </template>
      <template #title>
        {{ $t('migration.recipe-data-migrations') }}
      </template>
      {{ $t('migration.recipe-data-migrations-explanation') }}
    </BasePageTitle>
    <v-container :class="$vuetify.display.smAndDown ? 'px-0': ''">
      <BaseCardSectionTitle :title="$t('migration.new-migration')" />
      <v-card
        variant="outlined"
        :loading="loading"
        style="border-color: lightgrey;"
      >
        <v-card-title> {{ $t('migration.choose-migration-type') }} </v-card-title>
        <v-card-text
          v-if="content"
          class="pb-0"
        >
          <div class="mb-2">
            <BaseOverflowButton
              v-model="migrationType"
              mode="model"
              :items="items"
            />
          </div>
          {{ content.text }}
          <v-treeview
            v-if="content.tree && Array.isArray(content.tree)"
            :key="migrationType"
            density="compact"
            :items="content.tree"
          >
            <template #prepend="{ item }">
              <v-icon> {{ item.icon }}</v-icon>
            </template>
          </v-treeview>
        </v-card-text>

        <v-card-title class="mt-0">
          {{ $t('general.upload-file') }}
        </v-card-title>
        <v-card-text>
          <AppButtonUpload
            :accept="content.acceptedFileType || '.zip'"
            class="mb-2"
            :post="false"
            file-name="file"
            :text-btn="false"
            @uploaded="setFileObject"
          />
          {{ fileObject.name || $t('migration.no-file-selected') }}
        </v-card-text>

        <v-card-text>
          <v-checkbox v-model="addMigrationTag">
            <template #label>
              <i18n-t keypath="migration.tag-all-recipes">
                <template #tag-name>
                  <b class="mx-1"> {{ migrationType }} </b>
                </template>
              </i18n-t>
            </template>
          </v-checkbox>
        </v-card-text>

        <v-card-actions class="justify-end">
          <BaseButton
            :disabled="!fileObject.name"
            submit
            @click="startMigration"
          >
            {{ $t("general.submit") }}
          </BaseButton>
        </v-card-actions>
      </v-card>
    </v-container>
    <v-container class="$vuetify.display.smAndDown ? 'px-0': ''">
      <BaseCardSectionTitle :title="$t('migration.previous-migrations')" />
      <ReportTable
        :items="reports"
        @delete="deleteReport"
      />
    </v-container>
  </v-container>
</template>

<script lang="ts">
import type { ReportSummary } from "~/lib/api/types/reports";
import type { MenuItem } from "~/components/global/BaseOverflowButton.vue";
import { useUserApi } from "~/composables/api";
import type { SupportedMigrations } from "~/lib/api/types/group";

interface TreeNode {
  id?: number;
  icon: string;
  title: string;
  children?: TreeNode[];
}

interface MigrationContent {
  text: string;
  acceptedFileType: string;
  tree: TreeNode[] | false;
}

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

export default defineNuxtComponent({
  middleware: ["sidebase-auth", "advanced-only"],
  setup() {
    const i18n = useI18n();
    const { $globals } = useNuxtApp();

    useSeoMeta({
      title: i18n.t("settings.migrations"),
    });

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
        text: i18n.t("migration.mealie-pre-v1.title"),
        value: MIGRATIONS.mealie,
        divider: true,
      },
      {
        text: i18n.t("migration.chowdown.title"),
        value: MIGRATIONS.chowdown,
      },
      {
        text: i18n.t("migration.copymethat.title"),
        value: MIGRATIONS.copymethat,
      },
      {
        text: i18n.t("migration.myrecipebox.title"),
        value: MIGRATIONS.myrecipebox,
      },
      {
        text: i18n.t("migration.nextcloud.title"),
        value: MIGRATIONS.nextcloud,
      },
      {
        text: i18n.t("migration.paprika.title"),
        value: MIGRATIONS.paprika,
      },
      {
        text: i18n.t("migration.plantoeat.title"),
        value: MIGRATIONS.plantoeat,
      },
      {
        text: i18n.t("migration.recipekeeper.title"),
        value: MIGRATIONS.recipekeeper,
      },
      {
        text: i18n.t("migration.tandoor.title"),
        value: MIGRATIONS.tandoor,
      },
    ];
    const _content: Record<string, MigrationContent> = {
      [MIGRATIONS.mealie]: {
        text: i18n.t("migration.mealie-pre-v1.description-long"),
        acceptedFileType: ".zip",
        tree: [
          {
            icon: $globals.icons.zip,
            title: "mealie.zip",
            children: [
              {
                title: "recipes",
                icon: $globals.icons.folderOutline,
                children: [
                  {
                    title: "recipe-name",
                    icon: $globals.icons.folderOutline,
                    children: [
                      { title: "recipe-name.json", icon: $globals.icons.codeJson },
                      {
                        title: "images",
                        icon: $globals.icons.folderOutline,
                        children: [
                          { title: "original.webp", icon: $globals.icons.codeJson },
                          { title: "full.jpg", icon: $globals.icons.fileImage },
                          { title: "thumb.jpg", icon: $globals.icons.fileImage },
                        ],
                      },
                    ],
                  },
                  {
                    title: "recipe-name-1",
                    icon: $globals.icons.folderOutline,
                    children: [
                      { title: "recipe-name-1.json", icon: $globals.icons.codeJson },
                      {
                        title: "images",
                        icon: $globals.icons.folderOutline,
                        children: [
                          { title: "original.webp", icon: $globals.icons.codeJson },
                          { title: "full.jpg", icon: $globals.icons.fileImage },
                          { title: "thumb.jpg", icon: $globals.icons.fileImage },
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
        text: i18n.t("migration.chowdown.description-long"),
        acceptedFileType: ".zip",
        tree: [
          {
            icon: $globals.icons.zip,
            title: "nextcloud.zip",
            children: [
              {
                title: i18n.t("migration.recipe-1"),
                icon: $globals.icons.folderOutline,
                children: [
                  { title: "recipe.json", icon: $globals.icons.codeJson },
                  { title: "full.jpg", icon: $globals.icons.fileImage },
                  { title: "thumb.jpg", icon: $globals.icons.fileImage },
                ],
              },
              {
                title: i18n.t("migration.recipe-2"),
                icon: $globals.icons.folderOutline,
                children: [
                  { title: "recipe.json", icon: $globals.icons.codeJson },
                  { title: "full.jpg", icon: $globals.icons.fileImage },
                  { title: "thumb.jpg", icon: $globals.icons.fileImage },
                ],
              },
            ],
          },
        ],
      },
      [MIGRATIONS.copymethat]: {
        text: i18n.t("migration.copymethat.description-long"),
        acceptedFileType: ".zip",
        tree: [
          {
            icon: $globals.icons.zip,
            title: "Copy_Me_That_20230306.zip",
            children: [
              {
                title: "images",
                icon: $globals.icons.folderOutline,
                children: [
                  { title: "recipe_1_an5zy.jpg", icon: $globals.icons.fileImage },
                  { title: "recipe_2_82el8.jpg", icon: $globals.icons.fileImage },
                  { title: "recipe_3_j75qg.jpg", icon: $globals.icons.fileImage },
                ],
              },
              { title: "recipes.html", icon: $globals.icons.codeJson },
            ],
          },
        ],
      },
      [MIGRATIONS.myrecipebox]: {
        text: i18n.t("migration.myrecipebox.description-long"),
        acceptedFileType: ".csv",
        tree: false,
      },
      [MIGRATIONS.nextcloud]: {
        text: i18n.t("migration.nextcloud.description-long"),
        acceptedFileType: ".zip",
        tree: [
          {
            icon: $globals.icons.zip,
            title: "nextcloud.zip",
            children: [
              {
                title: i18n.t("migration.recipe-1"),
                icon: $globals.icons.folderOutline,
                children: [
                  { title: "recipe.json", icon: $globals.icons.codeJson },
                  { title: "full.jpg", icon: $globals.icons.fileImage },
                  { title: "thumb.jpg", icon: $globals.icons.fileImage },
                ],
              },
              {
                title: i18n.t("migration.recipe-2"),
                icon: $globals.icons.folderOutline,
                children: [
                  { title: "recipe.json", icon: $globals.icons.codeJson },
                  { title: "full.jpg", icon: $globals.icons.fileImage },
                  { title: "thumb.jpg", icon: $globals.icons.fileImage },
                ],
              },
            ],
          },
        ],
      },
      [MIGRATIONS.paprika]: {
        text: i18n.t("migration.paprika.description-long"),
        acceptedFileType: ".zip",
        tree: false,
      },
      [MIGRATIONS.plantoeat]: {
        text: i18n.t("migration.plantoeat.description-long"),
        acceptedFileType: ".zip",
        tree: [
          {
            icon: $globals.icons.zip,
            title: "plantoeat-recipes-508318_10-13-2023.zip",
            children: [
              { title: "plantoeat-recipes-508318_10-13-2023.csv", icon: $globals.icons.codeJson },
            ],
          },
        ],
      },
      [MIGRATIONS.recipekeeper]: {
        text: i18n.t("migration.recipekeeper.description-long"),
        acceptedFileType: ".zip",
        tree: [
          {
            icon: $globals.icons.zip,
            title: "recipekeeperhtml.zip",
            children: [
              { title: "recipes.html", icon: $globals.icons.codeJson },
              {
                title: "images", icon: $globals.icons.folderOutline,
                children: [
                  { title: "image1.jpg", icon: $globals.icons.fileImage },
                  { title: "image2.jpg", icon: $globals.icons.fileImage },
                ],
              },
            ],
          },
        ],
      },
      [MIGRATIONS.tandoor]: {
        text: i18n.t("migration.tandoor.description-long"),
        acceptedFileType: ".zip",
        tree: [
          {
            icon: $globals.icons.zip,
            title: "tandoor_default_export_full_2023-06-29.zip",
            children: [
              {
                title: "1.zip",
                icon: $globals.icons.zip,
                children: [
                  { title: "image.jpeg", icon: $globals.icons.fileImage },
                  { title: "recipe.json", icon: $globals.icons.codeJson },
                ],
              },
              {
                title: "2.zip",
                icon: $globals.icons.zip,
                children: [
                  { title: "image.jpeg", icon: $globals.icons.fileImage },
                  { title: "recipe.json", icon: $globals.icons.codeJson },
                ],
              },
              {
                title: "3.zip",
                icon: $globals.icons.zip,
                children: [
                  { title: "image.jpeg", icon: $globals.icons.fileImage },
                  { title: "recipe.json", icon: $globals.icons.codeJson },
                ],
              },
            ],
          },
        ],
      },
    };

    function addIdToNode(counter: number, node: TreeNode): number {
      node.id = counter;
      counter += 1;
      if (node.children) {
        node.children.forEach((child: TreeNode) => {
          counter = addIdToNode(counter, child);
        });
      }
      return counter;
    }

    for (const key in _content) {
      const migration = _content[key];
      if (migration.tree && Array.isArray(migration.tree)) {
        let counter = 1;
        migration.tree.forEach((node: TreeNode) => {
          counter = addIdToNode(counter, node);
        });
      }
    }

    console.log(_content);

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
      }
      else {
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
});
</script>

<style lang="scss" scoped></style>
