<template>
  <div>
<<<<<<< HEAD:frontend/src/components/Admin/ThemeUI/NewTheme.vue
    <v-btn text color="success" @click="dialog = true"> {{$t('general.new')}} </v-btn>
=======
    <v-btn text color="info" @click="dialog = true"> New </v-btn>
>>>>>>> 5f25b2492e0263defdf1723cbb47ba536a1a7511:frontend/src/components/Settings/Theme/NewThemeDialog.vue
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
<<<<<<< HEAD:frontend/src/components/Admin/ThemeUI/NewTheme.vue
          <v-btn color="success" text @click="Select"> {{$t('general.create')}} </v-btn>
=======
          <v-spacer></v-spacer>
          <v-btn color="grey" text @click="dialog = false"> Cancel </v-btn>
          <v-btn color="success" text @click="Select" :disabled="!themeName">
            Create
          </v-btn>
>>>>>>> 5f25b2492e0263defdf1723cbb47ba536a1a7511:frontend/src/components/Settings/Theme/NewThemeDialog.vue
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