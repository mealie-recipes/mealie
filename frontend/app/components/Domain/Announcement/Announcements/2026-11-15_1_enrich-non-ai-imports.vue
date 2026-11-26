<template>
  <div>
    <p>
      AI can now enrich recipes that were imported without it. When a recipe is imported from a site Mealie
      can read on its own, your AI provider can fill in details the site doesn't provide, such as which
      ingredients each step uses and how long each step takes.
    </p>
    <p>
      This is off by default, and only runs for groups with an AI provider configured.
    </p>
    <hr class="mt-2 mb-4">
    <p v-if="user?.canManage">
      <span v-if="group?.aiProviderSettings?.aiEnabled">
        You can turn it on in the AI section of your group settings:
      </span>
      <span v-else>
        Your group does not currently have an AI provider configured. You can add one, and turn this on,
        in the AI section of your group settings:
      </span>
      <br>
      <v-btn class="mt-2" color="primary" to="/group">
        {{ $t("profile.group-settings") }}
      </v-btn>
    </p>
    <p v-else>
      Contact a group manager or server admin to turn this on for your group.
    </p>
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
  title: "Enrich Non-AI Imports",
};
</script>

<style scoped lang="css">
p {
  padding-bottom: 8px;
}
</style>
