import re
from enum import Enum

from humps import camelize
from pydantic import BaseModel, ConfigDict, Field
from slugify import slugify


class RouteObject:
    def __init__(self, route_string) -> None:
        self.prefix = "/" + route_string.split("/")[1]
        self.route = "/" + route_string.split("/", 2)[2]
        self.js_route = self.route.replace("{", "${")
        self.parts = route_string.split("/")[1:]
        self.var = re.findall(r"\{(.*?)\}", route_string)
        self.is_function = "{" in self.route
        self.router_slug = slugify("_".join(self.parts[1:]), separator="_")
        self.router_camel = camelize(self.router_slug)


class RequestType(str, Enum):
    get = "get"
    put = "put"
    post = "post"
    patch = "patch"
    delete = "delete"


class ParameterIn(str, Enum):
    query = "query"
    path = "path"
    header = "header"


class RouterParameter(BaseModel):
    model_config = ConfigDict(extra="allow")

    required: bool = False
    name: str
    location: ParameterIn = Field(..., alias="in")


class RequestBody(BaseModel):
    model_config = ConfigDict(extra="allow")

    required: bool = False


class HTTPRequest(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    request_type: RequestType
    description: str = ""
    summary: str
    request_body: RequestBody | None = None

    parameters: list[RouterParameter] = []
    tags: list[str] | None = []

    def list_as_js_object_string(self, parameters, braces=True):
        if len(parameters) == 0:
            return ""

        if braces:
            return "{" + ", ".join(parameters) + "}"
        else:
            return ", ".join(parameters)

    def payload(self):
        return "payload" if self.request_body else ""

    def function_args(self):
        all_params = [p.name for p in self.parameters]
        if self.request_body:
            all_params.append("payload")
        return self.list_as_js_object_string(all_params)

    def query_params(self):
        params = [param.name for param in self.parameters if param.location == ParameterIn.query]
        return self.list_as_js_object_string(params)

    def path_params(self):
        params = [param.name for param in self.parameters if param.location == ParameterIn.path]
        return self.list_as_js_object_string(parameters=params, braces=False)

    @property
    def summary_camel(self):
        return camelize(slugify(self.summary))

    @property
    def js_docs(self):
        return self.description.replace("\n", "  \n  * ")
