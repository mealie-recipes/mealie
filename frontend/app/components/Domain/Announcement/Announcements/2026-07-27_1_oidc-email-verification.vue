<template>
  <div>
    <p>
      If your server signs users in with an external identity provider (OIDC), Mealie now requires that
      provider to confirm the user's email address before allowing the login.
    </p>
    <p>
      This prevents an unverified, self-asserted email address from being used to match (and sign in) to
      an existing Mealie account.
    </p>
    <div v-if="user?.admin">
      <hr class="mt-2 mb-4">
      <p>
        As an admin, be aware that this is a <strong>breaking change</strong> for identity providers that do
        not emit the <code>email_verified</code> claim. Those logins now fail, and
        <code>[OIDC] email_verified claim is missing or false</code> is written to the server logs.
      </p>
      <div class="mb-2">
        You have two options:
        <ul class="ml-6">
          <li>Configure your identity provider to include the <code>email_verified</code> claim (recommended)</li>
          <li>Set <code>OIDC_REQUIRES_EMAIL_VERIFICATION=false</code> to restore the previous behavior</li>
        </ul>
      </div>
      <p>
        Most providers (Authentik, Authelia, Keycloak, Google, Entra ID, ...) send this claim already and are
        unaffected. See the OIDC docs for details:
        <br>
        <v-btn
          class="mt-2"
          color="primary"
          href="https://docs.mealie.io/documentation/getting-started/authentication/oidc-v2/#email-verification"
          target="_blank"
        >
          OpenID Connect (OIDC)
        </v-btn>
      </p>
    </div>
    <div v-else>
      <p>
        If you can no longer sign in with your external account, contact your server admin. They may need to
        update the server's OIDC configuration.
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
  title: "OIDC logins now require a verified email",
};
</script>

<style scoped lang="css">
p {
  padding-bottom: 8px;
}
</style>
