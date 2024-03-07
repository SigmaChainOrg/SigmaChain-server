from src.core.config.database import Base
from sqlalchemy import Column, UUID, ForeignKey
from src.core.models.user_model import UserModel
from src.core.models.rol_admin_model import RolAdminModel


class AdminModel(Base):
    __tablename__ = "admin"

    id_admin = Column(UUID(as_uuid=True), primary_key=True, nullable=False)
    id_user = Column(UUID(as_uuid=True), ForeignKey(UserModel.id_user), nullable=False)
    id_rol_admin = Column(
        UUID(as_uuid=True), ForeignKey(RolAdminModel.id_rol_admin), nullable=False
    )

    def model_to_dict(self):
        return {
            "id_admin": self.id_admin,
            "id_user": self.id_user,
            "id_rol_admin": self.id_rol_admin,
        }
