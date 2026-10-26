<template>
  <div>
    <p>
      Mealie now checks where its own outgoing requests are going. Anything the server fetches on your
      behalf, such as importing a recipe from a URL, downloading a recipe image, sending a webhook, or
      running a recipe action, is only allowed to reach addresses on the public internet.
    </p>
    <p>
      This protects your network: without it, someone could use one of those features to make your Mealie
      server reach devices it can see but they can't.
    </p>
    <div v-if="user?.admin">
      <hr class="mt-2 mb-4">
      <p>
        Webhooks and recipe actions were not checked before, and the checks on recipe imports were
        narrower than they are now. If any of these pointed at something on your own network, they will
        stop working after this update.
      </p>
      <div class="mb-2">
        <p class="mb-1">
          Requests are now refused when the target resolves to:
        </p>
        <ul class="ml-6">
          <li>a private, loopback, or link-local address, including the cloud metadata endpoint</li>
          <li>
            the carrier-grade NAT range <code>100.64.0.0/10</code>. This one is worth noting, because it
            is the range <strong>Tailscale</strong> uses
          </li>
          <li>the IPv6 equivalents of all of the above</li>
        </ul>
      </div>
      <p>
        A hostname is also refused if <em>any</em> of the addresses it resolves to is non-public, not just
        the first one. Split-horizon DNS setups are the usual reason this bites.
      </p>
      <p>
        If you need a target on your own network to keep working, allow it explicitly with
        <code>HTTP_ALLOW_LIST</code>, which accepts hostnames or CIDRs. To keep a Tailscale host
        reachable, for example:
      </p>
      <p>
        <code>HTTP_ALLOW_LIST=100.64.0.0/10</code>
      </p>
      <p>
        There is also <code>HTTP_DISALLOW_LIST</code> for blocking targets that would otherwise be
        allowed, including public ones. It takes precedence over the allow list.
      </p>
      <p>
        Notifiers are unaffected. They send through the Apprise library rather than Mealie's own HTTP
        client, so they are not covered by these checks.
        <br>
        <v-btn
          class="mt-2"
          color="primary"
          href="https://docs.mealie.io/documentation/getting-started/installation/backend-config/#security"
          target="_blank"
        >
          Backend Configuration
        </v-btn>
      </p>
    </div>
    <div v-else>
      <p>
        If a webhook or recipe action of yours has stopped working, or a recipe URL that used to import no
        longer does, let your server admin know. It may be pointing at an address Mealie no longer reaches
        by default, and they can allow it on the server.
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
  title: "Outgoing requests are now restricted to public addresses",
};
</script>

<style scoped lang="css">
p {
  padding-bottom: 8px;
}
</style>
