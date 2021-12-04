<template>
  <div>
    <v-checkbox
      v-for="(option, index) in options"
      :key="index"
      v-model="option.value"
      class="mb-n4 mt-n3"
      dense
      :label="option.text"
      @change="emitValue()"
    ></v-checkbox>
    <template v-if="importBackup">
      <v-divider class="my-3"></v-divider>
      <v-checkbox
        v-model="forceImport"
        class="mb-n4"
        dense
        :label="$t('settings.remove-existing-entries-matching-imported-entries')"
        @change="emitValue()"
      ></v-checkbox>
    </template>
  </div>
</template>

<script>
const UPDATE_EVENT = "input";
export default {
  props: {
    importBackup: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      options: {
        recipes: {
          value: true,
          text: this.$t("general.recipes"),
        },
        users: {
          value: true,
          text: this.$t("user.users"),
        },
        groups: {
          value: true,
          text: this.$t("group.groups"),
        },
      },
      forceImport: false,
    };
  },
  mounted() {
    this.emitValue();
  },
  methods: {
    emitValue() {
      this.$emit(UPDATE_EVENT, {
        recipes: this.options.recipes.value,
        settings: false,
        themes: false,
        pages: false,
        users: this.options.users.value,
        groups: this.options.groups.value,
        notifications: false,
        forceImport: this.forceImport,
      });
    },
  },
};
</script>