from typing import List, Dict, Any
from sanic_openapi3.types import Definition, Schema


class Contact(Definition):
    name: str
    url: str
    email: str


class License(Definition):
    name: str
    url: str

    def __init__(self, name: str, **kwargs):
        super().__init__(name=name, **kwargs)


class Info(Definition):
    title: str
    description: str
    termsOfService: str
    contact: Contact
    license: License
    version: str

    def __init__(self, title: str, version: str, **kwargs):
        super().__init__(title=title, version=version, **kwargs)


class Example(Definition):
    summary: str
    description: str
    value: Any
    externalValue: str  # TODO

    def __init__(self, value: Any, **kwargs):
        super().__init__(value=value, **kwargs)


class MediaType(Definition):
    schema: Schema
    example: Any

    def __init__(self, schema: Schema, **kwargs):
        super().__init__(schema=schema, **kwargs)


class Response(Definition):
    content: Dict[str, MediaType]
    description: str

    def __init__(self, content=None, **kwargs):
        super().__init__(content=content, **kwargs)


class RequestBody(Definition):
    description: str
    required: bool
    content: Dict[str, MediaType]

    def __init__(self, content: Dict[str, MediaType], **kwargs):
        super().__init__(content=content, **kwargs)


class ExternalDocumentation(Definition):
    name: str
    url: str

    def __init__(self, url: str, **kwargs):
        super().__init__(url=url, **kwargs)


class Parameter(Definition):
    name: str
    location: str
    description: str
    required: bool
    deprecated: bool
    allowEmptyValue: bool
    schema: Schema

    def __init__(self, name, schema: Schema, location='query', **kwargs):
        super().__init__(name=name, schema=schema, location=location, **kwargs)

    @property
    def fields(self):
        values = super().fields

        values['in'] = values.pop('location')

        return values


class Operation(Definition):
    tags: List[str]
    summary: str
    description: str
    operationId: str
    requestBody: RequestBody
    externalDocs: ExternalDocumentation
    parameters: List[Parameter]
    responses: Dict[str, Response]
    security: Dict[str, List[str]]
    callbacks: List[str]  # TODO
    deprecated: bool


class PathItem(Definition):
    summary: str
    description: str
    get: Operation
    put: Operation
    post: Operation
    delete: Operation
    options: Operation
    head: Operation
    patch: Operation
    trace: Operation


class Components(Definition):
    schemas: Dict[str, Schema]
    responses: Dict[str, Response]
    parameters: Dict[str, Parameter]
    examples: Dict[str, Example]
    requestBodies: Dict[str, RequestBody]
    headers: Dict[str, Schema]  # TODO
    securitySchemes: Dict[str, Schema]  # TODO
    links: Dict[str, Schema]  # TODO
    callbacks: Dict[str, Schema]  # TODO


class Tag(Definition):
    name: str
    description: str
    externalDocs: ExternalDocumentation

    def __init__(self, name: str, **kwargs):
        super().__init__(name=name, **kwargs)


class OpenAPI(Definition):
    openapi: str
    info: Info
    servers: []  # TODO
    paths: Dict[str, PathItem]
    components: Components
    security: Dict[str, Any]
    tags: List[Tag]
    externalDocs: ExternalDocumentation

    def __init__(self, info: Info, paths: Dict[str, PathItem], **kwargs):
        super().__init__(openapi="3.0.0", info=info, paths=paths, **kwargs)
