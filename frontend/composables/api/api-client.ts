import { AxiosResponse } from "axios";
import { useContext } from "@nuxtjs/composition-api";
import type { NuxtAxiosInstance } from "@nuxtjs/axios";
import { ApiRequestInstance, RequestResponse } from "~/lib/api/types/non-generated";
import { AdminAPI, PublicApi, UserApi } from "~/lib/api";
import { PublicExploreApi } from "~/lib/api/client-public";

const request = {
  async safe<T, U>(
    funcCall: (url: string, data: U) => Promise<AxiosResponse<T>>,
    url: string,
    data: U
  ): Promise<RequestResponse<T>> {
    let error = null;
    const response = await funcCall(url, data).catch(function (e) {
      console.log(e);
      // Insert Generic Error Handling Here
      error = e;
      return null;
    });
    return { response, error, data: response?.data ?? null };
  },
};

function getRequests(axiosInstance: NuxtAxiosInstance): ApiRequestInstance {
  return {
    async get<T>(url: string, params = {}): Promise<RequestResponse<T>> {
      let error = null;
      const response = await axiosInstance.get<T>(url, params).catch((e) => {
        error = e;
      });
      if (response != null) {
        return { response, error, data: response?.data };
      }
      return { response: null, error, data: null };
    },

    async post<T, U>(url: string, data: U) {
      // eslint-disable-next-line @typescript-eslint/unbound-method
      return await request.safe<T, U>(axiosInstance.post, url, data);
    },

    async put<T, U = T>(url: string, data: U) {
      // eslint-disable-next-line @typescript-eslint/unbound-method
      return await request.safe<T, U>(axiosInstance.put, url, data);
    },

    async patch<T, U = Partial<T>>(url: string, data: U) {
      // eslint-disable-next-line @typescript-eslint/unbound-method
      return await request.safe<T, U>(axiosInstance.patch, url, data);
    },

    async delete<T>(url: string) {
      // eslint-disable-next-line @typescript-eslint/unbound-method
      return await request.safe<T, undefined>(axiosInstance.delete, url, undefined);
    },
  };
}

export const useRequests = function (): ApiRequestInstance {
  const { $axios, i18n } = useContext();

  $axios.setHeader("Accept-Language", i18n.locale);

  return getRequests($axios);
};

export const useAdminApi = function (): AdminAPI {
  const requests = useRequests();
  return new AdminAPI(requests);
};

export const useUserApi = function (): UserApi {
  const requests = useRequests();
  return new UserApi(requests);
};

export const usePublicApi = function (): PublicApi {
  const requests = useRequests();
  return new PublicApi(requests);
};

export const usePublicExploreApi = function (groupSlug: string): PublicExploreApi {
  const requests = useRequests();
  return new PublicExploreApi(requests, groupSlug);
}
