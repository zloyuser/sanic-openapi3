import datetime

from examples.todos.models import *


test_todo: Todo = {
    'id': 1,
    'done': False,
    'text': 'Do something interesting',
    'title': 'Wow!',
    'deadline': datetime.date(year=2018, month=12, day=31)
}

test_list: TodoList = {
    'limit': 5,
    'items': [test_todo]
}
