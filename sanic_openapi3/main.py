from sanic.blueprints import Blueprint
from sanic.response import json
from sanic_openapi3.openapi import spec


blueprint = Blueprint('openapi3')


@blueprint.listener('before_server_start')
def build_spec(app, loop):
    openapi = spec.build(app).serialize()

    def spec_json(request):
        return json(openapi)

    app.add_route(spec_json, uri=getattr(app.config, 'OPENAPI_URL', 'openapi.json'), strict_slashes=True)
