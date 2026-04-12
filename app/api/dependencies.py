import os
from fastapi import Header, HTTPException, status

EXPECTED_API_KEY = "abcd-1234"


def verify_api_key(x_api_key: str = Header(default=None)):
    """
    FastAPI Dependency to verify the API key provided in the headers.
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key header (x-api-key) is missing"
        )

    if x_api_key != EXPECTED_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )

    return x_api_key
