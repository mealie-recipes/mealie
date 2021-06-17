<template>
  <v-card flat>
    <CreatePageDialog ref="createDialog" @refresh-page="getPages" />
    <v-card-text>
      <h2 class="mt-1 mb-1 ">
        {{ $t("settings.custom-pages") }}
        <span>
          <TheButton create small class="ml-3" @click="newPage" />
        </span>
      </h2>
      <draggable class="row mt-1" v-model="customPages">
        <v-col :sm="6" :md="6" :lg="4" :xl="3" v-for="(item, index) in customPages" :key="item + item.id">
          <v-card>
            <v-card-text class="mb-0 pb-0">
              <h3>{{ item.name }}</h3>
              <v-divider></v-divider>
            </v-card-text>
            <v-card-text class="mt-0">
              <div>
                <v-chip
                  v-for="cat in item.categories"
                  :key="cat.slug + cat.id"
                  class="my-2 mr-2"
                  label
                  small
                  color="accent lighten-1"
                >
                  {{ cat.name }}
                </v-chip>
              </div>
            </v-card-text>

            <v-card-actions>
              <ConfirmationDialog
                :title="$t('page.page') + ' ' + $t('general.delete')"
                :icon="$globals.icons.pages"
                :message="$t('general.confirm-delete-generic')"
                @confirm="deletePage(item.id)"
              >
                <template v-slot="{ open }">
                  <TheButton delete small minor @click="open" />
                </template>
              </ConfirmationDialog>
              <v-spacer> </v-spacer>
              <TheButton edit small @click="editPage(index)" />
            </v-card-actions>
          </v-card>
        </v-col>
      </draggable>
    </v-card-text>
    <v-card-actions>
      <v-spacer></v-spacer>
      <TheButton update @click="savePages" />
    </v-card-actions>
  </v-card>
</template>

<script>
import draggable from "vuedraggable";
import CreatePageDialog from "./CreatePageDialog";
import ConfirmationDialog from "@/components/UI/Dialogs/ConfirmationDialog.vue";
import TheButton from "@/components/UI/Buttons/TheButton.vue";
import { api } from "@/api";
export default {
  components: {
    draggable,
    CreatePageDialog,
    ConfirmationDialog,
    TheButton,
  },
  data() {
    return {
      pageDialog: false,
      customPages: [],
      newPageData: {
        create: true,
        title: this.$t("settings.new-page"),
        buttonText: this.$t("general.create"),
        data: {
          name: "",
          categories: [],
          position: 0,
        },
      },
      editPageData: {
        create: false,
        title: this.$t("settings.edit-page"),
        buttonText: this.$t("general.update"),
        data: {},
      },
    };
  },
  async mounted() {
    this.getPages();
  },
  methods: {
    async getPages() {
      this.customPages = await api.siteSettings.getPages();
      this.customPages.sort((a, b) => a.position - b.position);
    },
    async deletePage(id) {
      await api.siteSettings.deletePage(id);
      this.getPages();
    },
    async savePages() {
      this.customPages.forEach((element, index) => {
        element.position = index;
      });

      if (await api.siteSettings.updateAllPages(this.customPages)) {
        this.getPages();
      }
    },
    editPage(index) {
      this.editPageData.data = this.customPages[index];
      this.$refs.createDialog.open(this.editPageData);
    },
    newPage() {
      this.newPageData.position = this.customPages.length;
      this.$refs.createDialog.open(this.newPageData);
    },
  },
};
</script>

<style lang="scss" scoped></style>
