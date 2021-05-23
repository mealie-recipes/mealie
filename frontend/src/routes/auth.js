const LoginPage = () => import("@/pages/LoginPage");
const SignUpPage = () => import("@/pages/SignUpPage");
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
