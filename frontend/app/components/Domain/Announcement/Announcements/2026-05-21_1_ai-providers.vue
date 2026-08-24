<template>
  <div>
    <p>AI providers can now be configured directly in Mealie, without managing environment variables or secrets.</p>
    <div class="mb-2">
      AI providers enable features such as:
      <ul class="ml-6">
        <li>Creating recipes from images</li>
        <li>Importing recipes from videos (YouTube, TikTok, etc.)</li>
        <li>Enhanced ingredient parsing</li>
        <li>And more!</li>
      </ul>
    </div>
    <hr class="mt-2 mb-4">
    <p>
      <span v-if="group?.aiProviderSettings?.aiEnabled">
        Your group already has AI providers configured.
      </span>
      <span v-else>
        Your group does not currently have any AI providers configured.
      </span>
      <span v-if="user?.canManage">
        You can manage them here:
        <br>
        <v-btn class="mt-2" color="primary" to="/group">
          {{ $t("profile.group-settings") }}
        </v-btn>
      </span>
      <span v-else-if="!group?.aiProviderSettings?.aiEnabled">
        Contact a group manager or server admin to set up AI providers for your group.
      </span>
    </p>
    <div v-if="user?.admin">
      <br>
      <p>
        As an admin, you can configure AI providers for any group. Unlike the old environment variable approach, providers are configured per-group:
        <br>
        <v-btn class="mt-2" color="primary" to="/admin/manage/groups">
          {{ $t("group.admin-group-management") }}
        </v-btn>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useGroupSelf } from "~/composables/use-groups";
import type { AnnouncementMeta } from "~/composables/use-announcements";

const { user } = useMealieAuth();
const { group } = useGroupSelf();
</script>

<script lang="ts">
export const meta: AnnouncementMeta = {
  title: "Improved AI Provider Configuration",
};
</script>

<style scoped lang="css">
p {
  padding-bottom: 8px;
}
</style>
