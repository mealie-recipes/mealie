<template>
  <div>
    <v-card-title>
      <slot>
        <h1 class="mx-auto">{{ $t("404.page-not-found") }}</h1>
      </slot>
    </v-card-title>
    <div class="d-flex justify-space-around">
      <div class="d-flex">
        <p>4</p>
        <v-icon color="primary" class="mx-auto" size="200">
          {{ $globals.icons.primary }}
        </v-icon>
        <p>4</p>
      </div>
    </div>
    <v-card-actions>
      <v-spacer></v-spacer>
      <slot name="actions">
        <v-btn v-for="(button, index) in buttons" :key="index" :to="button.to" color="primary">
          <v-icon left> {{ button.icon }} </v-icon>
          {{ button.text }}
        </v-btn>
      </slot>
      <v-spacer></v-spacer>
    </v-card-actions>
  </div>
</template>

<script>
export default {
  computed: {
    buttons() {
      return[ 
        { icon: this.$globals.icons.home, to: "/", text: this.$t('general.home') },
        { icon: this.$globals.icons.primary, to: "/recipes/all", text: this.$t('page.all-recipes') },
        { icon: this.$globals.icons.search, to: "/search", text: this.$t('search.search') },
      ]; 
    },
  }
};
</script>

<style scoped>
p {
  padding-bottom: 0 !important;
  margin-bottom: 0 !important;
  color: var(--v-primary-base);
  font-size: 200px;
}
</style>