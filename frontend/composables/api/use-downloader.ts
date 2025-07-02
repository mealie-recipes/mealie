export function useDownloader() {
  function download(url: string, filename: string) {
    useFetch(url, {
      method: "GET",
      responseType: "blob",
      onResponse({ response }) {
        const url = window.URL.createObjectURL(new Blob([response._data]));
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", filename);
        document.body.appendChild(link);
        link.click();
      },
    });
  }

  return download;
}
