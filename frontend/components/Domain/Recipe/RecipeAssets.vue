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
              <v-btn color="error" icon top @click="deleteAsset(i)">
                <v-icon>{{ $globals.icons.delete }}</v-icon>
              </v-btn>
              <AppCopyButton :copy-text="copyLink(item.fileName)" />
            </div>
          </v-list-item-action>
        </v-list-item>
      </v-list>
    </v-card>
    <div class="d-flex ml-auto mt-2">
      <v-spacer></v-spacer>
      <BaseDialog :title="$t('asset.new-asset')" :icon="getIconDefinition(newAsset.icon).icon" @submit="addAsset">
        <template #open="{ open }">
          <v-btn v-if="edit" color="secondary" dark @click="open">
            <v-icon>{{ $globals.icons.create }}</v-icon>
          </v-btn>
        </template>
        <v-card-text class="pt-2">
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

<script>
import { useUserApi } from "~/composables/api";
export default {
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
  setup() {
    const api = useUserApi();

    return { api };
  },
  data() {
    return {
      fileObject: {},
      newAsset: {
        name: "",
        icon: "mdi-file",
      },
    };
  },
  computed: {
    baseURL() {
      return window.location.origin;
    },
    iconOptions() {
      return [
        {
          name: "mdi-file",
          title: this.$i18n.t("asset.file"),
          icon: this.$globals.icons.file,
        },
        {
          name: "mdi-file-pdf-box",
          title: this.$i18n.t("asset.pdf"),
          icon: this.$globals.icons.filePDF,
        },
        {
          name: "mdi-file-image",
          title: this.$i18n.t("asset.image"),
          icon: this.$globals.icons.fileImage,
        },
        {
          name: "mdi-code-json",
          title: this.$i18n.t("asset.code"),
          icon: this.$globals.icons.codeJson,
        },
        {
          name: "mdi-silverware-fork-knife",
          title: this.$i18n.t("asset.recipe"),
          icon: this.$globals.icons.primary,
        },
      ];
    },
  },
  methods: {
    getIconDefinition(val) {
      return this.iconOptions.find(({ name }) => name === val);
    },
    assetURL(assetName) {
      return api.recipes.recipeAssetPath(this.slug, assetName);
    },
    setFileObject(obj) {
      this.fileObject = obj;
    },
    async addAsset() {
      const serverAsset = await api.recipes.createAsset(
        this.slug,
        this.fileObject,
        this.newAsset.name,
        this.newAsset.icon
      );
      this.value.push(serverAsset.data);
      this.newAsset = { name: "", icon: "mdi-file" };
    },
    deleteAsset(index) {
      this.value.splice(index, 1);
    },
    copyLink(fileName) {
      const assetLink = api.recipes.recipeAssetPath(this.slug, fileName);
      return `<img src="${this.baseURL}${assetLink}" height="100%" width="100%"> </img>`;
    },
  },
};
</script>

