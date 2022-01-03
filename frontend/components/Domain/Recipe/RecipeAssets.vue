<template>
  <div v-if="value.length > 0 || edit">
    <v-card class="mt-2">
      <v-card-title class="py-2">
        {{ $t("asset.assets") }}
      </v-card-title>
      <v-divider class="mx-2"></v-divider>
      <v-list v-if="value.length > 0" :flat="!edit">
        <v-list-item v-for="(item, i) in value" :key="i">
          <v-list-item-icon class="ma-auto">
            <v-tooltip bottom>
              <template #activator="{ on, attrs }">
                <v-icon v-bind="attrs" v-on="on" v-text="getIconDefinition(item.icon).icon"></v-icon>
              </template>
              <span>{{ getIconDefinition(item.icon).title }}</span>
            </v-tooltip>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title class="pl-2" v-text="item.name"></v-list-item-title>
          </v-list-item-content>
          <v-list-item-action>
            <v-btn v-if="!edit" color="primary" icon :href="assetURL(item.fileName)" target="_blank" top>
              <v-icon> {{ $globals.icons.download }} </v-icon>
            </v-btn>
            <div v-else>
              <v-btn color="error" icon top @click="value.splice(i, 1)">
                <v-icon>{{ $globals.icons.delete }}</v-icon>
              </v-btn>
              <AppButtonCopy color="" :copy-text="assetEmbed(item.fileName)" />
            </div>
          </v-list-item-action>
        </v-list-item>
      </v-list>
    </v-card>
    <div class="d-flex ml-auto mt-2">
      <v-spacer></v-spacer>
      <BaseDialog
        v-model="newAssetDialog"
        :title="$t('asset.new-asset')"
        :icon="getIconDefinition(newAsset.icon).icon"
        @submit="addAsset"
      >
        <template #activator>
          <BaseButton v-if="edit" small create @click="newAssetDialog = true" />
        </template>
        <v-card-text class="pt-4">
          <v-text-field v-model="newAsset.name" dense :label="$t('general.name')"></v-text-field>
          <div class="d-flex justify-space-between">
            <v-select
              v-model="newAsset.icon"
              dense
              :prepend-icon="getIconDefinition(newAsset.icon).icon"
              :items="iconOptions"
              item-text="title"
              item-value="name"
              class="mr-2"
            >
              <template #item="{ item }">
                <v-list-item-avatar>
                  <v-icon class="mr-auto">
                    {{ item.icon }}
                  </v-icon>
                </v-list-item-avatar>
                {{ item.title }}
              </template>
            </v-select>
            <AppButtonUpload :post="false" file-name="file" :text-btn="false" @uploaded="setFileObject" />
          </div>
          {{ fileObject.name }}
        </v-card-text>
      </BaseDialog>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, useContext } from "@nuxtjs/composition-api";
import { useUserApi } from "~/composables/api";
import { alert } from "~/composables/use-toast";

const BASE_URL = window.location.origin;

export default defineComponent({
  props: {
    slug: {
      type: String,
      required: true,
    },
    value: {
      type: Array,
      required: true,
    },
    edit: {
      type: Boolean,
      default: true,
    },
  },
  setup(props, context) {
    const api = useUserApi();

    const state = reactive({
      newAssetDialog: false,
      fileObject: {} as File,
      newAsset: {
        name: "",
        icon: "mdi-file",
      },
    });

    const { $globals, i18n } = useContext();

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

    function getIconDefinition(icon: string) {
      return iconOptions.find((item) => item.name === icon) || iconOptions[0];
    }

    function assetURL(assetName: string) {
      return api.recipes.recipeAssetPath(props.slug, assetName);
    }

    function assetEmbed(name: string) {
      return `<img src="${BASE_URL}${assetURL(name)}" height="100%" width="100%"> </img>`;
    }

    function setFileObject(fileObject: any) {
      state.fileObject = fileObject;
    }

    function validFields() {
      return state.newAsset.name.length > 0 && state.fileObject.name.length > 0;
    }

    async function addAsset() {
      if (!validFields()) {
        alert.error("Error Submitting Form");
        return;
      }

      const { data } = await api.recipes.createAsset(props.slug, {
        name: state.newAsset.name,
        icon: state.newAsset.icon,
        file: state.fileObject,
        extension: state.fileObject.name.split(".").pop() || "",
      });

      context.emit("input", [...props.value, data]);
      state.newAsset = { name: "", icon: "mdi-file" };
      state.fileObject = {} as File;
    }

    return {
      ...toRefs(state),
      addAsset,
      assetURL,
      assetEmbed,
      getIconDefinition,
      iconOptions,
      setFileObject,
    };
  },
});
</script>
