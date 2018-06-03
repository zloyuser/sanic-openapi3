# from .openapi import operations
#
#
# def http(key, scheme=None, bearer_format=None, description=None):
#     def inner(func):
#         components["securitySchemes"][key] = HttpSecurity(scheme, bearer_format, description).properties()
#         operations[func].security[key] = []
#         return func
#     return inner
#
#
# def api_key(key, name=None, location='header', description=None):
#     def inner(func):
#         components["securitySchemes"][key] = ApiKeySecurity(name, location, description).properties()
#         operations[func].security[key] = []
#         return func
#     return inner
#
#
# def openid(key, url=None, description=None):
#     def inner(func):
#         components["securitySchemes"][key] = OpenIdSecurity(url, description).properties()
#         operations[func].security[key] = []
#         return func
#     return inner
