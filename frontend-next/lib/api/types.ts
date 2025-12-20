export type RequestResponse<T> = T;

export interface ApiRequestConfig extends RequestInit {
  timeoutMs?: number;
  retries?: number;
  next?: NextFetchRequestConfig;
  responseType?: "json" | "text" | "blob";
}

export interface ApiRequestInstance {
  get<T>(url: string, config?: ApiRequestConfig): Promise<RequestResponse<T>>;
  post<T>(
    url: string,
    data?: unknown,
    config?: ApiRequestConfig
  ): Promise<RequestResponse<T>>;
  put<T>(
    url: string,
    data: unknown,
    config?: ApiRequestConfig
  ): Promise<RequestResponse<T>>;
  patch<T>(
    url: string,
    data: unknown,
    config?: ApiRequestConfig
  ): Promise<RequestResponse<T>>;
  delete<T>(
    url: string,
    config?: ApiRequestConfig
  ): Promise<RequestResponse<T>>;
}

export interface PaginationData<T> {
  page: number;
  per_page: number;
  total: number;
  total_pages: number;
  items: T[];
}
