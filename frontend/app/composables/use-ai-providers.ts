import { useUserApi } from "~/composables/api";
import type { AIProviderCreate, AIProviderUpdate } from "~/lib/api/types/group";

export function useAIProviders() {
  const api = useUserApi();
  const loading = ref(false);

  async function getOne(id: string) {
    loading.value = true;
    try {
      return await api.aiProviders.getOne(id);
    }
    finally {
      loading.value = false;
    }
  }

  async function createOne(payload: AIProviderCreate) {
    loading.value = true;
    try {
      return await api.aiProviders.createOne(payload);
    }
    finally {
      loading.value = false;
    }
  }

  async function updateOne(id: string, payload: AIProviderUpdate) {
    loading.value = true;
    try {
      return await api.aiProviders.updateOne(id, payload);
    }
    finally {
      loading.value = false;
    }
  }

  async function deleteOne(id: string) {
    loading.value = true;
    try {
      return await api.aiProviders.deleteOne(id);
    }
    finally {
      loading.value = false;
    }
  }

  return {
    loading: readonly(loading),
    getOne,
    createOne,
    updateOne,
    deleteOne,
  };
}
