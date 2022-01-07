import { AxiosResponse } from "axios";

export interface RequestResponse<T> {
  response: AxiosResponse<T> | null;
  data: T | null;
  error: any;
}

export interface ApiRequestInstance {
  get<T>(url: string, data?: unknown): Promise<RequestResponse<T>>;
  post<T>(url: string, data: unknown): Promise<RequestResponse<T>>;
  put<T, U = T>(url: string, data: U): Promise<RequestResponse<T>>;
  patch<T, U = Partial<T>>(url: string, data: U): Promise<RequestResponse<T>>;
  delete<T>(url: string): Promise<RequestResponse<T>>;
}
