<template>
  <div>
    <p>
      You now need the <strong>Manage household</strong> permission to view or change notifiers and webhooks.
      Existing notifiers and webhooks keep running.
    </p>
    <p v-if="user?.canManage">
      You can turn this permission on for people in your household from the members page:
      <br>
      <v-btn class="mt-2" color="primary" to="/household/members">
        {{ $t("profile.manage-members") }}
      </v-btn>
    </p>
    <p v-else-if="!user?.canManageHousehold">
      If you need it, ask a group manager or your server admin.
    </p>
  </div>
</template>

<script setup lang="ts">
import type { AnnouncementMeta } from "~/composables/use-announcements";

const { user } = useMealieAuth();
</script>

<script lang="ts">
export const meta: AnnouncementMeta = {
  title: "Changes to notifiers and webhooks",
};
</script>

<style scoped lang="css">
p {
  padding-bottom: 8px;
}
</style>
