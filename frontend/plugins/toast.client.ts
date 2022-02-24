import { Plugin } from "@nuxt/types";
import { NuxtAxiosInstance } from "@nuxtjs/axios";
import { alert } from "~/composables/use-toast";

const toastPlugin: Plugin = ({ $axios }: { $axios: NuxtAxiosInstance }) => {
  $axios.onResponse((response) => {
    if (response?.data?.message) {
      alert.info(response.data.message);
    }
  });
  $axios.onError((error) => {
    if (error.response?.data?.detail?.message) {
      alert.error(error.response.data.detail.message);
    }
  });
};

export default toastPlugin;
