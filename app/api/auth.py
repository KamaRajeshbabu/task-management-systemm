from fastapi import APIRouter

router = APIRouter()

@router.post("/login")
async def login():
    return {"message": "login successful"}

# Add other auth routes here
