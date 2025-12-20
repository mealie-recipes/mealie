export const METHODS = {
  GET: "GET",
  POST: "POST",
  PUT: "PUT",
  DELETE: "DELETE",
  PATCH: "PATCH",
};

export type HttpMethod = (typeof METHODS)[keyof typeof METHODS];

export const isHttpMethod = (method: string): method is HttpMethod => {
  return Object.values(METHODS).includes(method as HttpMethod);
};
