from django.core.exceptions import PermissionDenied, BadRequest

from django.http import HttpRequest, HttpResponse
from ninja import Swagger
from ninja_extra import NinjaExtraAPI
from ninja_jwt.authentication import AsyncJWTAuth

from careernavigator.util.api import AsyncJWTController, Renderer

description = """
This API provides the functionality for the mobile and web frontends of the \
CareerNavigator application.
""".strip()

api = NinjaExtraAPI(
    title="CareerNavigator API",
    description=description,
    auth=AsyncJWTAuth(),
    renderer=Renderer(),
    docs=Swagger(settings={
        "persistAuthorization": True,
        "showCommonExtensions": True,
        "displayRequestDuration": True,
        "defaultModelRendering": "model",
        "displayOperationId": True,
    }),
)
api.register_controllers(AsyncJWTController)
api.auto_discover_controllers()

@api.exception_handler(PermissionDenied)
def permission_denied_handler(request: HttpRequest, exc: PermissionDenied) -> HttpResponse:
    return api.create_response(
        request,
        {"messages": list(exc.args)},
        status=403,
    )

@api.exception_handler(BadRequest)
def bad_request_handler(request: HttpRequest, exc: BadRequest) -> HttpResponse:
    return api.create_response(
        request,
        {"messages": list(exc.args)},
        status=400,
    )