from collections import defaultdict
from enum import Enum


class RequestBody(object):
    content = None
    description = str
    required = bool

    def __init__(self, content=None, description=None, required=True):
        self.content = content
        self.description = description
        self.required = required


class Parameter(object):
    schema = None
    location = None
    required = None
    description = None
    deprecated = None

    def __init__(self, schema, location='query', description=None, required=False, deprecated=False):
        self.schema = schema
        self.location = location
        self.description = description
        self.required = True if location == 'path' else required
        self.deprecated = deprecated


class Response(object):
    content = None
    description: str = None

    def __init__(self, content=None, description=None):
        self.content = content
        self.description = description


class Operation(object):
    id: str = None
    summary: str = None
    description: str = None
    tags: list = None
    body: RequestBody = None
    deprecated: bool = None
    responses = None
    parameters = None

    def __init__(self):
        self.tags = []
        self.responses = defaultdict(Response)
        self.parameters = defaultdict(Parameter)
        self.deprecated = False


operations = defaultdict(Operation)


def route(summary: str = None, description: str = None, id: str = None):
    def inner(func):
        route_spec = operations[func]

        if summary is not None:
            route_spec.summary = summary
        if description is not None:
            route_spec.description = description
        if id is not None:
            route_spec.id = id

        return func
    return inner


def summary(text: str):
    def inner(func):
        operations[func].summary = text
        return func
    return inner


def description(text: str):
    def inner(func):
        operations[func].description = text
        return func
    return inner


def tag(*args: str):
    def inner(func):
        for arg in args:
            operations[func].tags.append(arg)
        return func
    return inner


def deprecated():
    def inner(func):
        operations[func].deprecated = True
        return func
    return inner


def body(content=None, description=None, required=True):
    def inner(func):
        operations[func].body = RequestBody(content, description, required)
        return func
    return inner


def parameter(name, schema, location='query', description=None, required=False, deprecated=False):
    def inner(func):
        operations[func].parameters[name] = Parameter(schema, location, description, required, deprecated)
        return func
    return inner


def response(status, content=None, description=None):
    def inner(func):
        operations[func].responses[status] = Response(content, description)
        return func
    return inner