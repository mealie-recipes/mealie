import { useAdminApi } from "~/composables/api";
import type { UserIn, UserOut } from "~/lib/api/types/user";

/*
TODO: Potentially combine useAllUsers and useUser by delaying the get all users functionality
Unsure how this could work but still be clear and functional. Perhaps by passing arguments to the useUsers function
to control whether the object is substantiated... but some of the others rely on it being substantiated...Will come back to this.
*/

export const useAllUsers = function () {
  const api = useAdminApi();
  const asyncKey = String(Date.now());
  const { data: users, refresh: refreshAllUsers } = useLazyAsyncData(asyncKey, async () => {
    const { data } = await api.users.getAll();
    if (data) {
      return data.items;
    }
    else {
      return null;
    }
  });

  return { users, refreshAllUsers };
};

export const useUser = function (refreshFunc: CallableFunction | null = null) {
  const api = useAdminApi();
  const loading = ref(false);

  function getUser(id: string) {
    loading.value = true;
    const user = useAsyncData(id, async () => {
      const { data } = await api.users.getOne(id);
      return data;
    });

    loading.value = false;
    return user;
  }

  async function createUser(payload: UserIn) {
    loading.value = true;
    const { data } = await api.users.createOne(payload);

    console.log(payload, data);

    if (refreshFunc) {
      refreshFunc();
    }

    loading.value = false;
    return data;
  }

  async function deleteUser(id: string) {
    loading.value = true;
    const { data } = await api.users.deleteOne(id);
    loading.value = false;

    if (refreshFunc) {
      refreshFunc();
    }

    return data;
  }

  async function updateUser(itemId: string, user: UserOut) {
    loading.value = true;
    const { data } = await api.users.updateOne(itemId, user);
    loading.value = false;

    if (refreshFunc) {
      refreshFunc();
    }

    return data;
  }

  return { loading, getUser, deleteUser, updateUser, createUser };
};
