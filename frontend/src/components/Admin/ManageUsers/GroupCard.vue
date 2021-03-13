<template>
  <div>
    <Confirmation
      ref="deleteGroupConfirm"
      title="Confirm Group Deletion"
      :message="`Are you sure you want to delete <b>${group.name}<b/>`"
      icon="mdi-alert"
      @confirm="deleteGroup"
      :width="450"
      @close="closeGroupDelete"
    />
    <v-card class="ma-auto" tile min-height="325px">
      <v-list dense>
        <v-card-title class="py-1">{{ group.name }}</v-card-title>
        <v-divider></v-divider>
        <v-subheader>Group ID: {{ group.id }}</v-subheader>
        <v-list-item-group color="primary">
          <v-list-item v-for="property in groupProps" :key="property.text">
            <v-list-item-icon>
              <v-icon> {{ property.icon || "mdi-account" }} </v-icon>
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
        <v-btn
          small
          color="error"
          @click="confirmDelete"
          :disabled="ableToDelete"
        >
          Delete
        </v-btn>
        <!-- Coming Soon! -->
        <v-btn small color="success" disabled>
          Edit
        </v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script>
const RENDER_EVENT = "update";
import Confirmation from "@/components/UI/Confirmation";
import api from "@/api";
export default {
  components: { Confirmation },
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
  mounted() {
    this.buildData();
  },
  methods: {
    confirmDelete() {
      this.$refs.deleteGroupConfirm.open();
    },
    async deleteGroup() {
      await api.groups.delete(this.group.id);
      this.$emit(RENDER_EVENT);
    },
    closeGroupDelete() {
      console.log("Close Delete");
    },
    buildData() {
      this.groupProps = [
        {
          text: "Total Users",
          icon: "mdi-account",
          value: this.group.users.length,
        },
        {
          text: "Total MealPlans",
          icon: "mdi-food",
          value: this.group.mealplans.length,
        },
        {
          text: "Webhooks Enabled",
          icon: "mdi-webhook",
          value: this.group.webhookEnable ? "True" : "False",
        },
        {
          text: "Webhook Time",
          icon: "mdi-clock-outline",
          value: this.group.webhookTime,
        },
      ];
    },
  },
};
</script>

<style scoped>
</style>