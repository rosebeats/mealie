from fastapi import HTTPException


def raise_connection_error(exception: ConnectionError):
    raise HTTPException(
        500,
        detail={
            "message": "Cannot connect to voice service",
            "errorno": exception.errno,
            "exception": exception.strerror,
        },
    ) from exception
