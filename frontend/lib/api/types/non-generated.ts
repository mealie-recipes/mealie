import { AxiosResponse } from "axios";

export type NoUndefinedField<T> = { [P in keyof T]-?: NoUndefinedField<NonNullable<T[P]>> };

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

export interface PaginationData<T> {
  page: number;
  per_page: number;
  total: number;
  total_pages: number;
  items: T[];
}

export type RecipeOrganizer =
  | "categories"
  | "tags"
  | "tools"
  | "foods"
  | "households";

export enum Organizer {
  Category = "categories",
  Tag = "tags",
  Tool = "tools",
  Food = "foods",
  Household = "households",
}
