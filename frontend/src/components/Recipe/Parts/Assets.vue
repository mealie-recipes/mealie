<template>
  <div v-if="value.length > 0 || edit">
    <v-card class="mt-2">
      <v-card-title class="py-2">
        {{ $t("asset.assets") }}
      </v-card-title>
      <v-divider class="mx-2"></v-divider>
      <v-list :flat="!edit" v-if="value.length > 0">
        <v-list-item v-for="(item, i) in value" :key="i">
          <v-list-item-icon class="ma-auto">
            <v-tooltip bottom>
              <template v-slot:activator="{ on, attrs }">
                <v-icon v-text="getIconDefinition(item.icon).icon" v-bind="attrs" v-on="on"></v-icon>
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
              <v-btn color="error" icon @click="deleteAsset(i)" top>
                <v-icon>{{ $globals.icons.delete }}</v-icon>
              </v-btn>
              <TheCopyButton :copy-text="copyLink(item.fileName)" />
            </div>
          </v-list-item-action>
        </v-list-item>
      </v-list>
    </v-card>
    <div class="d-flex ml-auto mt-2">
      <v-spacer></v-spacer>
      <base-dialog @submit="addAsset" :title="$t('asset.new-asset')" :title-icon="getIconDefinition(newAsset.icon).icon">
        <template v-slot:open="{ open }">
          <v-btn color="secondary" dark @click="open" v-if="edit">
            <v-icon>{{ $globals.icons.create }}</v-icon>
          </v-btn>
        </template>
        <v-card-text class="pt-2">
          <v-text-field dense v-model="newAsset.name" :label="$t('general.name')"></v-text-field>
          <div class="d-flex justify-space-between">
            <v-select
              dense
              :prepend-icon="getIconDefinition(newAsset.icon).icon"
              v-model="newAsset.icon"
              :items="iconOptions"
              item-text="title"
              item-value="name"
              class="mr-2"
            >
              <template v-slot:item="{ item }">
                <v-list-item-avatar>
                  <v-icon class="mr-auto">
                    {{ item.icon }}
                  </v-icon>
                </v-list-item-avatar>
                {{ item.title }}
              </template>
            </v-select>
            <TheUploadBtn @uploaded="setFileObject" :post="false" file-name="file" :text-btn="false" />
          </div>
          {{ fileObject.name }}
        </v-card-text>
      </base-dialog>
    </div>
  </div>
</template>

<script>
import TheCopyButton from "@/components/UI/Buttons/TheCopyButton";
import TheUploadBtn from "@/components/UI/Buttons/TheUploadBtn";
import BaseDialog from "@/components/UI/Dialogs/BaseDialog";
import { api } from "@/api";
export default {
  components: {
    BaseDialog,
    TheUploadBtn,
    TheCopyButton,
  },
  props: {
    slug: String,
    value: {
      type: Array,
    },
    edit: {
      type: Boolean,
      default: true,
    },
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
          title: this.$i18n.t('asset.file'),
          icon: this.$globals.icons.file 
        },
        { 
          name: "mdi-file-pdf-box",
          title: this.$i18n.t('asset.pdf'),
          icon: this.$globals.icons.filePDF 
        },
        { 
          name: "mdi-file-image",
          title: this.$i18n.t('asset.image'),
          icon: this.$globals.icons.fileImage 
        },
        { 
          name: "mdi-code-json",
          title: this.$i18n.t('asset.code'),
          icon: this.$globals.icons.codeJson 
        },
        { 
          name: "mdi-silverware-fork-knife",
          title: this.$i18n.t('asset.recipe'),
          icon: this.$globals.icons.primary 
        },
      ];
    },
  },
  methods: {
    getIconDefinition(val) {
      return this.iconOptions.find(({ name }) => name === val );
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

