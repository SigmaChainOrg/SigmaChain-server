from src.core.config.database import Base
from sqlalchemy import Column, String, Integer, Date, UUID


class UserModel(Base):
    __tablename__ = "user"

    id_user = Column(UUID(as_uuid=True), primary_key=True, nullable=False)
    dni = Column(String, nullable=False, unique=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    birth_date = Column(Date, nullable=False)
    email = Column(String, nullable=False, unique=True)
    salt = Column(Integer, nullable=False)
    hash_pass = Column(String, nullable=False)

    def model_to_dict(self):
        return {
            "id_user": self.id_user,
            "dni": self.dni,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "birth_date": self.birth_date,
            "email": self.email,
            "password": self.hash_pass,
        }
