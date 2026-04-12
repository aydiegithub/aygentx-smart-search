from fastapi import APIRouter, Depends
from app.api.dependencies import verify_api_key
from app.models.pydantic.schemas import UserQueryRequest, ProcessedResponse
from app.services.query_service import QueryService

# Create a fast API router
router = APIRouter()

# Initialise the service that orchestrates LLM + Tools
query_service = QueryService()


@router.post(
    "/query",
    response_model=ProcessedResponse,
    dependencies=[Depends(verify_api_key)]
)
async def ask_agent(request: UserQueryRequest):
    """ 
    The main entry point for the AI Agent.
    Requires an 'x-api-key' header.
    """
    # Pass the user's query into your orchestration pipeline
    result = query_service.process_query(request.query)

    # The result is already a dictionary that matches our ProcessedResponse schema
    return result
