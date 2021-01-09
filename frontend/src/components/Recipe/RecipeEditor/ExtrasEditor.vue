<template>
  <div class="text-center">
    <v-dialog v-model="dialog" width="700">
      <template v-slot:activator="{ on, attrs }">
        <v-btn color="accent" dark v-bind="attrs" v-on="on"> API Extras </v-btn>
      </template>

      <v-card>
        <v-card-title> API Extras </v-card-title>

        <v-card-text :key="formKey">
          <v-row
            align="center"
            v-for="(value, key, index) in extras"
            :key="index"
          >
            <v-col cols="12" sm="1">
              <v-btn
                fab
                text
                x-small
                color="white"
                elevation="0"
                @click="removeExtra(key)"
              >
                <v-icon color="error">mdi-delete</v-icon>
              </v-btn>
            </v-col>
            <v-col cols="12" md="3" sm="6">
              <v-text-field
                label="Object Key"
                :value="key"
                @input="updateKey(index)"
              >
              </v-text-field>
            </v-col>
            <v-col cols="12" md="8" sm="6">
              <v-text-field label="Object Value" v-model="extras[key]">
              </v-text-field>
            </v-col>
          </v-row>
        </v-card-text>

        <v-divider></v-divider>

        <v-card-actions>
          <v-form ref="addKey">
            <v-text-field
              label="New Key Name"
              v-model="newKeyName"
              class="pr-4"
              :rules="[rules.required, rules.whiteSpace]"
            ></v-text-field>
          </v-form>
          <v-btn color="info" text @click="append"> Add Key</v-btn>

          <v-spacer></v-spacer>

          <v-btn color="success" text @click="save"> I accept </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
export default {
  props: {
    extras: Object,
  },
  data() {
    return {
      newKeyName: null,
      dialog: false,
      formKey: 1,
      rules: {
        required: (v) => !!v || "Key Name Required",
        whiteSpace: (v) => !v || v.split(" ").length <= 1 || "No White Space Allowed",
      },
    };
  },

  methods: {
    save() {
      this.$emit("save", this.extras);
      this.dialog = false;
    },
    append() {
      if (this.$refs.addKey.validate()) {
        this.extras[this.newKeyName] = "value";
        this.formKey += 1;
      }
    },
    removeExtra(key) {
      delete this.extras[key];
      this.formKey += 1;
    },
  },
};
</script>

<style>
</style>