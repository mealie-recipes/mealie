<template>
  <div>
    <v-btn text color="success" @click="dialog = true"> {{$t('general.new')}} </v-btn>
    <v-dialog v-model="dialog" width="400">
      <v-card>
        <v-card-title> {{$t('settings.add-a-new-theme')}} </v-card-title>
        <v-card-text>
          <v-text-field label="Theme Name" v-model="themeName"></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-btn color="success" text @click="Select"> {{$t('general.create')}} </v-btn>
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
          primary: this.randomColor(),
          accent: this.randomColor(),
          secondary: this.randomColor(),
          success: this.randomColor(),
          info: this.randomColor(),
          warning: this.randomColor(),
          error: this.randomColor(),
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