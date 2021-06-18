<template>
  <div>
    <ConfirmationDialog
      ref="deleteGroupConfirm"
      :title="$t('group.confirm-group-deletion')"
      :message="
        $t('group.are-you-sure-you-want-to-delete-the-group', {
          groupName: group.name,
        })
      "
      :icon="$globals.icons.alert"
      @confirm="deleteGroup"
      :width="450"
      @close="closeGroupDelete"
    />
    <v-card class="ma-auto" tile min-height="325px">
      <v-list dense>
        <v-card-title class="py-1">{{ group.name }}</v-card-title>
        <v-divider></v-divider>
        <v-subheader>{{ $t("group.group-id-with-value", { groupID: group.id }) }}</v-subheader>
        <v-list-item-group color="primary">
          <v-list-item v-for="property in groupProps" :key="property.text">
            <v-list-item-icon>
              <v-icon> {{ property.icon || $globals.icons.user }} </v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title class="pl-4 flex row justify-space-between">
                <div>{{ property.text }}</div>
                <div>{{ property.value }}</div>
              </v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list-item-group>
      </v-list>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn small color="error" @click="confirmDelete" :disabled="ableToDelete">
          {{ $t("general.delete") }}
        </v-btn>
        <!-- Coming Soon! -->
        <v-btn small color="success" disabled>
          {{ $t("general.edit") }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script>
const RENDER_EVENT = "update";
import ConfirmationDialog from "@/components/UI/Dialogs/ConfirmationDialog";
import { api } from "@/api";
export default {
  components: { ConfirmationDialog },
  props: {
    group: {
      default: {
        name: "DEFAULT_NAME",
        id: 1,
        users: [],
        mealplans: [],
        categories: [],
        webhookUrls: [],
        webhookTime: "00:00",
        webhookEnable: false,
      },
    },
  },
  data() {
    return {
      groupProps: {},
    };
  },
  computed: {
    ableToDelete() {
      return this.group.users.length >= 1 ? true : false;
    },
  },
  created() {
    this.buildData();
  },
  methods: {
    confirmDelete() {
      this.$refs.deleteGroupConfirm.open();
    },
    async deleteGroup() {
      if (await api.groups.delete(this.group.id)) {
        this.$emit(RENDER_EVENT);
      }
    },
    closeGroupDelete() {
      console.log("Close Delete");
    },
    buildData() {
      this.groupProps = [
        {
          text: this.$t("user.total-users"),
          icon: this.$globals.icons.user,
          value: this.group.users.length,
        },
        {
          text: this.$t("user.total-mealplans"),
          icon: this.$globals.icons.food,
          value: this.group.mealplans.length,
        },
        {
          text: this.$t("user.webhooks-enabled"),
          icon: this.$globals.icons.webhook,
          value: this.group.webhookEnable ? this.$t("general.yes") : this.$t("general.no"),
        },
        {
          text: this.$t("user.webhook-time"),
          icon: this.$globals.icons.clockOutline,
          value: this.group.webhookTime,
        },
      ];
    },
  },
};
</script>

<style scoped></style>
