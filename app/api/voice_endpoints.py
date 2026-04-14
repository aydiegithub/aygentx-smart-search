import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from google import genai
from google.genai import types
from app.constants import GEMINI_LIVE_MODEL, MIME_TYPE

from app.core.config import settings
from app.core.logging import Logger
from app.constants import VOICE_AGENT_PROMPT
from app.api.mcp_server import query_cloudflare_d1, search_vectorless_rag

router = APIRouter(prefix="/voice", tags=["Voice"])
logging = Logger()

# Tools exactly as Gemini expects them
voice_tools = [{"function_declarations": [
    {
        "name": "query_cloudflare_d1",
        "description": "Query structured data about Aydie's projects, music, and skills using SQL.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {
                    "type": "STRING"
                }
            }
        }
    },
    {
        "name": "search_vectorless_rag",
        "description": "Search Aydie's personal history, background, and stories.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {
                    "type": "STRING"
                }
            }
        }
    }
]}]


@router.websocket("/stream")
async def voice_stream(websocket: WebSocket, api_key: str = Query(None)):
    """Real-time voice streaming endpoint using Gemini Multimodal Live API."""

    # Authenticate via Query Parameter for Websockets
    if api_key != settings.api_secret_key:
        await websocket.close(code=1008, reason="Unauthorized")
        return

    await websocket.accept()
    logging.info("Voice WebSocket connection opened.")

    # Initialise Gemini Client
    client = genai.Client(api_key=settings.gemini_api_key)
    system_instruction = VOICE_AGENT_PROMPT

    # Configure the Live Session
    config = types.LiveConnectConfig(
        system_instruction=types.Content(
            parts=[types.Part.from_text(
                text=system_instruction
            )]
        ),
        tools=voice_tools,
        response_modalities=["AUDIO"]  # Force it to respond with audio
    )

    try:
        # Model supporting live api
        async with client.aio.live.connect(
            model=GEMINI_LIVE_MODEL,
            config=config
        ) as session:

            # Read audio from client (front-end) and send to Gemini
            async def receive_from_client():
                try:
                    while True:
                        # Client (front-end) sends raw PCM audio bytes
                        audio_data = await websocket.receive_bytes()
                        await session.send_realtime_input(
                            media=types.Blob(
                                data=audio_data,
                                mime_type=MIME_TYPE
                            )
                        )

                except WebSocketDisconnect:
                    logging.info("Client disconnected.")
                    return

            # Read From Gemini -> Send Audio to Client (front-end) or Run Tools
            async def receive_from_gemini():
                async for response in session.receive():
                    server_content = response.server_content
                    if server_content is not None and server_content.model_turn:
                        for part in server_content.model_turn.parts:
                            # If gemini sends audio, forward it to the client
                            if part.inline_data and part.inline_data.mime_type.startswith("audio/"):
                                await websocket.send_bytes(part.inline_data.data)

                    # In google-genai 1.73+, tool calls arrive as response.tool_call
                    if response.tool_call is not None and response.tool_call.function_calls:
                        function_responses = []
                        for fn_call in response.tool_call.function_calls:
                            tool_name = fn_call.name
                            tool_args = fn_call.args
                            tool_id = fn_call.id
                            logging.info(
                                f"Gemini Voice called tool: {tool_name}")

                            tool_result = ""
                            try:
                                if tool_name == "query_cloudflare_d1":
                                    # Fallback temporarily if it fails or returns string
                                    tool_result = await asyncio.to_thread(query_cloudflare_d1, tool_args.get("query", ""), "knowledge_base", ["id"], None, None)
                                elif tool_name == "search_vectorless_rag":
                                    tool_result = await asyncio.to_thread(search_vectorless_rag, tool_args.get("query", ""))
                            except Exception as ex:
                                tool_result = f'{{"error": "{str(ex)}" }}'

                            # Parse the JSON string so Gemini receives a proper dictionary object, not a stringified JSON
                            try:
                                parsed_result = json.loads(tool_result)
                            except:
                                parsed_result = {"result": str(tool_result)}

                            function_responses.append(
                                types.FunctionResponse(
                                    name=tool_name,
                                    id=tool_id,
                                    response=parsed_result
                                )
                            )

                        # Send the database result back to Gemini so it can speak them
                        await session.send_tool_response(function_responses=function_responses)

            # SECURE CONCURRENCY FIX: Create tasks and wait for the first one to complete
            client_task = asyncio.create_task(receive_from_client())
            gemini_task = asyncio.create_task(receive_from_gemini())

            done, pending = await asyncio.wait(
                [client_task, gemini_task],
                return_when=asyncio.FIRST_COMPLETED
            )

            # Cancel any remaining background task to prevent memory leaks
            for task in pending:
                task.cancel()

    except Exception as e:
        logging.error(f"Voice Streaming Error: {e}")
    finally:
        try:
            await websocket.close()
        except:
            pass