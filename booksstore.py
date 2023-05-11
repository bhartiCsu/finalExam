from pydantic import BaseModel
from fastapi import FastAPI

app = FastAPI()
class booksstore(BaseModel):
    title: str
    author: str
    description: str
    price: float
    stock: int
    sales: int
