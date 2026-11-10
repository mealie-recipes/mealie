<template>
  <div>
    <p>
      You now need the <strong>Organize group data</strong> permission to add, edit, or delete units, tools,
      labels, and recipe actions. This was already the case for foods, tags, and categories.
    </p>
    <p>
      Without it, you can still pick existing units and tools on your recipes. You just can't make new ones,
      including from the recipe editor or a shopping list.
    </p>
    <p v-if="user?.canManage">
      You can turn this permission on for people in your household from the members page:
      <br>
      <v-btn class="mt-2" color="primary" to="/household/members">
        {{ $t("profile.manage-members") }}
      </v-btn>
    </p>
    <p v-else-if="!user?.canOrganize">
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
  title: "Changes to the Organize permission",
};
</script>

<style scoped lang="css">
p {
  padding-bottom: 8px;
}
</style>
