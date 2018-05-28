# Sanic OpenAPI v3

[![Build Status](https://travis-ci.org/zloyuser/sanic-openapi3.svg?branch=master)](https://travis-ci.org/zloyuser/sanic-openapi3)
[![PyPI](https://img.shields.io/pypi/v/sanic-openapi3.svg)](https://pypi.python.org/pypi/sanic-openapi3/)
[![PyPI](https://img.shields.io/pypi/pyversions/sanic-openapi3.svg)](https://pypi.python.org/pypi/sanic-openapi3/)

Give your Sanic API an OpenAPI v3 specification.
Based on original [Sanic OpenAPI](https://github.com/channelcat/sanic-openapi) extension.

## Installation

```shell
pip install sanic-openapi3
```

## Usage

### Import blueprint and use simple decorators to document routes:

```python
from sanic_openapi3 import openapi, openapi_blueprint

@app.get("/user/<user_id:int>")
@openapi.summary("Fetches a user by ID")
@openapi.response(200, { "user": { "name": str, "id": int } })
async def get_user(request, user_id):
    ...

@app.post("/user")
@openapi.summary("Creates a user")
@openapi.body({"user": { "name": str }})
async def create_user(request):
    ...

app.blueprint(openapi_blueprint)
```

You'll now have a specification at the URL `/openapi.json`.
Your routes will be automatically categorized by their blueprints.

### Model your input/output

```python
class Car:
    make = str
    model = str
    year = int

class Garage:
    spaces = int
    cars = [Car]

@app.get("/garage")
@openapi.summary("Gets the whole garage")
@openapi.response(200, Garage)
async def get_garage(request):
    return json({
        "spaces": 2,
        "cars": [{"make": "Nissan", "model": "370Z"}]
    })

```

### Get more descriptive

```python
class Car:
    make = doc.String("Who made the car")
    model = doc.String("Type of car.  This will vary by make")
    year = doc.Integer("4-digit year of the car", required=False)

class Garage:
    spaces = doc.Integer("How many cars can fit in the garage")
    cars = doc.List(Car, description="All cars in the garage")
```

### Configure all the things

```python
app.config.OPENAPI_VERSION = '1.0.0'
app.config.OPENAPI_TITLE = 'Car API'
app.config.OPENAPI_DESCRIPTION = 'Car API'
app.config.OPENAPI_TERMS_OF_SERVICE = 'https://example.com/terms'
app.config.OPENAPI_CONTACT_EMAIL = 'mail@example.com'
app.config.OPENAPI_CONTACT_NAME = 'mail@example.com'
```
