import { useAdminApi, useUserApi } from "~/composables/api";
import type { AIPromptOverrideUpdate, AIPromptsOut, AIProviderCreate, AIProviderUpdate } from "~/lib/api/types/group";
import type { RequestResponse } from "~/lib/api/types/non-generated";

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

  async function testOne(payload: AIProviderCreate) {
    return await api.aiProviders.testOne(payload);
  }

  async function testSavedOne(id: string, overrides?: AIProviderUpdate & { apiKey?: string }) {
    return await api.aiProviders.testSavedOne(id, overrides);
  }

  return {
    loading: readonly(loading),
    getOne,
    createOne,
    updateOne,
    deleteOne,
    testOne,
    testSavedOne,
  };
}

/**
 * A group's AI prompt customizations. Pass a group id to manage another group's prompts as an admin,
 * otherwise the current user's group is used.
 */
export function useAIPrompts(groupId?: MaybeRefOrGetter<string | undefined>) {
  const isAdmin = groupId !== undefined;
  const userApi = useUserApi();
  const adminApi = useAdminApi();

  const prompts = ref<AIPromptsOut | null>(null);
  const loading = ref(false);

  async function run(
    userRequest: () => Promise<RequestResponse<AIPromptsOut>>,
    adminRequest: (id: string) => Promise<RequestResponse<AIPromptsOut>>,
  ) {
    let request = userRequest;
    if (isAdmin) {
      // Never fall back to the admin's own group while the target group is still loading
      const id = toValue(groupId);
      if (!id) {
        return null;
      }
      request = () => adminRequest(id);
    }

    loading.value = true;
    try {
      const { data } = await request();
      if (data) {
        prompts.value = data;
      }
      return data;
    }
    finally {
      loading.value = false;
    }
  }

  function refresh() {
    return run(
      () => userApi.aiProviders.getPrompts(),
      id => adminApi.aiProviders.getPrompts(id),
    );
  }

  function save(name: string, payload: AIPromptOverrideUpdate) {
    return run(
      () => userApi.aiProviders.updatePrompt(name, payload),
      id => adminApi.aiProviders.updatePrompt(id, name, payload),
    );
  }

  function reset(name: string) {
    return run(
      () => userApi.aiProviders.deletePrompt(name),
      id => adminApi.aiProviders.deletePrompt(id, name),
    );
  }

  return {
    prompts: readonly(prompts),
    loading: readonly(loading),
    refresh,
    save,
    reset,
  };
}
