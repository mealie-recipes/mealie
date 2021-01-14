<template>
  <div>
    <v-btn text color="info" @click="dialog = true"> {{$t('general.new')}} </v-btn>
    <v-dialog v-model="dialog" width="400">
      <v-card>
        <v-card-title> {{$t('settings.add-a-new-theme')}} </v-card-title>
        <v-card-text>
          <v-text-field
            label="Theme Name"
            v-model="themeName"
            :rules="[rules.required]"
          ></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey" text @click="dialog = false"> {{$t('general.cancel')}} </v-btn>
          <v-btn color="success" text @click="Select" :disabled="!themeName">
            {{$t('general.create')}}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
export default {
  props: {
    buttonText: String,
    value: String,
  },
  data() {
    return {
      dialog: false,
      themeName: "",
      rules: {
        required: (val) => !!val || "Required.",
      },
    };
  },

  watch: {
    color() {
      this.updateColor();
    },
  },
  methods: {
    randomColor() {
      return "#" + Math.floor(Math.random() * 16777215).toString(16);
    },
    Select() {
      const newTheme = {
        name: this.themeName,
        colors: {
          primary: "#E58325",
          accent: "#00457A",
          secondary: "#973542",
          success: "#5AB1BB",
          info: "#4990BA",
          warning: "#FF4081",
          error: "#EF5350",
        },
      };

      this.$emit("new-theme", newTheme);
      this.dialog = false;
    },
  },
};
</script>

<style>
</style>