import re
from enum import Enum
from typing import Optional

from humps import camelize
from pydantic import BaseModel, Field
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


class RouterParameter(BaseModel):
    required: bool = False
    name: str
    location: ParameterIn = Field(..., alias="in")


class RequestBody(BaseModel):
    required: bool = False


class HTTPRequest(BaseModel):
    request_type: RequestType
    description: str = ""
    summary: str
    requestBody: Optional[RequestBody]

    parameters: list[RouterParameter] = []
    tags: list[str]

    def list_as_js_object_string(self, parameters, braces=True):
        if len(parameters) == 0:
            return ""

        if braces:
            return "{" + ", ".join(parameters) + "}"
        else:
            return ", ".join(parameters)

    def payload(self):
        return "payload" if self.requestBody else ""

    def function_args(self):
        all_params = [p.name for p in self.parameters]
        if self.requestBody:
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
