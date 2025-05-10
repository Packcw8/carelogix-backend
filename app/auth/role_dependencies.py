from fastapi import Depends, HTTPException
from app.auth.auth_dependencies import get_current_user

def require_admin(user=Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
