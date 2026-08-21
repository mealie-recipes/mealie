<template>
  <div class="recipe-press-page">
    <div class="d-flex align-center justify-space-between px-4 py-2 ga-2">
      <div>
        <h1 class="text-h5 font-weight-medium">
          Recipe Press
        </h1>
        <p class="text-body-2 text-medium-emphasis mb-0">
          Generate, review, and send recipes directly to Mealie.
        </p>
      </div>
      <v-btn
        :href="recipePressUrl"
        target="_blank"
        rel="noopener noreferrer"
        variant="outlined"
        :prepend-icon="$globals.icons.externalLink"
      >
        Open in new tab
      </v-btn>
    </div>

    <iframe
      class="recipe-press-frame"
      :src="recipePressUrl"
      title="Recipe Press"
      allow="microphone"
    />
  </div>
</template>

<script setup lang="ts">
const config = useRuntimeConfig();
const recipePressUrl = config.public.RECIPE_PRESS_URL as string;

useSeoMeta({ title: "Recipe Press" });
</script>

<style scoped>
.recipe-press-page {
  height: calc(100dvh - 48px);
  display: flex;
  flex-direction: column;
}

.recipe-press-frame {
  width: 100%;
  flex: 1;
  border: 0;
  background: rgb(var(--v-theme-background));
}

@media (max-width: 600px) {
  .recipe-press-page {
    height: calc(100dvh - 48px);
  }
}
</style>
