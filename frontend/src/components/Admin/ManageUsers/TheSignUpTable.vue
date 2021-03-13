<template>
  <v-card outlined class="mt-n1">
    <Confirmation
      ref="deleteUserDialog"
      title="Confirm User Deletion"
      :message="`Are you sure you want to delete the link <b>${activeName}<b/>`"
      icon="mdi-alert"
      @confirm="deleteUser"
      :width="450"
      @close="closeDelete"
    />
    <v-toolbar flat>
      <v-icon large color="accent" class="mr-1">
        mdi-link-variant
      </v-icon>
      <v-toolbar-title class="headine">
        Sign Up Links
      </v-toolbar-title>

      <v-spacer> </v-spacer>
      <v-dialog v-model="dialog" max-width="600px">
        <template v-slot:activator="{ on, attrs }">
          <v-btn small color="success" dark v-bind="attrs" v-on="on">
            Create Link
          </v-btn>
        </template>
        <v-card>
          <v-app-bar dark dense color="primary">
            <v-icon left>
              mdi-account
            </v-icon>

            <v-toolbar-title class="headline">
              Create Link
            </v-toolbar-title>

            <v-spacer></v-spacer>
          </v-app-bar>

          <v-card-text>
            <v-form ref="newUser">
              <v-row class="justify-center mt-3">
                <v-text-field
                  class="mr-2"
                  v-model="editedItem.name"
                  label="Link Name"
                  :rules="[existsRule]"
                  validate-on-blur
                ></v-text-field>
                <v-checkbox
                  v-model="editedItem.admin"
                  label="Admin"
                ></v-checkbox>
              </v-row>
            </v-form>
          </v-card-text>

          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="grey" text @click="close">
              Cancel
            </v-btn>
            <v-btn color="primary" @click="save">
              Save
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-toolbar>
    <v-divider></v-divider>

    <v-card-text>
      <v-data-table :headers="headers" :items="links" sort-by="calories">
        <template v-slot:item.token="{ item }">
          {{ `${baseURL}/sign-up/${item.token}` }}
          <v-btn
            icon
            class="mr-1"
            small
            color="accent"
            @click="updateClipboard(`${baseURL}/sign-up/${item.token}`)"
          >
            <v-icon>
              mdi-content-copy
            </v-icon>
          </v-btn>
        </template>
        <template v-slot:item.admin="{ item }">
          <v-btn small :color="item.admin ? 'success' : 'error'" text>
            <v-icon small left>
              mdi-account-cog
            </v-icon>
            {{ item.admin ? "Yes" : "No" }}
          </v-btn>
        </template>
        <template v-slot:item.actions="{ item }">
          <v-btn class="mr-1" small color="error" @click="deleteItem(item)">
            <v-icon small left>
              mdi-delete
            </v-icon>
            Delete
          </v-btn>
        </template>
      </v-data-table>
    </v-card-text>
  </v-card>
</template>

<script>
import Confirmation from "@/components/UI/Confirmation";
import api from "@/api";
import { validators } from "@/mixins/validators";
export default {
  components: { Confirmation },
  mixins: [validators],
  data: () => ({
    dialog: false,
    activeId: null,
    activeName: null,
    headers: [
      {
        text: "Link ID",
        align: "start",
        sortable: false,
        value: "id",
      },
      { text: "Name", value: "name" },
      { text: "Token", value: "token" },
      { text: "Admin", value: "admin", align: "center" },
      { text: "", value: "actions", sortable: false, align: "center" },
    ],
    links: [],
    editedIndex: -1,
    editedItem: {
      name: "",
      admin: false,
      token: "",
      id: 0,
    },
    defaultItem: {
      name: "",
      token: "",
      admin: false,
      id: 0,
    },
  }),

  computed: {
    baseURL() {
      return window.location.origin;
    },
  },

  watch: {
    dialog(val) {
      val || this.close();
    },
    dialogDelete(val) {
      val || this.closeDelete();
    },
  },

  created() {
    this.initialize();
  },

  methods: {
    updateClipboard(newClip) {
      navigator.clipboard.writeText(newClip).then(
        function() {
          console.log("Copied", newClip);
        },
        function() {
          console.log("Copy Failed", newClip);
        }
      );
    },
    async initialize() {
      this.links = await api.signUps.getAll();
    },

    async deleteUser() {
      await api.signUps.deleteToken(this.activeId);
      this.initialize();
    },

    editItem(item) {
      this.editedIndex = this.links.indexOf(item);
      this.editedItem = Object.assign({}, item);
      this.dialog = true;
    },

    deleteItem(item) {
      this.activeId = item.token;
      this.activeName = item.name;
      this.editedIndex = this.links.indexOf(item);
      this.editedItem = Object.assign({}, item);
      this.$refs.deleteUserDialog.open();
    },

    deleteItemConfirm() {
      this.links.splice(this.editedIndex, 1);
      this.closeDelete();
    },

    close() {
      this.dialog = false;
      this.$nextTick(() => {
        this.editedItem = Object.assign({}, this.defaultItem);
        this.editedIndex = -1;
      });
    },

    closeDelete() {
      this.dialogDelete = false;
      this.$nextTick(() => {
        this.editedItem = Object.assign({}, this.defaultItem);
        this.editedIndex = -1;
      });
    },

    async save() {
      if (this.editedIndex > -1) {
        api.links.update(this.editedItem);
        this.close();
      } else if (this.$refs.newUser.validate()) {
        api.signUps.createToken({
          name: this.editedItem.name,
          admin: this.editedItem.admin,
        });
        this.close();
      }
      await this.initialize();
    },
  },
};
</script>

<style>
</style>