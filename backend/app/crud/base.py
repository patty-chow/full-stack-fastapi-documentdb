from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from uuid import uuid4

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic import BaseModel

from app.db.mongodb import get_database

ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], collection_name: str):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        
        **Parameters**
        
        * `model`: A Pydantic model class
        * `collection_name`: Name of the MongoDB collection
        """
        self.model = model
        self.collection_name = collection_name

    async def get_collection(self) -> AsyncIOMotorCollection:
        db = await get_database()
        return db[self.collection_name]

    async def get(self, id: str) -> Optional[ModelType]:
        collection = await self.get_collection()
        doc = await collection.find_one({"_id": id})
        if doc:
            doc["id"] = doc.pop("_id")
            return self.model(**doc)
        return None

    async def get_multi(
        self, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        collection = await self.get_collection()
        cursor = collection.find().skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        items = []
        for doc in docs:
            doc["id"] = doc.pop("_id")
            items.append(self.model(**doc))
        return items

    async def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        collection = await self.get_collection()
        obj_data = obj_in.dict()
        # Generate a unique ID
        obj_data["_id"] = str(uuid4())
        result = await collection.insert_one(obj_data)
        obj_data["id"] = obj_data.pop("_id")
        return self.model(**obj_data)

    async def update(
        self,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        collection = await self.get_collection()
        
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        if update_data:
            await collection.update_one(
                {"_id": db_obj.id}, {"$set": update_data}
            )
        
        updated_doc = await collection.find_one({"_id": db_obj.id})
        updated_doc["id"] = updated_doc.pop("_id")
        return self.model(**updated_doc)

    async def remove(self, *, id: str) -> ModelType:
        collection = await self.get_collection()
        doc = await collection.find_one({"_id": id})
        if doc:
            await collection.delete_one({"_id": id})
            doc["id"] = doc.pop("_id")
            return self.model(**doc)
        return None