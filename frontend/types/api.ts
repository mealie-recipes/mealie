import { AxiosResponse } from "axios";

interface RequestResponse<T> {
    response: AxiosResponse<T> | null;
    data: T | null;
    error: any;
  }

export interface ApiRequestInstance {
    get<T>(url: string, data?: T | object): Promise<RequestResponse<T>>;
    post<T>(url: string, data: T | object): Promise<RequestResponse<T>>;
    put<T>(url: string, data: T | object): Promise<RequestResponse<T>>;
    patch<T>(url: string, data: T | object): Promise<RequestResponse<T>>;
    delete<T>(url: string, data?: T | object): Promise<RequestResponse<T>>;
}

