<template>
  <div v-if="model.length > 0 || edit">
    <v-card class="mt-4">
      <v-card-title class="py-2">
        {{ $t("asset.assets") }}
      </v-card-title>
      <v-divider class="mx-2" />
      <v-list
        v-if="model.length > 0"
        :flat="!edit"
      >
        <v-list-item
          v-for="(item, i) in model"
          :key="i"
        >
          <template #prepend>
            <div class="ma-auto">
              <v-tooltip location="bottom">
                <template #activator="{ props: tooltipProps }">
                  <v-icon v-bind="tooltipProps">
                    {{ getIconDefinition(item.icon).icon }}
                  </v-icon>
                </template>
                <span>{{ getIconDefinition(item.icon).title }}</span>
              </v-tooltip>
            </div>
          </template>
          <v-list-item-title class="pl-2">
            {{ item.name }}
          </v-list-item-title>
          <template #append>
            <v-btn
              v-if="!edit"
              color="primary"
              icon
              size="small"
              :href="assetURL(item.fileName ?? '')"
              target="_blank"
              top
            >
              <v-icon> {{ $globals.icons.download }} </v-icon>
            </v-btn>
            <div v-else>
              <v-btn
                color="error"
                icon
                size="small"
                top
                @click="model.splice(i, 1)"
              >
                <v-icon>{{ $globals.icons.delete }}</v-icon>
              </v-btn>
              <AppButtonCopy
                color=""
                :copy-text="assetEmbed(item.fileName ?? '')"
              />
            </div>
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
        <template #activator>
          <BaseButton
            v-if="edit"
            size="small"
            create
            @click="state.newAssetDialog = true"
          />
        </template>
        <v-card-text class="pt-4">
          <v-text-field
            v-model="state.newAsset.name"
            density="compact"
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
              <template #item="{ item, props }">
                <v-list-item v-bind="props">
                  <template #prepend>
                    <v-icon>{{ item.raw.icon }}</v-icon>
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
          {{ state.fileObject.name }}
        </v-card-text>
      </BaseDialog>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useStaticRoutes, useUserApi } from "~/composables/api";
import { alert } from "~/composables/use-toast";
import type { RecipeAsset } from "~/lib/api/types/recipe";

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

const { recipeAssetPath } = useStaticRoutes();
function assetURL(assetName: string) {
  return recipeAssetPath(props.recipeId, assetName);
}

function assetEmbed(name: string) {
  return `<img src="${serverBase}${assetURL(name)}" height="100%" width="100%"> </img>`;
}

function setFileObject(fileObject: File) {
  state.fileObject = fileObject;
}

function validFields() {
  return state.newAsset.name.length > 0 && state.fileObject.name.length > 0;
}

async function addAsset() {
  if (!validFields()) {
    alert.error(i18n.t("asset.error-submitting-form") as string);
    return;
  }

  const { data } = await api.recipes.createAsset(props.slug, {
    name: state.newAsset.name,
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
