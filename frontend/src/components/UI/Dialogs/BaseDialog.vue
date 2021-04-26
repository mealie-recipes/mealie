<template>
  <div>
    <v-dialog v-model="dialog" :width="modalWidth + 'px'">
      <v-card class="pb-2">
        <v-app-bar dark :color="color" class="mt-n1 mb-2">
          <v-icon large left v-if="!loading">
            {{ titleIcon }}
          </v-icon>
          <v-progress-circular
            v-else
            indeterminate
            color="white"
            large
            class="mr-2"
          >
          </v-progress-circular>
          <v-toolbar-title class="headline"> {{ title }} </v-toolbar-title>
          <v-spacer></v-spacer>
        </v-app-bar>
        <slot> </slot>
        <v-card-actions>
          <v-btn text color="grey" @click="dialog = false">
            Cancel
          </v-btn>
          <v-spacer></v-spacer>
          <v-btn color="success" @click="$emit('submit')">
            Submit
          </v-btn>
        </v-card-actions>
        <slot name="below-actions"> </slot>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
export default {
  props: {
    color: {
      default: "primary",
    },
    title: {
      default: "Modal Title",
    },
    titleIcon: {
      default: "mdi-account",
    },
    modalWidth: {
      default: "500",
    },
  },
  data() {
    return {
      dialog: false,
      loading: false,
    };
  },
  methods: {
    open() {
      this.dialog = true;
    },
  },
};
</script>

<style scoped>
</style>