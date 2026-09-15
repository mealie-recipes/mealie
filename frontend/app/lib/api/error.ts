export function getApiErrorMessage(error: unknown): string | null {
  if (typeof error !== "object" || error === null || !("response" in error)) {
    return null;
  }

  const response = error.response;
  if (typeof response !== "object" || response === null || !("data" in response)) {
    return null;
  }

  const data = response.data;
  if (typeof data !== "object" || data === null || !("detail" in data)) {
    return null;
  }

  const detail = data.detail;
  if (typeof detail === "string") {
    return detail;
  }

  if (typeof detail === "object" && detail !== null && "message" in detail && typeof detail.message === "string") {
    return detail.message;
  }

  return null;
}
