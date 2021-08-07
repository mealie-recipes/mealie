import { useAsync, ref } from "@nuxtjs/composition-api";
import { set } from "@vueuse/core";
import { toastLoading, loader } from "./use-toast";
import { AllBackups, ImportBackup, BackupJob } from "~/api/class-interfaces/backups";
import { useApiSingleton } from "~/composables/use-api";

const backups = ref<AllBackups>({
  imports: [],
  templates: [],
});

function setBackups(newBackups: AllBackups | null) {
  if (newBackups) {
    set(backups, newBackups);
  }
}

export const useBackups = function (fetch = true) {
  const api = useApiSingleton();

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

  async function createBackup(payload: BackupJob | null = null) {
    if (payload === null) {
      payload = {
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
    loader.info("Creating Backup...");

    const { response } = await api.backups.createOne(payload);
    if (response && response.status === 201) {
      refreshBackups();
      toastLoading.open = false;
    }
  }

  async function deleteBackup(fileName: string) {
    const { response } = await api.backups.deleteOne(fileName);

    if (response && response.status === 200) {
      refreshBackups();
    }
  }

  async function importBackup(fileName: string, payload: ImportBackup) {
    loader.info("Import Backup...");
    const { response } = await api.backups.restoreDatabase(fileName, payload);

    if (response && response.status === 200) {
      refreshBackups();
      loader.close();
    }
  }

  if (fetch) {
    refreshBackups();
  }

  return { getBackups, refreshBackups, deleteBackup, backups, importBackup, createBackup };
};
