import axios from "axios";
import { alert } from "~/composables/use-toast";
const AXIOS_TIMEOUT = process.env.OPENAI_REQUEST_TIMEOUT || 10000;


export default defineNuxtPlugin(() => {
  const tokenName = useRuntimeConfig().public.AUTH_TOKEN;
  const axiosInstance = axios.create({
    baseURL: "/", // api calls already pass with /api
    timeout: AXIOS_TIMEOUT,
    headers: {
      Authorization: "Bearer " + useCookie(tokenName).value,
    },
    withCredentials: true,
  });

  // Add request interceptor
  axiosInstance.interceptors.request.use(
    (config) => {
      // You can add auth tokens or other headers here
      return config;
    },
    (error) => {
      return Promise.reject(error);
    },
  );

  // Add response interceptor
  axiosInstance.interceptors.response.use(
    (response) => {
      if (response?.data?.message) alert.info(response.data.message as string);
      return response;
    },
    (error) => {
      if (error?.response?.data?.detail?.message) alert.error(error.response.data.detail.message as string);
      return Promise.reject(error);
    },
  );

  return {
    provide: {
      axios: axiosInstance,
    },
  };
});
