<template>
  <v-card outlined class="mt-n1">
    <Confirmation
      ref="deleteUserDialog"
      :title="$t('user.confirm-user-deletion')"
      :message="
        $t('user.are-you-sure-you-want-to-delete-the-user', {
          activeName,
          activeId,
        })
      "
      icon="mdi-alert"
      @confirm="deleteUser"
      :width="450"
      @close="closeDelete"
    />
    <v-toolbar flat>
      <v-spacer> </v-spacer>
      <div width="100px">
        <v-text-field
          v-model="search"
          class="mr-2"
          append-icon="mdi-filter"
          :label="$t('general.filter')"
          single-line
          hide-details
        ></v-text-field>
      </div>

      <v-dialog v-model="dialog" max-width="600px">
        <template v-slot:activator="{ on, attrs }">
          <v-btn small color="success" dark v-bind="attrs" v-on="on">
            {{ $t("user.create-user") }}
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
              {{ $t("user.user-id-with-value", { id: editedItem.id }) }}
            </v-toolbar-title>
          </v-app-bar>
          <v-form ref="newUser" @submit.prevent="save">
            <v-card-text>
              <v-row>
                <v-col cols="12" sm="12" md="6">
                  <v-text-field
                    v-model="editedItem.fullName"
                    :label="$t('user.full-name')"
                    :rules="[existsRule]"
                    validate-on-blur
                  ></v-text-field>
                </v-col>
                <v-col cols="12" sm="12" md="6">
                  <v-text-field
                    v-model="editedItem.email"
                    :label="$t('user.email')"
                    :rules="[existsRule, emailRule]"
                    validate-on-blur
                  ></v-text-field>
                </v-col>
                <v-col cols="12" sm="12" md="6">
                  <v-select
                    dense
                    v-model="editedItem.group"
                    :items="existingGroups"
                    :label="$t('user.user-group')"
                  ></v-select>
                </v-col>
                <v-col cols="12" sm="12" md="6" v-if="showPassword">
                  <v-text-field
                    dense
                    v-model="editedItem.password"
                    :label="$t('user.user-password')"
                    :rules="[existsRule, minRule]"
                  ></v-text-field>
                </v-col>
                <v-col cols="12" sm="12" md="3">
                  <v-switch
                    v-model="editedItem.admin"
                    :label="$t('user.admin')"
                  ></v-switch>
                </v-col>
              </v-row>
            </v-card-text>

            <v-card-actions>
              <v-btn color="info" text @click="resetPassword">
                Reset Password
              </v-btn>
              <v-spacer></v-spacer>
              <v-btn color="grey" text @click="close">
                {{ $t("general.cancel") }}
              </v-btn>
              <v-btn color="primary" type="submit">
                {{ $t("general.save") }}
              </v-btn>
            </v-card-actions>
          </v-form>
        </v-card>
      </v-dialog>
    </v-toolbar>
    <v-divider></v-divider>
    <v-card-text>
      <v-data-table
        :headers="headers"
        :items="users"
        sort-by="calories"
        :search="search"
      >
        <template v-slot:item.actions="{ item }">
          <v-btn class="mr-1" small color="error" @click="deleteItem(item)">
            <v-icon small left>
              mdi-delete
            </v-icon>
            {{ $t("general.delete") }}
          </v-btn>
          <v-btn small color="success" @click="editItem(item)">
            <v-icon small left class="mr-2">
              mdi-pencil
            </v-icon>
            {{ $t("general.edit") }}
          </v-btn>
        </template>
        <template v-slot:item.admin="{ item }">
          {{ item.admin ? "Admin" : "User" }}
        </template>
        <template v-slot:no-data>
          <v-btn color="primary" @click="initialize">
            {{ $t("general.reset") }}
          </v-btn>
        </template>
      </v-data-table>
    </v-card-text>
  </v-card>
</template>

<script>
import Confirmation from "@/components/UI/Confirmation";
import { api } from "@/api";
import { validators } from "@/mixins/validators";
export default {
  components: { Confirmation },
  mixins: [validators],
  data() {
    return {
      search: "",
      dialog: false,
      activeId: null,
      activeName: null,
      headers: [
        {
          text: this.$t("user.user-id"),
          align: "start",
          sortable: false,
          value: "id",
        },
        { text: this.$t("user.full-name"), value: "fullName" },
        { text: this.$t("user.email"), value: "email" },
        { text: this.$t("user.group"), value: "group" },
        { text: this.$t("user.admin"), value: "admin" },
        { text: "", value: "actions", sortable: false, align: "center" },
      ],
      users: [],
      editedIndex: -1,
      editedItem: {
        id: 0,
        fullName: "",
        password: "",
        email: "",
        group: "",
        admin: false,
      },
      defaultItem: {
        id: 0,
        fullName: "",
        password: "",
        email: "",
        group: "",
        admin: false,
      },
    };
  },

  computed: {
    formTitle() {
      return this.editedIndex === -1
        ? this.$t("user.new-user")
        : this.$t("user.edit-user");
    },
    showPassword() {
      return this.editedIndex === -1 ? true : false;
    },
    existingGroups() {
      return this.$store.getters.getGroupNames;
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
      await api.users.delete(this.activeId);
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
        api.users.update(this.editedItem);
        this.close();
      } else if (this.$refs.newUser.validate()) {
        api.users.create(this.editedItem);
        this.close();
      }
      await this.initialize();
    },
    resetPassword() {
      console.log(this.activeId);
      api.users.resetPassword(this.editedItem.id);
    },
  },
};
</script>

<style>
</style>