import re

from collections import defaultdict
from itertools import repeat
from sanic import Sanic
from sanic.views import CompositionView
from sanic_openapi3.definitions import *


class OperationBuilder:
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
    deprecated: bool = False

    def __init__(self):
        self.responses = {}
        self.parameters = []
        self.tags = []


class SpecificationBuilder:
    operations: Dict[Any, OperationBuilder]
    schemes: Dict[Any, Definition]

    def __init__(self):
        self.operations = defaultdict(OperationBuilder)

    def build(self, app: Sanic) -> OpenAPI:
        info = self.build_info(app)
        paths = defaultdict(dict)
        tags = {}

        # --------------------------------------------------------------- #
        # Blueprints
        # --------------------------------------------------------------- #
        for _blueprint in app.blueprints.values():
            if not hasattr(_blueprint, 'routes'):
                continue

            for _route in _blueprint.routes:
                if _route.handler not in self.operations:
                    continue

                operation = self.operations.get(_route.handler)

                if not operation.tags:
                    operation.tags.append(_blueprint.name)

        # --------------------------------------------------------------- #
        # Operations
        # --------------------------------------------------------------- #
        for _uri, _route in app.router.routes_all.items():
            if '<file_uri' in _uri:
                continue

            handler_type = type(_route.handler)

            if handler_type is CompositionView:
                view = _route.handler
                method_handlers = view.handlers.items()
            else:
                method_handlers = zip(_route.methods, repeat(_route.handler))

            uri = _uri if _uri == "/" else _uri.rstrip('/')

            for segment in _route.parameters:
                uri = re.sub('<' + segment.name + '.*?>', '{' + segment.name + '}', uri)

            for _method, _handler in method_handlers:
                if _handler not in self.operations:
                    continue

                operation = self.operations[_handler]

                if not hasattr(operation, 'operationId'):
                    operation.operationId = '%s_%s' % (_method.lower(), _route.name)

                for _parameter in _route.parameters:
                    operation.parameters.append(Parameter(
                        _parameter.name, scheme(_parameter.cast), 'path', required=True
                    ))

                paths[uri][_method] = operation.__dict__

        paths = {k: PathItem(**{k1.lower(): Operation(**v1) for k1, v1 in v.items()}) for k, v in paths.items()}

        # --------------------------------------------------------------- #
        # Tags
        # --------------------------------------------------------------- #
        for operation in self.operations.values():
            for _tag in operation.tags:
                tags[_tag] = True

        # --------------------------------------------------------------- #
        # Definitions
        # --------------------------------------------------------------- #

        # for key, definitions in components.items():
        #     for cls, definition in definitions.items():
        #         _spec['components'][key][cls] = definition

        return OpenAPI(info, paths, tags=[{"name": name} for name in tags.keys()])

    @staticmethod
    def build_info(app: Sanic) -> Info:
        title = getattr(app.config, 'OPENAPI_TITLE', 'API')
        version = getattr(app.config, 'OPENAPI_VERSION', '1.0.0')
        description = getattr(app.config, 'OPENAPI_DESCRIPTION', None)
        terms = getattr(app.config, 'OPENAPI_TERMS_OF_SERVICE', None)

        license_name = getattr(app.config, 'OPENAPI_LICENSE_NAME', None)
        license_url = getattr(app.config, 'OPENAPI_LICENSE_URL', None)
        license = License(license_name, url=license_url)

        contact_name = getattr(app.config, 'OPENAPI_CONTACT_NAME', None)
        contact_url = getattr(app.config, 'OPENAPI_CONTACT_URL', None)
        contact_email = getattr(app.config, 'OPENAPI_CONTACT_EMAIL', None)
        contact = Contact(name=contact_name, url=contact_url, email=contact_email)

        return Info(title, version, description=description, termsOfService=terms, license=license, contact=contact)


spec = SpecificationBuilder()


def summary(text: str):
    def inner(func):
        spec.operations[func].summary = text
        return func
    return inner


def description(text: str):
    def inner(func):
        spec.operations[func].description = text
        return func
    return inner


def tag(*args: str):
    def inner(func):
        for arg in args:
            spec.operations[func].tags.append(arg)
        return func
    return inner


def deprecated():
    def inner(func):
        spec.operations[func].deprecated = True
        return func
    return inner


def body(content: Any, **kwargs):
    def inner(func):
        spec.operations[func].requestBody = RequestBody(media(content), **kwargs)
        return func
    return inner


def parameter(name: str, schema: Any, location: str = 'query', **kwargs):
    def inner(func):
        param = Parameter(name, scheme(schema), location, **kwargs)

        spec.operations[func].parameters.append(param)
        return func
    return inner


def response(status, content: Any=None, desc: str=None, **kwargs):
    def inner(func):
        _desc = desc or 'Response %s' % status

        spec.operations[func].responses[status] = Response(media(content), description=_desc, **kwargs)
        return func
    return inner
