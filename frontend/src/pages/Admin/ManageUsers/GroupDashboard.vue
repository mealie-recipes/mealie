<template>
  <div>
    <v-card outlined class="mt-n1">
      <v-card-actions>
        <v-spacer></v-spacer>
        <div width="100px">
          <v-text-field
            v-model="filter"
            clearable
            class="mr-2 pt-0"
            :append-icon="$globals.icons.filter"
            :label="$t('general.filter')"
            single-line
            hide-details
          ></v-text-field>
        </div>
        <v-dialog v-model="groupDialog" max-width="400">
          <template v-slot:activator="{ on, attrs }">
            <v-btn class="mx-2" small color="success" dark v-bind="attrs" v-on="on">
              {{ $t("group.create-group") }}
            </v-btn>
          </template>
          <v-card>
            <v-app-bar dark dense color="primary">
              <v-icon left>
                {{ $globals.icons.group }}
              </v-icon>

              <v-toolbar-title class="headline">
                {{ $t("group.create-group") }}
              </v-toolbar-title>

              <v-spacer></v-spacer>
            </v-app-bar>
            <v-form ref="newGroup" @submit.prevent="createGroup">
              <v-card-text>
                <v-text-field
                  v-model="newGroupName"
                  :label="$t('group.group-name')"
                  :rules="[existsRule]"
                ></v-text-field>
              </v-card-text>

              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="grey" text @click="groupDialog = false">
                  {{ $t("general.cancel") }}
                </v-btn>
                <v-btn color="primary" type="submit">
                  {{ $t("general.create") }}
                </v-btn>
              </v-card-actions>
            </v-form>
          </v-card>
        </v-dialog>
      </v-card-actions>
      <v-card-text>
        <v-row>
          <v-col :sm="6" :md="6" :lg="4" :xl="3" v-for="group in groups" :key="group.id">
            <GroupCard :group="group" @update="$store.dispatch('requestAllGroups')" />
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import { validators } from "@/mixins/validators";
import { api } from "@/api";
import GroupCard from "./GroupCard";
export default {
  components: { GroupCard },
  mixins: [validators],
  data() {
    return {
      filter: "",
      groupDialog: false,
      newGroupName: "",
    };
  },
  computed: {
    groups() {
      return this.$store.getters.getGroups;
    },
  },
  methods: {
    async createGroup() {
      this.groupLoading = true;
      if (await api.groups.create(this.newGroupName)) {
        this.groupDialog = false;
        this.$store.dispatch("requestAllGroups");
      }
      this.groupLoading = false;
    },
  },
};
</script>

<style></style>
