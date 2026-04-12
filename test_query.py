import asyncio
from app.services.query_service import QueryService
from app.models.pydantic.schemas import QueryRequest

async def main():
    service = QueryService()
    req = QueryRequest(query="Tell me about the project nyc-taxi", session_id="test1234", model_name="gemini-3.1-flash-lite-preview")
    res = await service.process_query(req)
    print(res)

asyncio.run(main())
