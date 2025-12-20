import { baseRequest } from "@/lib/http/base-request";
import {
  ApiRequestConfig,
  ApiRequestInstance,
  RequestResponse,
} from "../types";

export class ApiRequestAdapter implements ApiRequestInstance {
  async get<T>(
    url: string,
    config?: ApiRequestConfig
  ): Promise<RequestResponse<T>> {
    return this.request<T>(url, { ...config, method: "GET" });
  }

  async post<T>(
    url: string,
    data?: unknown,
    config?: ApiRequestConfig
  ): Promise<RequestResponse<T>> {
    return this.request<T>(url, { ...config, method: "POST" }, data);
  }

  async put<T>(
    url: string,
    data: unknown,
    config?: ApiRequestConfig
  ): Promise<RequestResponse<T>> {
    return this.request<T>(url, { ...config, method: "PUT" }, data);
  }

  async patch<T>(
    url: string,
    data: unknown,
    config?: ApiRequestConfig
  ): Promise<RequestResponse<T>> {
    return this.request<T>(url, { ...config, method: "PATCH" }, data);
  }

  async delete<T>(
    url: string,
    config?: ApiRequestConfig
  ): Promise<RequestResponse<T>> {
    return this.request<T>(url, { ...config, method: "DELETE" });
  }

  private async request<T>(
    path: string,
    config: ApiRequestConfig,
    data?: unknown
  ): Promise<T> {
    const { timeoutMs, retries, ...fetchInit } = config;
    const headers = new Headers(fetchInit.headers);

    let body: BodyInit | null | undefined = undefined;

    if (data !== undefined && data !== null) {
      if (headers.has("Content-Type")) {
        // 1. Handle application/x-www-form-urlencoded
        if (headers.get("Content-Type")?.includes("x-www-form-urlencoded")) {
          body = new URLSearchParams(data as Record<string, string>).toString();
        } else {
          body = data as BodyInit;
        }
      }
      // 2. FormData (File Uploads)
      else if (data instanceof FormData) {
        headers.delete("Content-Type"); // Let fetch handle boundary
        body = data;
      }
      // 3. URLSearchParams (detected safely)
      else if (data instanceof URLSearchParams) {
        // Explicitly set the header to ensure consistency
        headers.set("Content-Type", "application/x-www-form-urlencoded");
        body = data.toString();
      }
      // 4. Default: JSON
      else {
        headers.set("Content-Type", "application/json");
        body = JSON.stringify(data);
      }
    }

    return baseRequest<T>(
      path,
      { ...fetchInit, headers, body },
      { timeoutMs, retries }
    );
  }
}

export const apiRequest = new ApiRequestAdapter();
