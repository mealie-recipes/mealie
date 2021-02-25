import { store } from "@/store";
export const user = {
  data() {},
  computed: {
    user() {
      return store.getters.getUserData;
    },
    loggedIn() {
      return store.getters.getIsLoggedIn;
    },
  },
};
