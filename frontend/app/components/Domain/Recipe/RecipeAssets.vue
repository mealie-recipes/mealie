<template>
  <div v-if="model.length > 0 || edit">
    <v-card class="mt-4">
      <v-list-item class="pr-2 pl-0">
        <v-card-title>
          {{ $t("asset.assets") }}
        </v-card-title>
        <template #append>
          <v-btn
            v-if="edit"
            variant="plain"
            :icon="$globals.icons.create"
            @click="state.newAssetDialog = true"
          />
        </template>
      </v-list-item>
      <v-divider class="mx-2" />
      <v-list
        v-if="model.length > 0"
        lines="two"
        :flat="!edit"
      >
        <v-list-item
          v-for="(item, i) in model"
          :key="i"
          :href="!edit ? assetURL(item.fileName ?? '') : ''"
          target="_blank"
          class="pr-2"
        >
          <template #prepend>
            <v-avatar size="48" rounded="lg" class="elevation-1">
              <v-img
                v-if="isImage(item.fileName)"
                :src="assetURL(item.fileName ?? '')"
                :alt="item.name"
                loading="lazy"
                cover
              />
              <v-icon v-else size="large">
                {{ getIconDefinition(item.icon).icon }}
              </v-icon>
            </v-avatar>
          </template>

          <v-list-item-title>
            {{ item.name }}
          </v-list-item-title>
          <template #append>
            <v-menu v-if="edit" location="bottom end">
              <template #activator="{ props: menuProps }">
                <v-btn
                  v-bind="menuProps"
                  icon
                  variant="plain"
                >
                  <v-icon :icon="$globals.icons.dotsVertical" />
                </v-btn>
              </template>
              <v-list density="compact" min-width="220">
                <v-list-item
                  :href="assetURL(item.fileName ?? '')"
                  :prepend-icon="$globals.icons.eye"
                  :title="$t('general.view')"
                  target="_blank"
                />
                <v-list-item
                  :href="assetURL(item.fileName ?? '')"
                  :prepend-icon="$globals.icons.download"
                  :title="$t('general.download')"
                  download
                />
                <v-list-item
                  v-if="edit"
                  :prepend-icon="$globals.icons.contentCopy"
                  :title="$t('general.copy')"
                  @click="copyText(assetEmbed(item.fileName ?? ''))"
                />
                <v-list-item
                  v-if="edit"
                  :prepend-icon="$globals.icons.delete"
                  :title="$t('general.delete')"
                  @click="model.splice(i, 1)"
                />
              </v-list>
            </v-menu>
            <v-btn
              v-if="!edit"
              icon
              variant="plain"
              :href="assetURL(item.fileName ?? '')"
              download
            >
              <v-icon> {{ $globals.icons.download }} </v-icon>
            </v-btn>
          </template>
        </v-list-item>
      </v-list>
    </v-card>
    <div class="d-flex ml-auto mt-2">
      <v-spacer />
      <BaseDialog
        v-model="state.newAssetDialog"
        :title="$t('asset.new-asset')"
        :icon="getIconDefinition(state.newAsset.icon).icon"
        can-submit
        @submit="addAsset"
      >
        <v-card-text class="pt-4">
          <v-text-field
            v-model="state.newAsset.name"
            :label="$t('general.name')"
          />
          <div class="d-flex justify-space-between">
            <v-select
              v-model="state.newAsset.icon"
              density="compact"
              :prepend-icon="getIconDefinition(state.newAsset.icon).icon"
              :items="iconOptions"
              item-title="title"
              item-value="name"
              class="mr-2"
            >
              <template #item="{ props: itemProps, item }">
                <v-list-item v-bind="itemProps">
                  <template #prepend>
                    <v-avatar>
                      <v-icon>
                        {{ item.raw.icon }}
                      </v-icon>
                    </v-avatar>
                  </template>
                </v-list-item>
              </template>
            </v-select>
            <AppButtonUpload
              :post="false"
              file-name="file"
              :text-btn="false"
              @uploaded="setFileObject"
            />
          </div>
        </v-card-text>
      </BaseDialog>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useStaticRoutes, useUserApi } from "~/composables/api";
import { alert } from "~/composables/use-toast";
import type { RecipeAsset } from "~/lib/api/types/recipe";
import { useCopy } from "~/composables/use-copy";

const props = defineProps({
  slug: {
    type: String,
    required: true,
  },
  recipeId: {
    type: String,
    required: true,
  },
  edit: {
    type: Boolean,
    default: true,
  },
});

const model = defineModel<RecipeAsset[]>({ required: true });

const api = useUserApi();

const state = reactive({
  newAssetDialog: false,
  fileObject: {} as File,
  newAsset: {
    name: "",
    icon: "mdi-file",
  },
});

const i18n = useI18n();
const { $globals } = useNuxtApp();
const { copyText } = useCopy();

const iconOptions = [
  {
    name: "mdi-file",
    title: i18n.t("asset.file"),
    icon: $globals.icons.file,
  },
  {
    name: "mdi-file-pdf-box",
    title: i18n.t("asset.pdf"),
    icon: $globals.icons.filePDF,
  },
  {
    name: "mdi-file-image",
    title: i18n.t("asset.image"),
    icon: $globals.icons.fileImage,
  },
  {
    name: "mdi-code-json",
    title: i18n.t("asset.code"),
    icon: $globals.icons.codeJson,
  },
  {
    name: "mdi-silverware-fork-knife",
    title: i18n.t("asset.recipe"),
    icon: $globals.icons.primary,
  },
];

const serverBase = useRequestURL().origin;

function getIconDefinition(icon: string) {
  return iconOptions.find(item => item.name === icon) || iconOptions[0];
}

function isImage(fileName?: string | null) {
  if (!fileName) return false;
  return /\.(png|jpe?g|gif|webp|bmp|avif)$/i.test(fileName);
}

const { recipeAssetPath } = useStaticRoutes();
function assetURL(assetName: string) {
  return recipeAssetPath(props.recipeId, assetName);
}

function assetEmbed(name: string) {
  return `<img src="${serverBase}${assetURL(name)}" height="100%" width="100%" />`;
}

function setFileObject(fileObject: File) {
  state.fileObject = fileObject;
  // If the user didn't provide a name, default to the file base name
  if (!state.newAsset.name?.trim()) {
    state.newAsset.name = fileObject.name.substring(0, fileObject.name.lastIndexOf("."));
  }
}

function validFields() {
  // Only require a file; name will fall back to the file name if empty
  return Boolean(state.fileObject?.name);
}

async function addAsset() {
  if (!validFields()) {
    alert.error(i18n.t("asset.error-submitting-form") as string);
    return;
  }

  const nameToUse = state.newAsset.name?.trim() || state.fileObject.name;

  const { data } = await api.recipes.createAsset(props.slug, {
    name: nameToUse,
    icon: state.newAsset.icon,
    file: state.fileObject,
    extension: state.fileObject.name.split(".").pop() || "",
  });
  if (data) {
    model.value = [...model.value, data];
  }
  state.newAsset = { name: "", icon: "mdi-file" };
  state.fileObject = {} as File;
}
</script>
