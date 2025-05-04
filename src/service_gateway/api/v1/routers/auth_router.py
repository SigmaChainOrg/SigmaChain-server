from uuid import UUID

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.configuration import get_db
from src.service_gateway.api.v1.functions.send_emails import send_secure_code_email
from src.service_gateway.api.v1.schemas.access_control.auth_schemas import (
    SecureCodeRead,
    SecureCodeValidate,
    SigninInput,
    SignupInput,
    TokenRead,
)
from src.service_gateway.api.v1.schemas.access_control.user_schemas import (
    UserInfoUpdate,
    UserQuery,
    UserRead,
)
from src.service_gateway.api.v1.schemas.general.general_schemas import APIResponse
from src.service_gateway.api.v1.services.user_service import UserService
from src.service_gateway.security.authentication import (
    create_access_token,
    validate_password,
    validate_password_match,
)
from src.utils.http_exceptions import BadRequestError, InternalServerError

security = HTTPBearer()

auth_router_open = APIRouter(prefix="/auth", tags=["Auth"])
auth_router = APIRouter(prefix="/auth", tags=["Auth"], dependencies=[Depends(security)])


@auth_router_open.post(
    "/signup",
    response_model=APIResponse[SecureCodeRead],
    status_code=201,
)
async def signup(user_signup: SignupInput, db: AsyncSession = Depends(get_db)):
    pw_validity = validate_password(user_signup.password.get_secret_value())

    if not pw_validity.ok:
        raise BadRequestError(pw_validity.msg)

    pw_validity = validate_password_match(
        user_signup.password.get_secret_value(),
        user_signup.confirm_password.get_secret_value(),
    )
    if not pw_validity.ok:
        raise BadRequestError(pw_validity.msg)

    user_service = UserService(db)

    user_id = await user_service.create_user(user_signup)

    secure_code_response, code = await user_service.create_secure_code(user_id)

    email_sent = send_secure_code_email(
        email=user_signup.email,
        code=code,
        code_id=secure_code_response.secure_code_id,
    )

    if not email_sent:
        raise InternalServerError("Error sending Email")

    return JSONResponse(
        content=APIResponse[SecureCodeRead](
            msg="User signed up successfully",
            data=secure_code_response,
            ok=True,
        ).model_dump(),
    )


@auth_router_open.post(
    "/signin",
    response_model=APIResponse[TokenRead | SecureCodeRead],
    status_code=200,
)
async def signin(
    input: SigninInput,
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)

    user_id, user_email = await user_service.verify_user_password(input)

    secure_code_response, code = await user_service.create_secure_code(user_id)

    email_sent = send_secure_code_email(
        email=user_email,
        code=code,
        code_id=secure_code_response.secure_code_id,
    )

    if not email_sent:
        raise InternalServerError("Error sending Email")

    return JSONResponse(
        content=APIResponse[SecureCodeRead](
            msg="Secure code created successfully",
            data=secure_code_response,
            ok=True,
        ).model_dump(),
    )


@auth_router_open.post(
    "/secure-code/validate",
    response_model=APIResponse[TokenRead],
    status_code=200,
)
async def validate_secure_code(
    data: SecureCodeValidate,
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)

    user_id, roles = await user_service.verify_secure_code(data)

    token = create_access_token(
        data={
            "sub": str(user_id),
            "roles": roles,
        }
    )

    token_schema = TokenRead(
        access_token=token,
        token_type="bearer",
    )

    return JSONResponse(
        content=APIResponse[TokenRead](
            msg="User signed in successfully",
            data=token_schema,
            ok=True,
        ).model_dump(),
    )


@auth_router.get("/me", response_model=APIResponse[UserRead], status_code=200)
async def me(
    request: Request,
    query: UserQuery = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)

    user_id: UUID = request.state.user_id
    user_data = await user_service.get_user_data_by_id(user_id, query)

    return JSONResponse(
        content=APIResponse[UserRead](
            msg="User signed in successfully",
            data=user_data,
            ok=True,
        ).model_dump(),
    )


@auth_router.patch(
    "/me/user-info",
    response_model=APIResponse[UserRead],
    status_code=200,
)
async def update_user_info(
    data: UserInfoUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)

    user_id: UUID = request.state.user_id
    user_data = await user_service.update_user_info_data_by_user_id(user_id, data)

    return JSONResponse(
        content=APIResponse[UserRead](
            msg="User info updated successfully",
            data=user_data,
            ok=True,
        ).model_dump(),
    )
