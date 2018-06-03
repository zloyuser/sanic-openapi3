import json

from datetime import date, datetime, time
from typing import List, Dict, Any, get_type_hints


class Definition:
    __fields: dict

    def __init__(self, **kwargs):
        self.__fields = self.guard(kwargs)

    @property
    def fields(self) -> Dict[str, Any]:
        return self.__fields

    def guard(self, fields: Dict[str, Any])-> Dict[str, Any]:
        properties = props(self).keys()

        return {x: v for x, v in fields.items() if x in properties}

    def serialize(self):
        return serialize(self.fields)

    def __str__(self):
        return json.dumps(self.serialize())


class Schema(Definition):
    type: str
    format: str
    description: str
    nullable: False
    default: None
    example: None
    oneOf: List[Definition]
    anyOf: List[Definition]
    allOf: List[Definition]


class Boolean(Schema):
    def __init__(self, **kwargs):
        super().__init__(type="boolean", **kwargs)


class Integer(Schema):
    def __init__(self, **kwargs):
        super().__init__(type="integer", format="int32", **kwargs)


class Long(Schema):
    def __init__(self, **kwargs):
        super().__init__(type="integer", format="int64", **kwargs)


class Float(Schema):
    def __init__(self, **kwargs):
        super().__init__(type="number", format="float", **kwargs)


class Double(Schema):
    def __init__(self, **kwargs):
        super().__init__(type="number", format="double", **kwargs)


class String(Schema):
    def __init__(self, **kwargs):
        super().__init__(type="string", **kwargs)


class Byte(Schema):
    def __init__(self, **kwargs):
        super().__init__(type="string", format="byte", **kwargs)


class Binary(Schema):
    def __init__(self, **kwargs):
        super().__init__(type="string", format="binary", **kwargs)


class Date(Schema):
    def __init__(self, **kwargs):
        super().__init__(type="string", format="date", **kwargs)


class Time(Schema):
    def __init__(self, **kwargs):
        super().__init__(type="string", format="time", **kwargs)


class DateTime(Schema):
    def __init__(self, **kwargs):
        super().__init__(type="string", format="date-time", **kwargs)


class Password(Schema):
    def __init__(self, **kwargs):
        super().__init__(type="string", format="password", **kwargs)


class Email(Schema):
    def __init__(self, **kwargs):
        super().__init__(type="string", format="email", **kwargs)


class Object(Schema):
    properties: Dict[str, Schema]

    def __init__(self, properties: Dict[str, Schema]=None, **kwargs):
        super().__init__(type="object", properties=properties or {}, **kwargs)


class Array(Schema):
    items: Schema

    def __init__(self, items: Schema, **kwargs):
        super().__init__(type="array", items=items, **kwargs)


def serialize(value) -> Any:
    if isinstance(value, Definition):
        return value.serialize()

    if isinstance(value, dict):
        return {k: serialize(v) for k, v in value.items()}

    if isinstance(value, list):
        return [serialize(v) for v in value]

    return value


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


def props(value: Any) -> Dict[str, Any]:
    fields = {x: v for x, v in value.__dict__.items() if not x.startswith('_')}

    return {**get_type_hints(value.__class__), **fields}


def scheme(value: Any) -> Schema:
    def __recur(fields: Dict):
        return {k: scheme(v) for k, v in fields.items()}

    if isinstance(value, Schema):
        return value

    if value == bool:
        return Boolean()
    elif value == int:
        return Integer()
    elif value == float:
        return Float()
    elif value == str:
        return String()
    elif value == bytes:
        return Byte()
    elif value == bytearray:
        return Binary()
    elif value == date:
        return Date()
    elif value == time:
        return Time()
    elif value == datetime:
        return DateTime()

    _type = type(value)

    if _type == bool:
        return Boolean(default=value)
    elif _type == int:
        return Integer(default=value)
    elif _type == float:
        return Float(default=value)
    elif _type == str:
        return String(default=value)
    elif _type == bytes:
        return Byte(default=value)
    elif _type == bytearray:
        return Binary(default=value)
    elif _type == date:
        return Date()
    elif _type == time:
        return Time()
    elif _type == datetime:
        return DateTime()
    elif _type == list:
        if len(value) == 0:
            schema = Schema(nullable=True)
        elif len(value) == 1:
            schema = scheme(value[0])
        else:
            schema = Schema(oneOf=[scheme(x) for x in value])

        return Array(schema)
    elif _type == dict:
        return Object(__recur(value))
    else:
        return Object(__recur(props(value)))


def media(value: Any) -> Dict[str, MediaType]:
    media_types = value

    if value is not dict:
        media_types = {'*/*': value or {}}

    return {x: MediaType(scheme(v)) for x, v in media_types.items()}
