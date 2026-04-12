from fastapi import APIRouter, Depends
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

    result = query_service.process_query(
        user_text=user_message,
        model_name=request.model,
        urls=urls
    )

    return QueryResponse(
        ai_response=result.get(
            "ai_response", "Processed successfully."),
        data=result.get('data', []),
        assistant_voice_memo=False,  # Set to True later when Gemini Voice is integrated TODO
        assistant_voice_file=None
    )
