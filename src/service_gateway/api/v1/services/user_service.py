from datetime import datetime, timedelta, timezone
from math import ceil
from typing import List, Literal, Optional, Sequence, Tuple
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import or_

from src.database.models.access_control.enums import RoleEnum
from src.database.models.access_control.role import UserRoles
from src.database.models.access_control.secure_code import SecureCode
from src.database.models.access_control.user import User, UserInfo
from src.service_gateway.api.v1.schemas.access_control.auth_schemas import (
    SecureCodeRead,
    SecureCodeValidate,
)
from src.service_gateway.api.v1.schemas.access_control.user_schemas import (
    UserFilters,
    UserInfoUpdate,
    UserInput,
    UserQuery,
    UserRead,
    UserSignInInput,
)
from src.service_gateway.api.v1.schemas.general.general_schemas import (
    PaginatedData,
    Pagination,
)
from src.service_gateway.security.authentication import (
    generate_random_code,
    hash_password,
    verify_password,
)
from src.utils.http_exceptions import (
    AuthenticationError,
    DatabaseIntegrityError,
    EmailAlreadyExistsError,
    NotFoundError,
    UnprocessableEntityError,
)


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.db: AsyncSession = db

    ## Friendly methods

    async def _get_user(
        self,
        *,
        by: Literal["email", "id"],
        value: str | UUID,
        with_groups: bool = False,
        with_roles: bool = False,
    ) -> Optional[User]:
        if by == "email":
            query = select(User).where(
                User.email == value,
                User.is_active.is_(True),
            )
        elif by == "id":
            query = select(User).where(
                User.user_id == value,
                User.is_active.is_(True),
            )
        else:
            raise ValueError("Invalid 'by' parameter. Use 'email' or 'id'.")

        if with_groups:
            query = query.options(selectinload(User.groups))
        if with_roles:
            query = query.options(selectinload(User.roles))

        result = await self.db.execute(query)
        user = result.scalars().first()

        return user

    async def _get_users(
        self,
        *,
        with_groups: bool = False,
        with_roles: bool = False,
        only_active: bool = True,
        only_verified: Optional[bool] = None,
        name_like: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> Sequence[User]:
        query = select(User).where(
            User.is_active.is_(only_active),
        )

        if page is not None and page_size is not None:
            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)
        elif page is not None or page_size is not None:
            raise ValueError("Both page and page_size must be provided together.")

        if only_verified is not None:
            query = query.where(User.is_verified.is_(only_verified))

        if with_groups:
            query = query.options(selectinload(User.groups))

        if with_roles:
            query = query.options(selectinload(User.roles))

        if name_like:
            query = query.join(User.user_info).where(
                or_(
                    UserInfo.first_name.ilike(f"%{name_like}%"),
                    UserInfo.last_name.ilike(f"%{name_like}%"),
                )
            )

        result = await self.db.execute(query)
        users = result.scalars().all()

        return users

    ## Public methods

    async def create_user(self, user_signin: UserInput) -> UUID:
        try:
            hashed_password = hash_password(user_signin.password.get_secret_value())

            new_user = User(
                email=user_signin.email,
                hashed_password=hashed_password,
            )
            self.db.add(new_user)

            await self.db.flush()
            await self.db.refresh(new_user)

            new_user_role = UserRoles(user_id=new_user.user_id, role=RoleEnum.REQUESTER)
            self.db.add(new_user_role)

            await self.db.flush()
            await self.db.refresh(new_user)

            user_id = new_user.user_id

            await self.db.commit()

            return user_id

        except IntegrityError as e:
            await self.db.rollback()

            if "user_email" in str(e):
                raise EmailAlreadyExistsError()

            raise DatabaseIntegrityError()

        except Exception:
            await self.db.rollback()

            raise

    async def get_user_data_by_id(
        self, user_id: UUID, user_query: UserQuery
    ) -> UserRead:
        user = await self._get_user(
            by="id",
            value=user_id,
            with_groups=user_query.include_groups,
            with_roles=user_query.include_roles,
        )

        if user is None:
            raise NotFoundError("User not found")

        return UserRead.model_validate(
            user.to_dict(
                with_user_info=user_query.include_user_info,
                with_roles=user_query.include_roles,
                with_groups=user_query.include_groups,
            )
        )

    async def get_users(
        self,
        filters: UserFilters,
    ) -> PaginatedData[UserRead]:
        total_count = await self.db.execute(select(func.count()).select_from(User))
        total_count = total_count.scalar_one()

        total_pages = ceil(total_count / filters.page_size)

        if filters.page > total_pages:
            raise UnprocessableEntityError(
                f"Page {filters.page} exceeds the total number of pages {total_pages}."
            )

        users = await self._get_users(
            with_groups=filters.include_groups,
            with_roles=filters.include_roles,
            only_active=filters.only_active,
            only_verified=filters.only_verified,
            name_like=filters.name,
            page=filters.page,
            page_size=filters.page_size,
        )

        users_schema = [
            UserRead.model_validate(
                user.to_dict(
                    with_user_info=filters.include_user_info,
                    with_roles=filters.include_roles,
                    with_groups=filters.include_groups,
                )
            )
            for user in users
        ]

        pagination = Pagination(
            page=filters.page,
            size=filters.page_size,
            total=total_count,
            pages=total_pages,
        )

        paginated_data = PaginatedData(
            items=users_schema,
            pagination=pagination,
        )

        return paginated_data

    async def update_user_info_data_by_user_id(
        self,
        user_id: UUID,
        user_info_data: UserInfoUpdate,
    ) -> UserRead:
        user = await self._get_user(by="id", value=user_id)

        if user is None:
            raise NotFoundError("User not found")

        update_data = user_info_data.model_dump(exclude_unset=True)
        user_info = user.user_info

        if user_info is None:
            user_info = UserInfo(user_id=user_id, **update_data)
            self.db.add(user_info)
        else:
            for key, value in update_data.items():
                setattr(user_info, key, value)

        await self.db.refresh(user)

        user_schema = UserRead.model_validate(user)

        await self.db.commit()

        return user_schema

    async def verify_user_password(
        self,
        input: UserSignInInput,
    ) -> Tuple[UUID, str]:
        user = await self._get_user(by="email", value=input.email)

        if user is None:
            raise AuthenticationError("Invalid email or password")

        password_verified = verify_password(
            input.password.get_secret_value(), user.hashed_password
        )

        if not password_verified:
            raise AuthenticationError("Invalid email or password")

        return user.user_id, user.email

    async def change_user_password(self, email: str, new_password: str) -> bool:
        user = await self._get_user(by="email", value=email)

        if user is None:
            return False

        hashed_password = hash_password(new_password)
        user.hashed_password = hashed_password

        await self.db.commit()

        return True

    async def verify_secure_code(
        self, secure_code_input: SecureCodeValidate
    ) -> Tuple[UUID, List[str]]:
        try:
            result = await self.db.execute(
                select(SecureCode).where(
                    SecureCode.secure_code_id == secure_code_input.secure_code_id,
                    SecureCode.code == secure_code_input.code,
                )
            )
            secure_code = result.scalars().first()

            if secure_code is None:
                raise AuthenticationError("Invalid secure code")

            if secure_code.expires_at.replace(tzinfo=timezone.utc) < datetime.now(
                timezone.utc
            ):
                raise AuthenticationError("Secure code expired")

            if secure_code.has_been_used:
                raise AuthenticationError("Secure code already used")

            secure_code.has_been_used = True

            user = await self._get_user(
                by="id",
                value=secure_code.user_id,
                with_roles=True,
            )

            if not user:
                raise NotFoundError("User not found")

            if user.is_verified is False:
                user.is_verified = True
                await self.db.flush()

            roles = [user_role.role.value for user_role in user.roles]

            response = (secure_code.user_id, roles)

            await self.db.commit()

            return response

        except Exception:
            await self.db.rollback()

            raise

    async def create_secure_code(self, user_id: UUID) -> Tuple[SecureCodeRead, str]:
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

        try:
            secure_code = SecureCode(
                user_id=user_id,
                expires_at=expires_at.replace(tzinfo=None),
                code=generate_random_code(6),
            )
            self.db.add(secure_code)

            await self.db.flush()

            secure_schema = SecureCodeRead.model_validate(secure_code)
            code = secure_code.code

            await self.db.commit()

            return (secure_schema, code)

        except Exception:
            await self.db.rollback()

            raise
