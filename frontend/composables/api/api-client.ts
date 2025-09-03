import type { AxiosInstance, AxiosResponse, AxiosRequestConfig } from "axios";
import type { Composer } from "vue-i18n";
import type { ApiRequestInstance, RequestResponse } from "~/lib/api/types/non-generated";
import { AdminAPI, PublicApi, UserApi } from "~/lib/api";
import { PublicExploreApi } from "~/lib/api/client-public";
import { useGlobalI18n } from "~/composables/use-global-i18n";

const request = {
  async safe<T, U>(
    funcCall: (url: string, data: U, config?: AxiosRequestConfig) => Promise<AxiosResponse<T>>,
    url: string,
    data: U,
    config?: AxiosRequestConfig,
  ): Promise<RequestResponse<T>> {
    let error = null;
    const response = await funcCall(url, data, config).catch(function (e) {
      console.log(e);
      // Insert Generic Error Handling Here
      error = e;
      return null;
    });
    return { response, error, data: response?.data ?? null };
  },
};

function getRequests(axiosInstance: AxiosInstance): ApiRequestInstance {
  return {
    async get<T>(url: string, params = {}, config?: AxiosRequestConfig): Promise<RequestResponse<T>> {
      let error = null;
      const response = await axiosInstance.get<T>(url, { ...config, params }).catch((e) => {
        error = e;
      });
      if (response != null) {
        return { response, error, data: response?.data };
      }
      return { response: null, error, data: null };
    },

    async post<T, U>(url: string, data: U, config?: AxiosRequestConfig) {
      return await request.safe<T, U>(axiosInstance.post, url, data, config);
    },

    async put<T, U = T>(url: string, data: U, config?: AxiosRequestConfig) {
      return await request.safe<T, U>(axiosInstance.put, url, data, config);
    },

    async patch<T, U = Partial<T>>(url: string, data: U, config?: AxiosRequestConfig) {
      return await request.safe<T, U>(axiosInstance.patch, url, data, config);
    },

    async delete<T>(url: string, config?: AxiosRequestConfig) {
      return await request.safe<T, undefined>(axiosInstance.delete, url, undefined, config);
    },
  };
}

export const useRequests = function (i18n?: Composer): ApiRequestInstance {
  const { $axios } = useNuxtApp();
  if (!i18n) {
    i18n = useGlobalI18n();
  }

  $axios.defaults.headers.common["Accept-Language"] = i18n.locale.value;

  return getRequests($axios);
};

export const useAdminApi = function (i18n?: Composer): AdminAPI {
  const requests = useRequests(i18n);
  return new AdminAPI(requests);
};

export const useUserApi = function (i18n?: Composer): UserApi {
  const requests = useRequests(i18n);
  return new UserApi(requests);
};

export const usePublicApi = function (i18n?: Composer): PublicApi {
  const requests = useRequests(i18n);
  return new PublicApi(requests);
};

export const usePublicExploreApi = function (groupSlug: string, i18n?: Composer): PublicExploreApi {
  const requests = useRequests(i18n);
  return new PublicExploreApi(requests, groupSlug);
};
