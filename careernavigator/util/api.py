from typing import Any, Optional

from asgiref.sync import sync_to_async
from django.http import HttpRequest
from ninja import Schema
from ninja.renderers import JSONRenderer
from ninja_extra import ControllerBase, api_controller, route
from ninja_extra.permissions import AllowAny, BasePermission
from ninja_jwt.controller import TokenVerificationController, TokenObtainPairController
from ninja_jwt.exceptions import AuthenticationFailed
from ninja_jwt.schema_control import SchemaControl
from ninja_jwt.settings import api_settings
from pydantic import model_validator
from pydantic_core import Url

from core.models import FailedLogin


__all__ = ('AsyncJWTController', 'Renderer')


schema = SchemaControl(api_settings)


def log_failure(verify_schema):
    class _Wrap(verify_schema):
        @classmethod
        def validate_values(cls, values):
            if failure := FailedLogin.is_blocked(cls._request):
                raise AuthenticationFailed(cls._default_error_messages["no_active_account"])
            try:
                return super(_Wrap, cls).validate_values(values)
            except AuthenticationFailed as e:
                FailedLogin.report_failure(cls._request, failure=failure)
                raise e
            
        @model_validator(mode="before")
        def validate_inputs(cls, values):
            cls._request = values._context["request"]
            return super(_Wrap, cls).validate_inputs(values)
    _Wrap.__name__ = verify_schema.__name__
    return _Wrap


@api_controller("/token", permissions=[AllowAny], tags=["token"], auth=None)
class AsyncJWTController(TokenVerificationController, TokenObtainPairController):
    @route.post(
        "/verify",
        response={200: Schema},
        url_name="token_verify",
        operation_id='token_verify',
    )
    async def verify_token(self, token: schema.verify_schema): # type: ignore
        return token.to_response_schema()
    
    @route.post(
        "/pair",
        response=schema.obtain_pair_schema.get_response_schema(),
        url_name="token_obtain_pair",
        operation_id='token_obtain_pair',
    )
    async def obtain_token(self, request: HttpRequest, user_token: log_failure(schema.obtain_pair_schema)): # type: ignore
        await sync_to_async(user_token.check_user_authentication_rule)()
        return user_token.to_response_schema()

    @route.post(
        "/refresh",
        response=schema.obtain_pair_refresh_schema.get_response_schema(),
        url_name="token_refresh",
        operation_id='token_refresh',
    )
    async def refresh_token(self, refresh_token: schema.obtain_pair_refresh_schema): # type: ignore
        refresh = await sync_to_async(refresh_token.to_response_schema)()
        return refresh


class Renderer(JSONRenderer):
    def reshape(self, value) -> Any:
        if isinstance(value, list):
            return [self.reshape(v) for v in value]
        elif isinstance(value, tuple):
            return tuple(self.reshape(v) for v in value)
        elif isinstance(value, dict):
            return {k: self.reshape(v) for k, v in value.items()}
        elif isinstance(value, Url):
            return str(value)
        else:
            return value

    def render(self, request: HttpRequest, data: Any, *, response_status: int) -> Any:
        return super().render(request, self.reshape(data), response_status=response_status)

class UserWithPermission(BasePermission):
    def __init__(self, permission: str) -> None:
        self._permission = permission

    def has_permission(self, request: HttpRequest, controller: Optional[ControllerBase] = None) -> bool:
        return request.user.has_perm(self._permission)


class SuperuserPermission(BasePermission):
    def has_permission(self, request: HttpRequest, controller: Optional[ControllerBase] = None) -> bool:
        return request.user.is_superuser


class MentorPermission(BasePermission):
    def has_permission(self, request: HttpRequest, controller: Optional[ControllerBase] = None) -> bool:
        return request.user.is_mentor or request.user.is_superuser


class JobseekerPermission(BasePermission):
    def has_permission(self, request: HttpRequest, controller: Optional[ControllerBase] = None) -> bool:
        return request.user.is_jobseeker or request.user.is_superuser