from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.database.models.access_control.secure_code import SecureCode
from src.database.models.access_control.user import User, UserInfo
from src.service_gateway.api.v1.schemas.access_control.auth_schemas import (
    SecureCodeInput,
    SecureCodeSchema,
)
from src.service_gateway.api.v1.schemas.access_control.user_schemas import (
    UserInfoUpdate,
    UserSchema,
    UserSignUpInput,
)
from src.service_gateway.security.authentication import (
    generate_random_code,
    hash_password,
    verify_password,
)
from src.utils.function_responses import ResponseComplete, ResponseData
from src.utils.http_exceptions import (
    BadRequestError,
    DatabaseIntegrityError,
    EmailAlreadyExistsError,
)


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.db: AsyncSession = db

    ## Private methods

    async def __get_user_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).filter(
                User.email == email,
                User.is_active.is_(True),
            )
        )
        user = result.scalars().first()

        return user

    async def __get_user_by_id(self, user_id: UUID) -> Optional[User]:
        result = await self.db.execute(
            select(User).filter(
                User.user_id == user_id,
                User.is_active.is_(True),
            )
        )
        user = result.scalars().first()

        return user

    ## Public methods

    async def create_user(self, user_signin: UserSignUpInput) -> None:
        hashed_password = hash_password(user_signin.password.get_secret_value())

        new_user = User(
            email=user_signin.email,
            hashed_password=hashed_password,
        )
        self.db.add(new_user)

        try:
            await self.db.commit()
        except IntegrityError as e:
            await self.db.rollback()

            if "user_email" in str(e):
                raise EmailAlreadyExistsError()

            raise DatabaseIntegrityError()

    async def get_user_data_by_id(self, user_id: UUID) -> Optional[UserSchema]:
        result = await self.db.execute(
            select(User).filter(
                User.user_id == user_id,
                User.is_active.is_(True),
            )
        )
        user = result.scalars().first()

        if user is None:
            return None

        return UserSchema.model_validate(user)

    async def update_user_info_data_by_user_id(
        self, user_id: UUID, user_info_data: UserInfoUpdate
    ) -> Optional[UserSchema]:
        user = await self.__get_user_by_id(user_id)

        if user is None:
            raise BadRequestError("User not found")

        update_data = user_info_data.model_dump(exclude_unset=True)
        user_info = user.user_info

        if user_info is None:
            user_info = UserInfo(user_id=user_id, **update_data)
            self.db.add(user_info)
        else:
            for key, value in update_data.items():
                setattr(user_info, key, value)

        await self.db.refresh(user)

        user_schema = UserSchema.model_validate(user)

        await self.db.commit()

        return user_schema

    async def verify_user_password(
        self,
        email: str,
        password: str,
    ) -> ResponseData[Optional[UserSchema]]:
        user = await self.__get_user_by_email(email)

        if user is None:
            return ResponseData(data=None, ok=False)

        user_schema = UserSchema.model_validate(user)
        return ResponseData(
            data=user_schema,
            ok=verify_password(password, user.hashed_password),
        )

    async def change_user_password(self, email: str, new_password: str) -> bool:
        user = await self.__get_user_by_email(email)

        if user is None:
            return False

        hashed_password = hash_password(new_password)
        user.hashed_password = hashed_password

        await self.db.commit()

        return True

    async def verify_secure_code(
        self, secure_code_input: SecureCodeInput
    ) -> ResponseComplete[Optional[UUID]]:
        try:
            result = await self.db.execute(
                select(SecureCode).filter(
                    SecureCode.secure_code_id == secure_code_input.secure_code_id,
                    SecureCode.code == secure_code_input.code,
                )
            )
            secure_code = result.scalars().first()

            if secure_code is None:
                return ResponseComplete(msg="Invalid secure code", data=None, ok=False)

            if secure_code.expires_at.replace(tzinfo=timezone.utc) < datetime.now(
                timezone.utc
            ):
                return ResponseComplete(msg="Secure code expired", data=None, ok=False)

            if secure_code.has_been_used:
                return ResponseComplete[Optional[UUID]](
                    msg="Secure code already used", data=None, ok=False
                )

            secure_code.has_been_used = True

            response = ResponseComplete[Optional[UUID]](
                msg="Secure code verified", data=secure_code.user_id, ok=True
            )

            await self.db.commit()

            return response

        except Exception:
            await self.db.rollback()

            raise

    async def create_secure_code(self, user_id: UUID) -> Tuple[SecureCodeSchema, str]:
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

        try:
            secure_code = SecureCode(
                user_id=user_id,
                expires_at=expires_at.replace(tzinfo=None),
                code=generate_random_code(6),
            )
            self.db.add(secure_code)

            await self.db.flush()

            secure_schema = SecureCodeSchema.model_validate(secure_code)
            code = secure_code.code

            await self.db.commit()

            return (secure_schema, code)

        except Exception:
            await self.db.rollback()

            raise
