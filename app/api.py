from fastapi import APIRouter
from coop_utils.calculator import add, multiply

router = APIRouter()

@router.get("/add")
def add_numbers(a: int, b: int):
    return {"result": add(a, b)}

@router.get("/multiply")
def multiply_numbers(a: int, b: int):
    return {"result": multiply(a, b)}
