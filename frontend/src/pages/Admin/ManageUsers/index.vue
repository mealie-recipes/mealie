<template>
  <v-data-table
    :headers="headers"
    :items="users"
    sort-by="calories"
    class="elevation-1"
  >
    <template v-slot:top>
      <v-toolbar flat>
        <v-toolbar-title>Mealie Users</v-toolbar-title>
        <v-divider class="mx-4" inset vertical></v-divider>
        <v-spacer></v-spacer>
        <v-dialog v-model="dialog" max-width="600px">
          <template v-slot:activator="{ on, attrs }">
            <v-btn color="primary" dark class="mb-2" v-bind="attrs" v-on="on">
              Create User
            </v-btn>
          </template>
          <v-card>
            <v-app-bar dark dense color="primary">
              <v-icon left>
                mdi-account
              </v-icon>

              <v-toolbar-title class="headline">
                {{ formTitle }}
              </v-toolbar-title>

              <v-spacer></v-spacer>
              <v-toolbar-title class="headline">
                User ID: {{ editedItem.id }}
              </v-toolbar-title>
            </v-app-bar>

            <v-card-text>
              <v-container>
                <v-row>
                  <v-col cols="12" sm="12" md="6">
                    <v-text-field
                      v-model="editedItem.fullName"
                      label="Full Name"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" sm="12" md="6">
                    <v-text-field
                      v-model="editedItem.email"
                      label="Email"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" sm="12" md="6">
                    <v-text-field
                      v-model="editedItem.family"
                      label="Family Group"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" sm="12" md="6" v-if="showPassword">
                    <v-text-field
                      v-model="editedItem.password"
                      label="User Password"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" sm="12" md="3">
                    <v-switch
                      v-model="editedItem.admin"
                      label="Admin"
                    ></v-switch>
                  </v-col>
                </v-row>
              </v-container>
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
        <Confirmation
          ref="deleteUserDialog"
          title="Confirm User Deletion"
          :message="
            `Are you sure you want to delete the user <b>${activeName} ID: ${activeId}<b/>`
          "
          icon="mdi-alert"
          @confirm="deleteUser"
          :width="450"
          @close="closeDelete"
        />
      </v-toolbar>
    </template>
    <template v-slot:item.actions="{ item }">
      <v-btn class="mr-1" small color="error" @click="deleteItem(item)">
        <v-icon small left>
          mdi-delete
        </v-icon>
        Delete
      </v-btn>
      <v-btn small color="success" @click="editItem(item)">
        <v-icon small left class="mr-2">
          mdi-pencil
        </v-icon>
        Edit
      </v-btn>
    </template>
    <template v-slot:item.admin="{ item }">
      {{ item.admin ? "Admin" : "User" }}
    </template>
    <template v-slot:no-data>
      <v-btn color="primary" @click="initialize">
        Reset
      </v-btn>
    </template>
  </v-data-table>
</template>

<script>
import Confirmation from "@/components/UI/Confirmation";
import api from "@/api";
export default {
  components: { Confirmation },
  data: () => ({
    dialog: false,
    activeId: null,
    activeName: null,
    headers: [
      {
        text: "User ID",
        align: "start",
        sortable: false,
        value: "id",
      },
      { text: "Full Name", value: "fullName" },
      { text: "Email", value: "email" },
      { text: "Family", value: "family" },
      { text: "Admin", value: "admin" },
      { text: "", value: "actions", sortable: false, align: "center" },
    ],
    users: [],
    editedIndex: -1,
    editedItem: {
      id: 0,
      fullName: "",
      email: "",
      family: "",
      admin: false,
    },
    defaultItem: {
      id: 0,
      fullName: "",
      email: "",
      family: "",
      admin: false,
    },
  }),

  computed: {
    formTitle() {
      return this.editedIndex === -1 ? "New User" : "Edit User";
    },
    showPassword() {
      return this.editedIndex === -1 ? true : false;
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
    async initialize() {
      this.users = await api.users.allUsers();
    },

    async deleteUser() {
      await api.users.delete(this.editedIndex);
      this.initialize();
    },

    editItem(item) {
      this.editedIndex = this.users.indexOf(item);
      this.editedItem = Object.assign({}, item);
      this.dialog = true;
    },

    deleteItem(item) {
      this.activeId = item.id;
      this.activeName = item.fullName;
      this.editedIndex = this.users.indexOf(item);
      this.editedItem = Object.assign({}, item);
      this.$refs.deleteUserDialog.open();
    },

    deleteItemConfirm() {
      this.users.splice(this.editedIndex, 1);
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
        console.log("New User", this.editedItem);
        api.users.update(this.editedItem);
      } else {
        api.users.create(this.editedItem);
      }
      await this.initialize();
      this.close();
    },
  },
};
</script>

<style>
</style>