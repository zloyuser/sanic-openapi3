import re

from itertools import repeat
from sanic.blueprints import Blueprint
from sanic.response import json
from sanic.views import CompositionView

from sanic_openapi3.builders import ComponentsBuilder, OperationsBuilder, SpecificationBuilder

blueprint = Blueprint('openapi3')
components = ComponentsBuilder()
operations = OperationsBuilder()
specification = SpecificationBuilder(components)


@blueprint.listener('before_server_start')
def build_spec(app, loop):
    # --------------------------------------------------------------- #
    # Globals
    # --------------------------------------------------------------- #
    specification.describe(
        getattr(app.config, 'OPENAPI_TITLE', 'API'),
        getattr(app.config, 'OPENAPI_VERSION', '1.0.0'),
        getattr(app.config, 'OPENAPI_DESCRIPTION', None),
        getattr(app.config, 'OPENAPI_TERMS_OF_SERVICE', None)
    )

    specification.license(
        getattr(app.config, 'OPENAPI_LICENSE_NAME', None),
        getattr(app.config, 'OPENAPI_LICENSE_URL', None)
    )

    specification.contact(
        getattr(app.config, 'OPENAPI_CONTACT_NAME', None),
        getattr(app.config, 'OPENAPI_CONTACT_URL', None),
        getattr(app.config, 'OPENAPI_CONTACT_EMAIL', None)
    )

    # --------------------------------------------------------------- #
    # Blueprints
    # --------------------------------------------------------------- #
    for _blueprint in app.blueprints.values():
        if not hasattr(_blueprint, 'routes'):
            continue

        for _route in _blueprint.routes:
            if _route.handler not in operations:
                continue

            operation = operations.get(_route.handler)

            if not operation.tags:
                operation.tag(_blueprint.name)

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

        for method, _handler in method_handlers:
            if _handler not in operations:
                continue

            operation = operations[_handler]

            if not hasattr(operation, 'operationId'):
                operation.operationId = '%s_%s' % (method.lower(), _route.name)

            for _parameter in _route.parameters:
                operation.parameter(_parameter.name, _parameter.cast, 'path')

            specification.operation(uri, method, operation)

    openapi = specification.build().serialize()

    def spec_json(request):
        return json(openapi)

    app.add_route(spec_json, uri=getattr(app.config, 'OPENAPI_URL', 'openapi.json'), strict_slashes=True)
