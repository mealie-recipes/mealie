import { alert } from "~/composables/use-toast";
import { useGlobalI18n } from "~/composables/use-global-i18n";

export function useDownloader() {
  /** Fetches `url` and saves it as `filename`. Resolves to false, after showing an error, if the request fails. */
  async function download(url: string, filename: string): Promise<boolean> {
    let blob: Blob;
    try {
      blob = await $fetch<Blob>(url, { responseType: "blob" });
    }
    catch (error) {
      console.error("Download failed", error);
      alert.error(useGlobalI18n().t("events.something-went-wrong"));
      return false;
    }

    const objectUrl = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = objectUrl;
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(objectUrl);
    return true;
  }

  return download;
}
