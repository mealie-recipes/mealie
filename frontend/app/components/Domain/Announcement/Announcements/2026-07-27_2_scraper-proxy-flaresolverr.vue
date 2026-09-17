<template>
  <div>
    <p>
      Importing recipes from a URL is now more reliable. Mealie does a better job of looking like a real
      browser, rotates between several browser signatures, and retries more intelligently when a site
      pushes back. This works out of the box, with no configuration.
    </p>
    <p>
      Some sites sit behind bot protection (such as Cloudflare) that blocks requests made by a server, no
      matter how they're made. For those, Mealie can now optionally fall back to two extra layers.
    </p>
    <div class="mb-2">
      <ul class="ml-6">
        <li>
          <strong>Proxy support</strong>, which routes recipe and image requests through a proxy. This
          helps with sites that block your server's IP address.
        </li>
        <li>
          <strong>FlareSolverr support</strong>, which hands the page to a real headless browser as a last
          resort. This helps with challenges that Mealie can't get past on its own.
        </li>
      </ul>
    </div>
    <div v-if="user?.admin">
      <hr class="mt-2 mb-4">
      <p>
        Both are optional and off by default, so nothing changes unless you configure them. Mealie
        escalates only as far as it needs to for each import: a direct fetch first, then the proxy (if
        set), then FlareSolverr (if set, and only when the page is still blocked).
      </p>
      <p>
        Both are enabled with environment variables. Mealie does not ship or manage either one. You supply
        the proxy, and host FlareSolverr yourself (it runs nicely as a sidecar container). See the
        configuration docs for the settings, setup details, and an example compose file:
        <br>
        <v-btn
          class="mt-2"
          color="primary"
          href="https://docs.mealie.io/documentation/getting-started/installation/backend-config/#recipe-scraper"
          target="_blank"
        >
          Backend Configuration
        </v-btn>
      </p>
    </div>
    <div v-else>
      <p>
        If a recipe URL still refuses to import, let your server admin know. They can enable these extra
        options on the server.
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
  title: "Better recipe imports, with proxy and FlareSolverr support",
};
</script>

<style scoped lang="css">
p {
  padding-bottom: 8px;
}
</style>
