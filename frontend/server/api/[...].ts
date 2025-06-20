import { joinURL } from "ufo";

export default defineEventHandler(async (event) => {
  const apiUrl = useRuntimeConfig().apiUrl; // 'http://localhost:9000'

  const target = joinURL(apiUrl, event.path);
  if (event.path === "/api/auth/oauth") {
    return sendRedirect(event, target); // redirect to BE for Oauth login
  }

  return proxyRequest(event, target);
});
