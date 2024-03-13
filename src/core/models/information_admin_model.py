from src.core.config.database import Base
from sqlalchemy import Column, String, Integer, Date, UUID
from src.core.models.data_admin_model import DataAdminModel
from src.core.models.admin_model import AdminModel

class InfoAdminModel(Base):
    __tablename__ = "information_admin"

    id_info_admin = Column(UUID(as_uuid=True), primary_key=True, nullable=False)
    id_admin = Column(UUID(as_uuid=True), ForeignKey(AdminModel.id_admin), nullable=False)
    id_data_admin = Column(UUID(as_uuid=True), ForeignKey(DataAdminModel.id_data_admin), nullable=False)
    data_info_admin = Column(String, nullable=False)

    def model_to_dict(self):
        return {
            "id_info_admin": self.id_info_admin,
            "id_admin": self.id_admin,
            "id_data_admin": self.id_data_admin,
            "data_info_admin": self.data_info_admin,
        }