from fastapi import APIRouter, Depends, HTTPException, status
from app.api.dependencies import verify_api_key
from app.models.pydantic.schemas import QueryRequest, QueryResponse
from app.services.query_service import QueryService
from app.core.logging import Logger

logger = Logger()
# Create a fast API router
router = APIRouter()

# Initialise the service that orchestrates LLM + Tools
query_service = QueryService()


@router.post(
    "/query",
    response_model=QueryResponse,
    dependencies=[Depends(verify_api_key)]
)
async def ask_agent(request: QueryRequest):
    """ 
    The main entry point for the AI Agent.
    Requires an 'x-api-key' header.
    """

    logger.info(f"Received request for model: {request.model}")

    # Adding audio feature
    if request.user_voice_memo:
        # In the future: user_message = transcribe_audio(request.user_voice_memo)
        user_message = "[Voice Memo Received - Transcription Pending]"
        logger.info("Voice memo received.")
    else:
        user_message = request.user_message

    urls = request.supporting_url if request.supporting_url_exist else []

    try:
        result = query_service.process_query(
            user_text=user_message,
            model_name=request.model,
            session_id=request.session_id,
            urls=urls
        )

        if not isinstance(result, dict):
            logger.error("Invalid response from query_service")
            raise HTTPException(
                status_code=500,
                detail="Internal processing error"
            )

        return QueryResponse(
            ai_response=result.get("ai_response", "Processed successfully."),
            suggested_links=result.get("suggested_links", []),
            data=result.get("data", []),
            assistant_voice_memo=False,
            assistant_voice_file=None
        )

    except Exception as e:
        logger.error(f"Error in /query endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Something went wrong"
        )
