<template>
  <div>
    <p>
      Welcome to Mealie! If this is your first time seeing announcements, here's what to expect.
    </p>
    <div class="mb-2">
      Announcements are reserved for things like:
      <ul class="ml-6">
        <li>Important new features</li>
        <li>Major changes</li>
        <li>Anything that might require additional user actions (such as migration scripts)</li>
      </ul>
    </div>
    <p>
      While we generally keep everything in our <a class="text-primary" href="https://github.com/mealie-recipes/mealie/releases" target="_blank">GitHub release notes</a>,
      sometimes certain changes require some extra attention.
    </p>
    <p>
      Announcements are English-only; they're one-off messages from the maintainers, not a replacement for our release notes. Some elements may still be translated.
    </p>
    <hr class="mt-2 mb-4">
    <p>
      You can opt out of announcements in your user settings:
      <br>
      <v-btn class="mt-2" color="primary" to="/user/profile/edit">
        {{ $t("profile.user-settings") }}
      </v-btn>
    </p>
    <p v-if="user?.canManageHousehold" class="mt-3">
      As {{ user?.admin ? "an admin" : "a household manager" }}, you can disable announcements for your entire household:
      <br>
      <v-btn class="mt-2" color="primary" to="/household">
        {{ $t("profile.household-settings") }}
      </v-btn>
    </p>
    <p v-if="user?.canManage" class="mt-3">
      {{ user?.admin ? "You can also" : "As a group manager, you can" }} disable announcements for your entire group:
      <br>
      <v-btn class="mt-2" color="primary" to="/group">
        {{ $t("profile.group-settings") }}
      </v-btn>
    </p>
  </div>
</template>

<script setup lang="ts">
import type { AnnouncementMeta } from "~/composables/use-announcements";

const { user } = useMealieAuth();
</script>

<script lang="ts">
export const meta: AnnouncementMeta = {
  title: "Welcome to Mealie 🎉",
};
</script>

<style scoped lang="css">
p {
  padding-bottom: 8px;
}
</style>
