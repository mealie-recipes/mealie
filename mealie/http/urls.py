from typing import Any, cast

from asgiref.sync import async_to_sync
from django.http import HttpResponse
from django.urls import re_path
from rest_framework.decorators import api_view
from rest_framework.response import Response

from mealie.app import app, settings
from mealie.http.api import HTTPException
from mealie.http.routing import compile_path
from mealie.http.views import ControllerView

urlpatterns: list[Any] = []
by_path: dict[str, list[Any]] = {}
for route in app.routes:
    by_path.setdefault(route.path, []).append(route)
for path, routes in by_path.items():
    pattern = compile_path(path.lstrip("/"))
    view = cast(
        type[ControllerView], type("Mealie" + routes[0].name.title() + "View", (ControllerView,), {"routes": routes})
    )
    urlpatterns.append(re_path(pattern.pattern, view.as_view(), name=routes[0].name))


@api_view(["GET", "HEAD"])
def openapi(request: Any) -> Response:
    return Response(app.openapi())


urlpatterns.append(re_path(r"^openapi\.json$", openapi, name="openapi"))
if settings.DOCS_URL:

    @api_view(["GET", "HEAD"])
    def docs(request: Any) -> HttpResponse:
        return HttpResponse("""<!doctype html><html><head><title>Mealie API</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css"></head>
<body><div id="swagger-ui"></div><script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
<script>SwaggerUIBundle({url:'/openapi.json',dom_id:'#swagger-ui',persistAuthorization:true,oauth2RedirectUrl:window.location.origin+'/docs/oauth2-redirect'})</script></body></html>""")

    urlpatterns.append(re_path(r"^docs$", docs, name="docs"))

    @api_view(["GET", "HEAD"])
    def oauth_redirect(request: Any) -> HttpResponse:
        return HttpResponse("""<!doctype html><html><body><script>
const oauth=window.opener.swaggerUIRedirectOauth2;
const query=window.location.hash.substring(1)||window.location.search.substring(1);
const values=Object.fromEntries(new URLSearchParams(query));
if(values.state!==oauth.state){
oauth.errCb({authId:oauth.auth.name,source:'auth',level:'warning',message:'Authorization state mismatch'});
}
else {oauth.callback({auth:oauth.auth,redirectUrl:oauth.redirectUrl,token:values});}
window.close();</script></body></html>""")

    urlpatterns.append(re_path(r"^docs/oauth2-redirect$", oauth_redirect, name="oauth-redirect"))


@api_view(["GET", "HEAD"])
def redoc(request: Any) -> HttpResponse:
    return HttpResponse("""<!doctype html><html><head><title>Mealie - ReDoc</title></head>
<body><redoc spec-url="/openapi.json"></redoc>
<script src="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"></script></body></html>""")


urlpatterns.append(re_path(r"^redoc$", redoc, name="redoc"))


def handler500(request: Any) -> HttpResponse:
    return HttpResponse("Internal Server Error", status=500, content_type="text/plain; charset=utf-8")


def fallback(request: Any, path: str = "") -> HttpResponse:
    # Match the old router's slash redirects before considering the SPA shell.
    from mealie.http.responses import JSONResponse, RedirectResponse

    alternate = request.path.rstrip("/") if request.path.endswith("/") else request.path + "/"
    for pattern in urlpatterns[:-1]:
        if pattern.pattern.match(alternate.lstrip("/")):
            query = request.META.get("QUERY_STRING", "")
            return RedirectResponse(request.build_absolute_uri(alternate) + ("?" + query if query else ""))
    if settings.PRODUCTION and not settings.TESTING:
        from mealie.routes.spa import static_files

        if static_files:
            scope = {
                "method": request.method,
                "path": request.path,
                "query_string": request.META.get("QUERY_STRING", "").encode(),
                "headers": [(k.lower().encode(), v.encode()) for k, v in request.headers.items()],
            }
            try:
                response = async_to_sync(static_files.get_response)(path, scope)
                from mealie.http.files import prepare_file_response
                from mealie.http.responses import FileResponse

                if isinstance(response, FileResponse):
                    prepare_file_response(response, request)
                return response
            except HTTPException as exc:
                return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)
    return JSONResponse({"detail": "Not Found"}, status_code=404)


urlpatterns.append(re_path(r"^(?P<path>.*)$", fallback))
