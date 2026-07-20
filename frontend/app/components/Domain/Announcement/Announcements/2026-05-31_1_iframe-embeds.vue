<template>
  <div>
    <p>
      To harden Mealie against malicious content, <code>&lt;iframe&gt;</code> embeds in recipe
      instructions, notes, and descriptions are now restricted to a trusted set of hosts.
    </p>
    <div class="mb-2">
      By default, embeds are allowed only from well-known video providers:
      <ul class="ml-6">
        <li>YouTube</li>
        <li>Vimeo</li>
      </ul>
    </div>
    <p>
      Existing recipes that embed content from <strong>other</strong> hosts will no longer render
      those embeds. The rest of the recipe is unaffected.
    </p>
    <div v-if="user?.admin">
      <hr class="mt-2 mb-4">
      <p>
        As an admin, you can allow additional hosts with the <code>ALLOWED_IFRAME_HOSTS</code>
        environment variable (comma-separated). It extends the built-in defaults, and only
        <code>https</code> sources are permitted. See the configuration docs for details:
        <br>
        <v-btn
          class="mt-2"
          color="primary"
          href="https://docs.mealie.io/documentation/getting-started/installation/backend-config/"
          target="_blank"
        >
          Backend Configuration
        </v-btn>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { AnnouncementMeta } from "~/composables/use-announcements";

const { user } = useMealieAuth();
</script>

<script lang="ts">
export const meta: AnnouncementMeta = {
  title: "Recipe embeds restricted to trusted hosts",
};
</script>

<style scoped lang="css">
p {
  padding-bottom: 8px;
}
</style>
