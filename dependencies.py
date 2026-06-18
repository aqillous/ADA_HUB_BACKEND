from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from authentication import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login" , auto_error=False)  # make sure /login exists

def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = verify_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    return payload

def get_current_admin(user=Depends(get_current_user)):
    if not user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user

