<template>
  <div>
    <v-checkbox
      v-for="(option, index) in options"
      :key="index"
      class="mb-n4 mt-n3"
      dense
      :label="option.text"
      v-model="option.value"
      @change="emitValue()"
    ></v-checkbox>
  </div>
</template>

<script>
const UPDATE_EVENT = "update-options";
export default {
  data() {
    return {
      options: {
        recipes: {
          value: true,
          text: this.$t("general.recipes"),
        },
        settings: {
          value: true,
          text: this.$t("general.settings"),
        },
        pages: {
          value: true,
          text: this.$t("settings.pages"),
        },
        themes: {
          value: true,
          text: this.$t("general.themes"),
        },
        users: {
          value: true,
          text: this.$t("user.users"),
        },
        groups: {
          value: true,
          text: this.$t("group.groups"),
        },
        notifications: {
          value: true,
          text: this.$t("events.notification"),
        },
      },
    };
  },
  mounted() {
    this.emitValue();
  },
  methods: {
    emitValue() {
      this.$emit(UPDATE_EVENT, {
        recipes: this.options.recipes.value,
        settings: this.options.settings.value,
        themes: this.options.themes.value,
        pages: this.options.pages.value,
        users: this.options.users.value,
        groups: this.options.groups.value,
        notifications: this.options.notifications.value,
      });
    },
  },
};
</script>