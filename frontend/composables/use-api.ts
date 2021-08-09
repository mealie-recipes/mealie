import { AxiosResponse } from "axios";
import { useContext } from "@nuxtjs/composition-api";
import { NuxtAxiosInstance } from "@nuxtjs/axios";
import { Api } from "~/api";
import { ApiRequestInstance } from "~/types/api";

interface RequestResponse<T> {
  response: AxiosResponse<T> | null;
  data: T | null;
  error: any;
}

const request = {
  async safe<T>(funcCall: any, url: string, data: object = {}): Promise<RequestResponse<T>> {
    const response = await funcCall(url, data).catch(function (error: object) {
      console.log(error);
      // Insert Generic Error Handling Here
      return { response: null, error, data: null };
    });
    return { response, error: null, data: response.data };
  },
};

function getRequests(axoisInstance: NuxtAxiosInstance): ApiRequestInstance {
  const requests = {
    async get<T>(url: string, params = {}): Promise<RequestResponse<T>> {
      let error = null;
      const response = await axoisInstance.get<T>(url, params).catch((e) => {
        error = e;
      });
      if (response != null) {
        return { response, error, data: response?.data };
      }
      return { response: null, error, data: null };
    },

    async post<T>(url: string, data: object) {
      return await request.safe<T>(axoisInstance.post, url, data);
    },

    async put<T>(url: string, data: object) {
      return await request.safe<T>(axoisInstance.put, url, data);
    },

    async patch<T>(url: string, data: object) {
      return await request.safe<T>(axoisInstance.patch, url, data);
    },

    async delete<T>(url: string) {
      return await request.safe<T>(axoisInstance.delete, url);
    },
  };
  return requests;
}

export const useApiSingleton = function (): Api {
  const { $axios } = useContext();
  const requests = getRequests($axios);

  return new Api(requests);
};
