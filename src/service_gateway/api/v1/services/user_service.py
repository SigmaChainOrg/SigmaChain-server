from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.database.models.access_control.user import User
from src.service_gateway.api.v1.schemas.access_control.user_schemas import (
    UserSchema,
    UserSignUpSchema,
)
from src.service_gateway.security.authentication import hash_password, verify_password
from src.utils.function_responses import ResponseData


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

    ## Public methods

    async def create_user(self, user_signin: UserSignUpSchema) -> None:
        hashed_password = hash_password(user_signin.password.get_secret_value())

        new_user = User(
            email=user_signin.email,
            hashed_password=hashed_password,
        )
        self.db.add(new_user)

        await self.db.commit()

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
