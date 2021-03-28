<template>
  <v-card flat>
    <v-card-text>
      <h2 class="mt-1 mb-1 ">
        Custom Pages
        <span>
          <v-btn color="success" small class="ml-3">
            New
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
            <v-card-title class="headline">{{ item.name }}</v-card-title>
            <v-divider></v-divider>

            <v-card-text>
              Card Position: {{ index }}
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
              <v-btn small text color="success">
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
import api from "@/api";
export default {
  components: {
    draggable,
  },
  data() {
    return {
      customPages: [],
    };
  },
  async mounted() {
    this.getPages();
  },
  methods: {
    async getPages() {
      this.customPages = await api.siteSettings.getPages();
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

      this.getPages;
    },
  },
};
</script>

<style lang="scss" scoped>
</style>