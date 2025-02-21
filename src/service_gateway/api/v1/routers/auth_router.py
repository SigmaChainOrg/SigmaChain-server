from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.configuration import get_db
from src.service_gateway.api.v1.schemas.access_control.auth_schemas import (
    SecureCodeInput,
    SecureCodeSchema,
    TokenSchema,
)
from src.service_gateway.api.v1.schemas.access_control.user_schemas import (
    UserInfoUpdate,
    UserSchema,
    UserSignUpInput,
)
from src.service_gateway.api.v1.schemas.general.general_schemas import ResponseSchema
from src.service_gateway.api.v1.services.user_service import UserService
from src.service_gateway.security.authentication import (
    create_access_token,
    validate_password,
    validate_password_match,
)
from src.utils.email_sender import send_html_email
from src.utils.http_exceptions import (
    AuthenticationError,
    BadRequestError,
    NotFoundError,
)
from src.utils.template_loader import load_html_template

security = HTTPBearer()

auth_router_open = APIRouter(prefix="/auth", tags=["Auth"])
auth_router = APIRouter(prefix="/auth", tags=["Auth"], dependencies=[Depends(security)])


class OAuth2EmailRequestForm:
    def __init__(
        self,
        email: str = Form(...),
        password: str = Form(..., extra={"type": "password"}),
    ):
        self.email = email
        self.password = password


@auth_router_open.post("/signup", response_model=ResponseSchema[None], status_code=201)
async def signup(user_signup: UserSignUpInput, db: AsyncSession = Depends(get_db)):
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

    await user_service.create_user(user_signup)

    return JSONResponse(
        content=ResponseSchema[None](
            msg="User signed up successfully",
            data=None,
            ok=True,
        ).model_dump(),
    )


@auth_router_open.post(
    "/signin",
    response_model=ResponseSchema[TokenSchema | SecureCodeSchema],
    status_code=200,
)
async def signin(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2EmailRequestForm = Depends(),
):
    user_service = UserService(db)

    verified_response = await user_service.verify_user_password(
        email=form_data.email,
        password=form_data.password,
    )

    if not verified_response.ok:
        raise AuthenticationError("Invalid email or password")

    user_schema = verified_response.data

    if user_schema is None:
        raise NotFoundError("User not found")

    secure_code_response, code = await user_service.create_secure_code(
        user_schema.user_id
    )

    if code is None:
        raise BadRequestError("Secure code not created")

    template_path = Path("templates/secure_code_email.html")

    html = load_html_template(
        str(template_path),
        secure_code=code,
        link="Link",
    )

    email_sent = send_html_email(
        to=user_schema.email,
        subject="Secure code for SigmaChain",
        html=html,
    )

    if not email_sent:
        raise BadRequestError("Email not sent")

    return JSONResponse(
        content=ResponseSchema[SecureCodeSchema](
            msg="Secure code created successfully",
            data=secure_code_response,
            ok=True,
        ).model_dump(),
    )


@auth_router_open.post(
    "/secure_code",
    response_model=ResponseSchema[TokenSchema],
    status_code=200,
)
async def secure_code(
    data: SecureCodeInput,
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)

    verified_response = await user_service.verify_secure_code(data)

    if not verified_response.ok:
        raise AuthenticationError(verified_response.msg)

    user_id = verified_response.data

    if user_id is None:
        raise NotFoundError("User not found")

    token = create_access_token(
        data={
            "sub": str(user_id),
        }
    )

    token_schema = TokenSchema(
        access_token=token,
        token_type="bearer",
    )

    return JSONResponse(
        content=ResponseSchema[TokenSchema](
            msg="User signed in successfully",
            data=token_schema,
            ok=True,
        ).model_dump(),
    )


@auth_router.get("/me", response_model=ResponseSchema[UserSchema], status_code=200)
async def me(request: Request, db: AsyncSession = Depends(get_db)):
    user_service = UserService(db)

    user_id: UUID = request.state.user_id
    user_data = await user_service.get_user_data_by_id(user_id)

    if user_data is None:
        raise NotFoundError("User not found")

    return JSONResponse(
        content=ResponseSchema[UserSchema](
            msg="User signed in successfully",
            data=user_data,
            ok=True,
        ).model_dump(),
    )


@auth_router.patch(
    "/me/user_info",
    response_model=ResponseSchema[UserSchema],
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

    if user_data is None:
        raise NotFoundError("User not found")

    return JSONResponse(
        content=ResponseSchema[UserSchema](
            msg="User info updated successfully",
            data=user_data,
            ok=True,
        ).model_dump(),
    )
