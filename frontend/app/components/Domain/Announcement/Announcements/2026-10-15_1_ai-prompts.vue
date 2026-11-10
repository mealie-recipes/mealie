<template>
  <div>
    <p>
      The instructions Mealie gives your AI provider can now be customized directly in Mealie. Add your own
      instructions to every prompt at once (for example, "always use metric units"), add to a single prompt,
      or replace one entirely.
    </p>
    <p v-if="user?.canManage">
      You can customize them in the AI section of your group settings:
      <br>
      <v-btn class="mt-2" color="primary" to="/group">
        {{ $t("profile.group-settings") }}
      </v-btn>
    </p>
    <p v-else>
      Contact a group manager or server admin to customize the prompts for your group.
    </p>
    <div v-if="user?.admin">
      <hr class="mt-2 mb-4">
      <p>
        Custom prompts used to be configured with prompt files and the <code>OPENAI_CUSTOM_PROMPT_DIR</code>
        environment variable. If you had any, they were imported into every group as part of this update,
        so the folder and the variable can now be removed. They're no longer used.
      </p>
      <p>
        As an admin, you can also customize prompts for any group:
        <br>
        <v-btn class="mt-2" color="primary" to="/admin/manage/groups">
          {{ $t("group.admin-group-management") }}
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
  title: "Custom AI Prompts",
};
</script>

<style scoped lang="css">
p {
  padding-bottom: 8px;
}
</style>
