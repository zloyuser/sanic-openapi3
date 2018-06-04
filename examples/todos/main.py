from sanic import Sanic, Blueprint
from sanic.response import json
from sanic_openapi3 import openapi, blueprint
from examples.todos.data import *


todos = Blueprint('todo', 'todo')


@todos.get("/", strict_slashes=True)
@openapi.summary("Fetches all todos")
@openapi.description("Really gets the job done fetching these todos. I mean, really, wow.")
@openapi.parameter('done', bool)
@openapi.response(200, TodoList)
def todo_list(request):
    return json(test_list)


@todos.get("/<todo_id:int>", strict_slashes=True)
@openapi.summary("Fetches a todo item by ID")
@openapi.response(200, Todo)
def todo_get(request, todo_id):
    return json(test_todo)


@todos.put("/<todo_id:int>", strict_slashes=True)
@openapi.summary("Updates a todo item")
@openapi.body(Todo, description='Todo object for update')
@openapi.response(200, Todo)
@openapi.secured(TodoApiKey)
def todo_put(request, todo_id):
    return json(test_todo)


@todos.delete("/<todo_id:int>", strict_slashes=True)
@openapi.summary("Deletes a todo")
@openapi.response(204)
@openapi.secured(TodoApiKey)
def todo_delete(request, todo_id):
    return json({})


app = Sanic()

app.blueprint(todos)
app.blueprint(blueprint)

app.config.OPENAPI_VERSION = '0.0.1'
app.config.OPENAPI_TITLE = 'Todo API'
app.config.OPENAPI_DESCRIPTION = 'Advenced todo API for own purposes'
app.config.OPENAPI_TERMS_OF_SERVICE = 'https://example.com/terms-of-service'
app.config.OPENAPI_CONTACT_NAME = 'John Doe'
app.config.OPENAPI_CONTACT_EMAIL = 'info@example.com'
app.config.OPENAPI_CONTACT_URL = 'https://example.com'
app.config.OPENAPI_LICENSE_NAME = 'MIT'
app.config.OPENAPI_LICENSE_URL = 'https://example.com/license'

app.run(host="0.0.0.0", debug=True)
