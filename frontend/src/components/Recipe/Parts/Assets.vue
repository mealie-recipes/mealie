<template>
  <div v-if="value.length > 0 || edit">
    <v-card class="mt-2">
      <v-card-title class="py-2">
        {{ $t("recipe.assets") }}
      </v-card-title>
      <v-divider class="mx-2"></v-divider>
      <v-list :flat="!edit" v-if="value.length > 0">
        <v-list-item v-for="(item, i) in value" :key="i">
          <v-list-item-icon class="ma-auto">
            <v-icon v-text="item.icon"></v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title class="pl-2" v-text="item.name"></v-list-item-title>
          </v-list-item-content>
          <v-list-item-action>
            <v-btn v-if="!edit" color="primary" icon :href="assetURL(item.fileName)" target="_blank" top>
              <v-icon> mdi-download</v-icon>
            </v-btn>
            <div v-else>
              <v-btn color="error" icon @click="deleteAsset(i)" top>
                <v-icon>mdi-delete</v-icon>
              </v-btn>
              <v-btn color="primary" icon @click="copyLink(item.name, item.fileName)" top>
                <v-icon>mdi-content-copy</v-icon>
              </v-btn>
            </div>
          </v-list-item-action>
        </v-list-item>
      </v-list>
    </v-card>
    <div class="d-flex ml-auto mt-2">
      <v-spacer></v-spacer>
      <base-dialog @submit="addAsset" :title="$t('recipe.new-asset')" :title-icon="newAsset.icon">
        <template v-slot:open="{ open }">
          <v-btn color="secondary" dark @click="open" v-if="edit">
            <v-icon>mdi-plus</v-icon>
          </v-btn>
        </template>
        <v-card-text class="pt-2">
          <v-text-field dense v-model="newAsset.name" :label="$t('general.name')"></v-text-field>
          <div class="d-flex justify-space-between">
            <v-select dense :prepend-icon="newAsset.icon" v-model="newAsset.icon" :items="iconOptions" class="mr-2">
              <template v-slot:item="{ item }">
                <v-list-item-avatar>
                  <v-icon class="mr-auto">
                    {{ item }}
                  </v-icon>
                </v-list-item-avatar>
                {{ item }}
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
import TheUploadBtn from "@/components/UI/Buttons/TheUploadBtn";
import BaseDialog from "@/components/UI/Dialogs/BaseDialog";
import { api } from "@/api";
export default {
  components: {
    BaseDialog,
    TheUploadBtn,
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
      iconOptions: ["mdi-file", "mdi-file-pdf-box", "mdi-file-image", "mdi-code-json", "mdi-silverware-fork-knife"],
      menu: [
        {
          title: "Link 1",
          icon: "mdi-file",
          action: "Do Something",
        },
        {
          title: "Link 1",
          icon: "mdi-file",
          action: "Do Something",
        },
        {
          title: "Link 1",
          icon: "mdi-file",
          action: "Do Something",
        },
      ],
    };
  },
  computed: {
    baseURL() {
      return window.location.origin;
    },
  },
  methods: {
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
    copyLink(name, fileName) {
      const assetLink = api.recipes.recipeAssetPath(this.slug, fileName);
      const copyText = `![${name}](${assetLink})`;
      navigator.clipboard.writeText(copyText).then(
        () => console.log("Copied", copyText),
        () => console.log("Copied Failed", copyText)
      );
    },
  },
};
</script>

<style scoped></style>
