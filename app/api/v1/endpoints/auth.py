from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user import User, Token
from app.core.security import create_access_token
from app.core.hashing import verify_password
from app.core.hashing import get_password_hash
# from app.mobile.user import users
from app.core.config import USERNAME, PASSWORD

router = APIRouter()

#Login a user
@router.post("/login", response_model=Token)
async def login(user:User):
    try:
        # stored_user = users.get(user.email)
        stored_user = {"email": USERNAME, "password": PASSWORD}
        hashed_password = get_password_hash(stored_user["password"])
        if not stored_user or not verify_password(user.password, hashed_password):
            raise HTTPException(status_code=400, detail="Incorrect email or password")

        access_token = create_access_token(data={"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/logout")
async def logout():
    return {"message": "Logout successful"}