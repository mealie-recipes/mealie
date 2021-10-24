<template>
  <v-container class="narrow-container">
    <BasePageTitle divider>
      <template #header>
        <v-img max-height="125" max-width="125" :src="require('~/static/svgs/manage-tasks.svg')"></v-img>
      </template>
      <template #title> Background Tasks </template>
      Here you can view all the running background tasks and their status
    </BasePageTitle>
    <v-card-actions>
      <BaseButton color="info" :loading="loading" @click="refreshTasks">
        <template #icon> {{ $globals.icons.refresh }} </template>
        Refresh
      </BaseButton>
      <BaseButton color="info" @click="testTask">
        <template #icon> {{ $globals.icons.testTube }} </template>
        Test
      </BaseButton>
    </v-card-actions>
    <v-expansion-panels class="mt-2">
      <v-expansion-panel v-for="(task, i) in tasks" :key="i">
        <v-expansion-panel-header>
          <span>
            <v-progress-circular v-if="task.status === 'running'" indeterminate color="info"></v-progress-circular>
            <v-icon v-else-if="task.status === 'finished'" large color="success"> {{ $globals.icons.check }}</v-icon>
            <v-icon v-else-if="task.status === 'failed'" large color="error"> {{ $globals.icons.close }}</v-icon>
            <v-icon v-else-if="task.status === 'pending'" large color="gray"> {{ $globals.icons.pending }}</v-icon>
            <span class="ml-2">
              {{ task.name }}
            </span>
          </span>
          {{ $d(Date.parse(task.createdAt), "short") }}
        </v-expansion-panel-header>
        <v-expansion-panel-content style="white-space: pre-line">
          {{ task.log === "" ? "No Logs Found" : task.log }}
        </v-expansion-panel-content>
      </v-expansion-panel>
    </v-expansion-panels>
  </v-container>
</template>
    
<script lang="ts">
import { defineComponent, onMounted, ref } from "@nuxtjs/composition-api";
import { ServerTask } from "~/api/types/server-task";
import { useAdminApi } from "~/composables/use-api";

export default defineComponent({
  layout: "admin",
  setup() {
    const api = useAdminApi();

    const tasks = ref<ServerTask[]>([]);
    const loading = ref(false);

    async function refreshTasks() {
      loading.value = true;
      const { data } = await api.serverTasks.getAll();

      if (data) {
        tasks.value = data;
      }
      loading.value = false;
    }

    async function testTask() {
      await api.serverTasks.testTask();
      refreshTasks();
    }

    onMounted(async () => {
      await refreshTasks();
    });

    return {
      loading,
      refreshTasks,
      testTask,
      tasks,
    };
  },
  head() {
    return {
      title: "Tasks",
    };
  },
});
</script>