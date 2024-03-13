from src.core.config.database import Base
from sqlalchemy import Column, String, Integer, Date, UUID


class DataAdminModel(Base):
    __tablename__ = "data_admin"

    id_data_admin = Column(UUID(as_uuid=True), primary_key=True, nullable=False)
    data_title = Column(String, nullable=False)

    def model_to_dict(self):
        return {
            "id_data_admin": self.id_data_admin,
            "data_title": self.data_title,
        }
