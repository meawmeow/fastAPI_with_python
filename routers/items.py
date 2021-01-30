from typing import List
from enum import Enum
from typing import Optional

from fastapi import APIRouter
from fastapi import FastAPI,Path,Query,Body,Header,status,UploadFile,File,HTTPException,Request,Depends
from pydantic import BaseModel,Field


app = FastAPI()
router = APIRouter()

class TypeName(str, Enum):
    TYPE_A = "a"
    TYPE_B = "b"
    TYPE_C = "c"

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: float = 10.5
    tags: List[str] = []

class User(BaseModel):
    username: str
    full_name: Optional[str] = None

class Skils(BaseModel):
    java:Optional[int] = Field(
        None, title="between 5 to 10", ge=5, le=10
    )
    kotlin:Optional[int] = Field(
        None, title="between 5 to 10", ge=5, le=10
    )

class Person(BaseModel):
    name:str
    kg:int
    cm:int
    skills:Optional[Skils] = None

items = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
    "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},
}

#List
@router.get("/items/",tags=["items"])
async def read_items(q: List[str] = Query(["num1", "num2"])):
    query_items = {"q": q}
    return query_items

#Path
@router.get("/items/path/{item_id}",tags=["items"])
async def read_items_path(
    *, item_id: int = Path(..., title="request length betweens 5 to 10", ge=5, le=10),
    q: Optional[str] = Query(None, alias="item-query"),
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results

#Optional Query
@router.get("/items/{item_id}",tags=["items"])
def read_item(item_id: int, q: Optional[str] = Query(None,title="Query string",min_length=3, max_length=10)):
    return {"item_id": item_id, "q": q}

#Example Value Schema
@router.put("/items/{item_id}",tags=["items"])
def update_item(item_id: int, item: Item,user:User=Body(
        ...,
        example={
           "item": {
            "name": "my name is..",
            "price": '0',
            "is_offer": 'true'
            },
            "user": {
            "username": "string",
            "full_name": "full name"
            }
        },)):
    results = {'id':item_id,'user':user,'item':item}
    return results

#params
@router.get("/items/type/{type_name}/number/{number}",tags=["items"])
async def get_type(type_name: TypeName,number:int):
    if type_name == TypeName.TYPE_A:
        return {"Type": type_name, "message": "type name is a , "*number}

    if type_name.value == "b":
        return {"Type": type_name, "message": "type name is b , "*number}

    return {"Type": type_name, "message": "type name is c , "*number}

#status code
@router.post("/items/",status_code=status.HTTP_201_CREATED,tags=["items"])
async def create_item(item: Item):
    item_dict = item.dict()
    full_name = "My name is "+item.name+" ackerman"
    item_dict.update({'full name':full_name})
    return item_dict

#put
@router.put("/items/person/{item_id}",deprecated=True,tags=["items"])
async def update_item_person(item_id: int, person: Person):
    results = {"item_id": item_id, "person": person}
    return results

#Header
@router.get("/items/",tags=["items"])
async def read_items(
    user_agent: Optional[str] = Header(None),
    x_token: Optional[List[str]] = Header(None)):
    results= {"User-Agent": user_agent,'X-Token values':x_token}
    return results

#Response Model HTTPException
@router.get("/items/item_strID/{item_id}", response_model=Item, response_model_exclude_unset=True,tags=["items"])
async def read_item_byID(item_id: str):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return items[item_id]

#UploadFile
@router.post("/items/uploadfile/",
    summary="My Upload file",
    description="Description file, Upload file",tags=["items"])
async def create_upload_file(file: UploadFile = File(...)):
    return {"filename": file.filename}

#Custom exception handlers
class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name

@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={"message": f"Oops! {exc.name} did something. There goes a rainbow..."},
    )

@router.get("/items/unicorns/{name}",tags=["items"])
async def read_unicorn(name: str):
    if name == "error":
        raise UnicornException(name=name)
    return {"unicorn_name": name}
