from typing import Any, Generic, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database.init_db import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CrudBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def get_all(self, db: Session, skip: int = 0, limit: int = 20) -> dict:
        query = db.query(self.model).order_by(desc("created_date"))
        total = query.count()

        items = query.offset(skip).limit(limit).all()

        return {
            "items": items,
            "total": total
        }

    async def get_one(self, db: Session, model_id: Any) -> Optional[ModelType]:
        return await db.query(self.model).filter(self.model.id == model_id).first()

    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        # db.add(db_obj)
        # db.commit()
        # db.refresh(db_obj)
        return db_obj.flush()

    def update(self, db: Session, db_obj: ModelType, obj_in: Union[UpdateSchemaType, dict[str, Any]]) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, model_id: int) -> ModelType:
        obj = db.query(self.model).get(model_id)
        db.delete(obj)
        db.commit()
        return obj

    def filter(self, db: Session, column: ModelType, value: str) -> list:
        return db.query(self.model).filter(column == value).all()
