from fastapi import HTTPException, status


def authentication_error(message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"code": "AUTHENTICATION_FAILED", "message": message},
        headers={"WWW-Authenticate": "Bearer"},
    )


def authorization_error(message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={"code": "AUTHORIZATION_FAILED", "message": message},
    )
