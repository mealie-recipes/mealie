<template>
  <v-card flat>
    <CreatePageDialog ref="createDialog" @refresh-page="getPages" />
    <v-card-text>
      <h2 class="mt-1 mb-1 ">
        Custom Pages
        <span>
          <v-btn color="success" @click="newPage" small class="ml-3">
            Create
          </v-btn>
        </span>
      </h2>
      <draggable class="row mt-1" v-model="customPages">
        <v-col
          :sm="6"
          :md="6"
          :lg="4"
          :xl="3"
          v-for="(item, index) in customPages"
          :key="item + item.id"
        >
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
              <v-btn text small color="error" @click="deletePage(item.id)">
                Delete
              </v-btn>
              <v-spacer> </v-spacer>
              <v-btn small text color="success" @click="editPage(index)">
                Edit
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </draggable>
    </v-card-text>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn color="success" @click="savePages">
        Save
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
import draggable from "vuedraggable";
import CreatePageDialog from "@/components/Admin/General/CreatePageDialog";
import { api } from "@/api";
export default {
  components: {
    draggable,
    CreatePageDialog,
  },
  data() {
    return {
      pageDialog: false,
      customPages: [],
      newPageData: {
        create: true,
        title: "New Page",
        buttonText: "Create",
        data: {
          name: "",
          categories: [],
          position: 0,
        },
      },
      editPageData: {
        create: false,
        title: "Edit Page",
        buttonText: "Update",
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

      await api.siteSettings.updateAllPages(this.customPages);

      this.getPages();
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

<style lang="scss" scoped>
</style>