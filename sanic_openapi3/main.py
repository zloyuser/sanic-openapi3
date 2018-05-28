import re

from itertools import repeat
from sanic.blueprints import Blueprint
from sanic.response import json
from sanic.views import CompositionView
from .openapi import *
from .types import *

blueprint = Blueprint('openapi3')

_spec = {}


# Removes all null values from a dictionary
def remove_nulls(dictionary, deep=True):
    return {
        k: remove_nulls(v, deep) if deep and type(v) is dict else v
        for k, v in dictionary.items()
        if v is not None
    }


def build_content(app, content):
    result = {}

    if isinstance(content, dict):
        for content_type, schema in content.items():
            result[content_type] = {
                "schema": serialize_schema(schema)
            }
    else:
        content_type = getattr(app.config, 'OPENAPI_CONTENT_TYPE', '*/*')

        result[content_type] = {
            "schema": serialize_schema(content)
        }

    return result


@blueprint.listener('before_server_start')
def build_spec(app, loop):
    app.add_route(spec, uri=getattr(app.config, 'OPENAPI_URL', 'openapi.json'), strict_slashes=True)

    _spec['openapi'] = '3.0.0'
    _spec['info'] = {
        "version": getattr(app.config, 'OPENAPI_VERSION', '1.0.0'),
        "title": getattr(app.config, 'OPENAPI_TITLE', 'API'),
        "description": getattr(app.config, 'OPENAPI_DESCRIPTION', ''),
        "termsOfService": getattr(app.config, 'OPENAPI_TERMS_OF_SERVICE', None),
        "contact": {
            "name": getattr(app.config, 'OPENAPI_CONTACT_NAME', None),
            "email": getattr(app.config, 'OPENAPI_CONTACT_EMAIL', None),
            "url": getattr(app.config, 'OPENAPI_CONTACT_URL', None),
        },
        "license": {
            "name": getattr(app.config, 'OPENAPI_LICENSE_NAME', None),
            "url": getattr(app.config, 'OPENAPI_LICENSE_URL', None),
        },
    }
    _spec['components'] = {
        "schemas": {},
    }

    paths = {}
    tags = {}

    # --------------------------------------------------------------- #
    # Blueprint Tags
    # --------------------------------------------------------------- #

    for _blueprint in app.blueprints.values():
        if not hasattr(_blueprint, 'routes'):
            continue

        for _route in _blueprint.routes:
            if _route.handler not in operations:
                continue

            operation = operations.get(_route.handler)

            if not operation.tags:
                operation.tags.append(_blueprint.name)

    for uri, _route in app.router.routes_all.items():
        if '<file_uri' in uri:
            continue

        # --------------------------------------------------------------- #
        # Methods
        # --------------------------------------------------------------- #

        # Build list of methods and their handler functions
        handler_type = type(_route.handler)

        if handler_type is CompositionView:
            view = _route.handler
            method_handlers = view.handlers.items()
        else:
            method_handlers = zip(_route.methods, repeat(_route.handler))

        methods = {}

        for _method, _handler in method_handlers:
            if _handler not in operations:
                continue

            parameters = []
            responses = {}

            operation = operations.get(_handler)

            # Parameters - Path & Query String
            for _parameter in _route.parameters:
                operation.parameters[_parameter.name] = Parameter(_parameter.cast, 'path')

            for key, _parameter in operation.parameters.items():
                parameters.append({
                    'name': key,
                    'in': _parameter.location,
                    'required': _parameter.required,
                    'schema': serialize_schema(_parameter.schema),
                })

            for key, _response in operation.responses.items():
                responses[key] = {
                    'description': _response.description or 'Response %s' % key
                }

                if not _response.content:
                    continue

                responses[key]['content'] = build_content(app, _response.content)

            request_body = None

            if operation.body:
                request_body = {
                    'description': operation.body.description,
                    'content': build_content(app, operation.body.content),
                }

            methods[_method.lower()] = remove_nulls({
                'operationId': (operation.id or "%s.%s" % (_method, _route.name)).lower(),
                'summary': operation.summary,
                'description': operation.description,
                'tags': operation.tags or None,
                'parameters': parameters,
                'responses': responses,
                'requestBody': request_body,
            })

        uri_parsed = uri if uri == "/" else uri.rstrip('/')

        for segment in _route.parameters:
            uri_parsed = re.sub('<' + segment.name + '.*?>', '{' + segment.name + '}', uri_parsed)

        if len(methods) > 0:
            paths[uri_parsed] = methods

    # --------------------------------------------------------------- #
    # Definitions
    # --------------------------------------------------------------- #

    _spec['components']['schemas'] = {obj.name: definition for cls, (obj, definition) in schemas.items()}

    # --------------------------------------------------------------- #
    # Tags
    # --------------------------------------------------------------- #

    for operation in operations.values():
        for _tag in operation.tags:
            tags[_tag] = True

    _spec['tags'] = [{"name": name} for name in tags.keys()]
    _spec['paths'] = paths


def spec(request):
    return json(_spec)
