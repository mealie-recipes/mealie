import { useContext } from "@nuxtjs/composition-api";

export function useAxiosDownloader() {
  const { $axios } = useContext();

  function download(url: string, filename: string) {
    $axios({
      url,
      method: "GET",
      responseType: "blob",
    }).then((response) => {
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
    });
  }

  return download;
}
