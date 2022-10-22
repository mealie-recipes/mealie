import { useAsync, ref } from "@nuxtjs/composition-api";
import { useUserApi } from "~/composables/api";
import { UserIn, UserOut } from "~/lib/api/types/user";

/*
TODO: Potentially combine useAllUsers and useUser by delaying the get all users functionality
Unsure how this could work but still be clear and functional. Perhaps by passing arguments to the useUsers function
to control whether the object is substantiated... but some of the others rely on it being substantiated...Will come back to this.
*/

export const useAllUsers = function () {
  const api = useUserApi();
  const loading = ref(false);

  function getAllUsers() {
    loading.value = true;
    const asyncKey = String(Date.now());
    const allUsers = useAsync(async () => {
      const { data } = await api.users.getAll();
      if (data) {
        return data.items;
      } else {
        return null;
      }
    }, asyncKey);

    loading.value = false;
    return allUsers;
  }

  async function refreshAllUsers() {
    loading.value = true;
    const { data } = await api.users.getAll();

    if (data) {
      users.value = data.items;
    } else {
      users.value = null;
    }

    loading.value = false;
  }

  const users = getAllUsers();

  return { users, refreshAllUsers };
};

export const useUser = function (refreshFunc: CallableFunction | null = null) {
  const api = useUserApi();
  const loading = ref(false);

  function getUser(id: string) {
    loading.value = true;
    const user = useAsync(async () => {
      const { data } = await api.users.getOne(id);
      return data;
    }, id);

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
