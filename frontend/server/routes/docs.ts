import { joinURL } from "ufo";

export default defineEventHandler(async (event) => {
  const apiUrl = useRuntimeConfig().apiUrl; // 'http://localhost:9000'

  const target = joinURL(apiUrl, event.path);

  return proxyRequest(event, target);
});
