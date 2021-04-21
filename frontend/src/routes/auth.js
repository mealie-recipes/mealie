import LoginPage from "@/pages/LoginPage";
import SignUpPage from "@/pages/SignUpPage";
import { store } from "../store";

export const authRoutes = [
  {
    path: "/logout",
    beforeEnter: (_to, _from, next) => {
      store.commit("setToken", "");
      store.commit("setIsLoggedIn", false);
      next("/");
    },
  },
  { path: "/login", component: LoginPage },

  { path: "/sign-up", redirect: "/" },
  { path: "/sign-up/:token", component: SignUpPage },
];
