from sanic_openapi3.types import Schema
from sanic_openapi3.definitions import Header, Example, Parameter, Response, RequestBody, SecurityScheme
from sanic_openapi3.main import components


def header(_name: str = None):
    def inner(cls: type):
        components.header(_name or cls.__name__, Header)
        return cls
    return inner


def example(_name: str = None, **kwargs):
    def inner(cls: type):
        components.example(_name or cls.__name__, Example.make(cls, **kwargs))
        return cls
    return inner


def parameter(_name: str = None, location: str = 'query', **kwargs):
    def inner(cls: type):
        name = _name or cls.__name__

        components.parameter(name, Parameter.make(name, cls, location, **kwargs))
        return cls
    return inner


def response(_name: str = None, **kwargs):
    def inner(cls: type):
        components.response(_name or cls.__name__, Response.make(cls, **kwargs))
        return cls
    return inner


def body(_name: str = None, **kwargs):
    def inner(cls: type):
        components.body(_name or cls.__name__, RequestBody.make(cls, **kwargs))
        return cls
    return inner


def scheme(_name: str = None):
    def inner(cls):
        components.schema(_name or cls.__name__, Schema.make(cls))
        return cls
    return inner


def security(_type: str, _name: str = None, **kwargs):
    def inner(cls: type):
        components.security(_name or cls.__name__, SecurityScheme.make(_type, cls, **kwargs))
        return cls
    return inner
