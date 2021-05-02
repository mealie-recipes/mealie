<template>
  <div>
    <base-dialog
      ref="deleteDialog"
      title-icon="mdi-tag"
      color="error"
      :title="$t('general.delete') + ' ' + (isTags ? $t('tag.tags') : $t('recipe.categories'))"
      :loading="loading"
      modal-width="400"
    >
      <v-list v-if="deleteList.length > 0">
        <v-list-item v-for="item in deleteList" :key="item.slug">
          <v-list-item-content>
            {{ item.name }}
          </v-list-item-content>
        </v-list-item>
      </v-list>
      <v-card-text v-else class=" mt-4 text-center">
        {{ $t("settings.toolbox.no-unused-items") }}
      </v-card-text>
      <template slot="card-actions">
        <v-btn text color="grey" @click="closeDialog">
          {{ $t("general.cancel") }}
        </v-btn>
        <v-spacer></v-spacer>
        <v-btn color="error" @click="deleteUnused" :loading="loading" :disabled="deleteList.length < 1">
          {{ $t("general.delete") }}
        </v-btn>
      </template>
    </base-dialog>

    <v-btn @click="openDialog" small color="error" class="mr-1">
      {{ $t("settings.toolbox.remove-unused") }}
    </v-btn>
  </div>
</template>

<script>
import BaseDialog from "@/components/UI/Dialogs/BaseDialog";
import { api } from "@/api";
export default {
  props: {
    isTags: {
      default: true,
    },
  },
  components: {
    BaseDialog,
  },
  data() {
    return {
      deleteList: [],
      loading: false,
    };
  },
  methods: {
    closeDialog() {
      this.$refs.deleteDialog.close();
    },
    async openDialog() {
      this.$refs.deleteDialog.open();
      if (this.isTags) {
        this.deleteList = await api.tags.getEmpty();
      } else {
        this.deleteList = await api.categories.getEmpty();
      }
    },

    async deleteUnused() {
      this.loading = true;
      if (this.isTags) {
        this.deleteList.forEach(async element => {
          await api.tags.delete(element.slug, true);
        });
        this.$store.dispatch("requestTags");
      } else {
        this.deleteList.forEach(async element => {
          await api.categories.delete(element.slug, true);
        });
        this.$store.dispatch("requestCategories");
      }
      this.loading = false;
      this.closeDialog();
    },
  },
};
</script>

<style lang="scss" scoped></style>
