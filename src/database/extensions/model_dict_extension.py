# src/database/extensions.py
from typing import Optional, Set

from sqlalchemy.orm import Mapper


class ModelDictExtension:
    """
    ModelDictExtension provides a utility to add a recursive and safe to_dict() method to all SQLAlchemy models.
    """

    @classmethod
    def register(cls):
        """Adds to_dict() to all SQLAlchemy models"""
        setattr(Mapper, "to_dict", cls._mapper_to_dict)

    @staticmethod
    def _mapper_to_dict(
        mapper,
        instance,
        exclude_unloaded: bool = True,
        _processed: Optional[Set[int]] = None,
    ) -> dict:
        """Safe version for MappedAsDataclass and recursion"""
        if _processed is None:
            _processed = set()

        instance_id = id(instance)
        if instance_id in _processed:
            return {"$recursive": f"{mapper.class_.__name__}#{instance_id}"}

        _processed.add(instance_id)

        # Usa columnas del mapper para compatibilidad con MappedAsDataclass
        result = {col.name: getattr(instance, col.name) for col in mapper.columns}

        for rel in mapper.relationships:
            if rel.key in instance.__dict__ or not exclude_unloaded:
                value = getattr(instance, rel.key)

                if value is None:
                    result[rel.key] = None
                elif rel.uselist:
                    result[rel.key] = [
                        item.to_dict(exclude_unloaded, _processed) for item in value
                    ]
                else:
                    result[rel.key] = (
                        value.to_dict(exclude_unloaded, _processed) if value else None
                    )

        return result
        return result
