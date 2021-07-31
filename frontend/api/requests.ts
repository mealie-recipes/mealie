import axios, { AxiosResponse } from "axios";

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

export const requests = {
  async get<T>(url: string, queryParams = {}): Promise<RequestResponse<T>> {
    let error = null;
    const response = await axios.get<T>(url, { params: { queryParams } }).catch((e) => {
      error = e;
    });
    if (response != null) {
      return { response, error, data: response?.data };
    }
    return { response: null, error, data: null };
  },

  async post<T>(url: string, data: object) {
    return await request.safe<T>(axios.post, url, data);
  },

  async put<T>(url: string, data: object) {
    return await request.safe<T>(axios.put, url, data);
  },

  async patch<T>(url: string, data: object) {
    return await request.safe<T>(axios.patch, url, data);
  },

  async delete<T>(url: string) {
    return await request.safe<T>(axios.delete, url);
  },
};
