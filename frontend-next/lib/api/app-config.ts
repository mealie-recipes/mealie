import type { AppConfig } from "@/lib/types/app-config";

/**
 * Fetches application configuration from the backend
 * @returns Promise with AppConfig data
 */
export async function fetchAppConfig(): Promise<AppConfig> {
  const response = await fetch("/api/app/about", {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
    cache: "no-store", // Always fetch fresh config
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch app config: ${response.statusText}`);
  }

  return response.json();
}
