from datetime import date


class Todo:
    id = int
    done = bool
    text = str
    title = str
    deadline = date


class TodoList:
    limit = int
    items = [Todo]
