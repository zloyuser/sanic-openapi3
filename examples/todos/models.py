from sanic_openapi3 import components


@components.security('apiKey')
class TodoApiKey:
    name = 'x-api-key'
    location = 'header'


@components.scheme()
class Todo:
    id = int
    done = bool
    text = str
    title = str


@components.scheme()
class TodoList:
    limit = int
    items = [Todo]
