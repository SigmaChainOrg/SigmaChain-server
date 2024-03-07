from src.core.config.database import Base
from sqlalchemy import Column, UUID, String


class RolAdminModel(Base):
    __tablename__ = "rol_admin"

    id_rol_admin = Column(UUID(as_uuid=True), primary_key=True, nullable=False)
    name = Column(String, nullable=False)

    def model_to_dict(self):
        return {
            "id_rol_admin": self.id_rol_admin,
            "name": self.name,
        }
