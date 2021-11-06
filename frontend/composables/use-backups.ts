import { useAsync, ref, reactive } from "@nuxtjs/composition-api";
import { set } from "@vueuse/core";
import { toastLoading, loader } from "./use-toast";
import { AllBackups, ImportBackup } from "~/api/class-interfaces/backups";
import { useUserApi } from "~/composables/api";

const backups = ref<AllBackups>({
  imports: [],
  templates: [],
});

function setBackups(newBackups: AllBackups | null) {
  if (newBackups) {
    set(backups, newBackups);
  }
}

function optionsFactory() {
  return {
    tag: "",
    templates: [],
    options: {
      recipes: true,
      settings: true,
      themes: true,
      pages: true,
      users: true,
      groups: true,
      notifications: true,
    },
  };
}

export const useBackups = function (fetch = true) {
  const api = useUserApi();

  const backupOptions = reactive(optionsFactory());
  const deleteTarget = ref("");

  const selected = ref<ImportBackup | null>({
    name: "",
    options: {
      recipes: true,
      settings: true,
      pages: true,
      themes: true,
      groups: true,
      users: true,
      notifications: true,
    },
  });

  function getBackups() {
    const backups = useAsync(async () => {
      const { data } = await api.backups.getAll();
      return data;
    });
    return backups;
  }

  async function refreshBackups() {
    const { data } = await api.backups.getAll();
    if (data) {
      setBackups(data);
    }
  }

  async function createBackup() {
    loader.info("Creating Backup...");
    const { response } = await api.backups.createOne(backupOptions);

    if (response && response.status === 201) {
      refreshBackups();
      toastLoading.open = false;
      Object.assign(backupOptions, optionsFactory());
    }
  }

  async function deleteBackup() {
    const { response } = await api.backups.deleteOne(deleteTarget.value);

    if (response && response.status === 200) {
      refreshBackups();
    }
  }

  async function importBackup() {
    loader.info("Import Backup...");

    if (!selected.value) {
      return;
    }

    const { response } = await api.backups.restoreDatabase(selected.value.name, selected.value.options);

    if (response && response.status === 200) {
      refreshBackups();
      loader.close();
    }
  }

  if (fetch) {
    refreshBackups();
  }

  return {
    getBackups,
    refreshBackups,
    deleteBackup,
    importBackup,
    createBackup,
    backups,
    backupOptions,
    deleteTarget,
    selected,
  };
};
