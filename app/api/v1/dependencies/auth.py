from fastapi import Header, HTTPException
from app.core.security import verify_token

def get_current_user(authorization: str = Header(...)):
    token = authorization.split(" ")[1]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload