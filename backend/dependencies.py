"""Shared authentication/authorization dependencies, independent of API routers."""
import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

bearer = HTTPBearer(auto_error=False)


def current_user(request: Request, auth: HTTPAuthorizationCredentials = Depends(bearer)):
    if not auth:
        raise HTTPException(401, 'Please sign in to continue', headers={'WWW-Authenticate': 'Bearer'})
    try:
        payload = jwt.decode(auth.credentials, request.app.state.secret, algorithms=['HS256'], options={'require': ['exp', 'sub']})
        user_id = int(payload['sub'])
    except (jwt.InvalidTokenError, ValueError, KeyError, TypeError):
        raise HTTPException(401, 'Session expired or invalid. Please sign in again.')
    with request.app.state.db.connect() as conn:
        row = conn.execute('SELECT id,name,email,role FROM users WHERE id=?', (user_id,)).fetchone()
    if not row:
        raise HTTPException(401, 'Account no longer exists')
    return dict(row)


def admin_user(user=Depends(current_user)):
    if user['role'] != 'admin':
        raise HTTPException(403, 'Administrator access required')
    return user
