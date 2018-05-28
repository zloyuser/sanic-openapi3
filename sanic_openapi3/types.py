from datetime import date, datetime


schemas = {}


class Field:
    description = str
    required = bool

    def __init__(self, description=None, required=None):
        self.description = description
        self.required = required

    def serialize(self):
        output = {}
        if self.description:
            output['description'] = self.description
        if self.required is not None:
            output['required'] = self.required
        return output


class Integer(Field):
    def serialize(self):
        return {
            "type": "integer",
            "format": "int32",
            **super().serialize()
        }


class Long(Field):
    def serialize(self):
        return {
            "type": "integer",
            "format": "int64",
            **super().serialize()
        }


class Float(Field):
    def serialize(self):
        return {
            "type": "number",
            "format": "float",
            **super().serialize()
        }


class Double(Field):
    def serialize(self):
        return {
            "type": "number",
            "format": "double",
            **super().serialize()
        }


class String(Field):
    def serialize(self):
        return {
            "type": "string",
            **super().serialize()
        }


class Byte(Field):
    def serialize(self):
        return {
            "type": "string",
            "format": "byte",
            **super().serialize()
        }


class Binary(Field):
    def serialize(self):
        return {
            "type": "string",
            "format": "binary",
            **super().serialize()
        }


class Boolean(Field):
    def serialize(self):
        return {
            "type": "boolean",
            **super().serialize()
        }


class Date(Field):
    def serialize(self):
        return {
            "type": "string",
            "format": "date",
            **super().serialize()
        }


class DateTime(Field):
    def serialize(self):
        return {
            "type": "string",
            "format": "date-time",
            **super().serialize()
        }


class Password(Field):
    def serialize(self):
        return {
            "type": "string",
            "format": "password",
            **super().serialize()
        }


class Tuple(Field):
    pass


class Dictionary(Field):
    def __init__(self, fields=None, **kwargs):
        self.fields = fields or {}
        super().__init__(**kwargs)

    def serialize(self):
        return {
            "type": "object",
            "properties": {key: serialize_schema(schema) for key, schema in self.fields.items()},
            **super().serialize()
        }


class List(Field):
    def __init__(self, items=None, *args, **kwargs):
        self.items = items or []
        if type(self.items) is not list:
            self.items = [self.items]
        super().__init__(*args, **kwargs)

    def serialize(self):
        items = []
        if len(self.items) > 1:
            items = Tuple(self.items).serialize()
        elif self.items:
            items = serialize_schema(self.items[0])
        return {
            "type": "array",
            "items": items
        }


class Object(Field):
    name = str

    def __init__(self, cls, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cls = cls
        self.name = cls.__name__

        if self.cls not in schemas:
            schemas[self.cls] = (self, self.definition)

    @property
    def definition(self):
        return {
            "type": "object",
            "properties": {
                key: serialize_schema(schema) for key, schema in self.cls.__dict__.items() if not key.startswith("_")
            },
            **super().serialize()
        }

    def serialize(self):
        return {
            "$ref": "#/components/schemas/{}".format(self.name),
            **super().serialize()
        }


def serialize_schema(schema):
    schema_type = type(schema)

    # --------------------------------------------------------------- #
    # Class
    # --------------------------------------------------------------- #
    if schema_type is type:
        if issubclass(schema, Field):
            return schema().serialize()
        elif schema is dict:
            return Dictionary().serialize()
        elif schema is list:
            return List().serialize()
        elif schema is int:
            return Integer().serialize()
        elif schema is float:
            return Float().serialize()
        elif schema is str:
            return String().serialize()
        elif schema is bool:
            return Boolean().serialize()
        elif schema is date:
            return Date().serialize()
        elif schema is datetime:
            return DateTime().serialize()
        else:
            return Object(schema).serialize()

    # --------------------------------------------------------------- #
    # Object
    # --------------------------------------------------------------- #
    else:
        if issubclass(schema_type, Field):
            return schema.serialize()
        elif schema_type is dict:
            return Dictionary(schema).serialize()
        elif schema_type is list:
            return List(schema).serialize()

    return {}
