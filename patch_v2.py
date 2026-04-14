import re

with open("app/api/voice_endpoints.py", "r") as f:
    content = f.read()

old_logic = """                    if server_content is not None and server_content.model_turn:
                        for part in server_content.model_turn.parts:
                            # If gemini sends audio, forward it to the client
                            if part.inline_data and part.inline_data.mime_type.startswith("audio/"):
                                await websocket.send_bytes(part.inline_data.data)

                            # If gemini wants to use tool
                            if part.function_call:
                                tool_name = part.function_call.name
                                tool_args = part.function_call.args
                                logging.info(
                                    f"Gemini Voice called tool: {tool_name}")

                                tool_result = ""
                                if tool_name == "query_cloudflare_d1":
                                    tool_result = query_cloudflare_d1(
                                        tool_args.get("query", ""))
                                elif tool_name == "search_vectorless_rag":
                                    tool_result = search_vectorless_rag(
                                        tool_args.get("query", ""))

                                # Send the database result back to Gemini so it can speak them

                                await session.send(
                                    input=types.LiveClientToolResponse(
                                        function_responses=[
                                            types.FunctionResponse(
                                                name=tool_name,
                                                response={
                                                    "result": tool_result
                                                }
                                            )
                                        ]
                                    )
                                )"""

new_logic = """                    if server_content is not None and server_content.model_turn:
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
                            logging.info(f"Gemini Voice called tool: {tool_name}")

                            tool_result = ""
                            if tool_name == "query_cloudflare_d1":
                                tool_result = query_cloudflare_d1(tool_args.get("query", ""))
                            elif tool_name == "search_vectorless_rag":
                                tool_result = search_vectorless_rag(tool_args.get("query", ""))

                            function_responses.append(
                                types.FunctionResponse(
                                    name=tool_name,
                                    id=tool_id,
                                    response={"result": tool_result}
                                )
                            )

                        # Send the database result back to Gemini so it can speak them
                        await session.send_tool_response(function_responses=function_responses)"""

content = content.replace(old_logic, new_logic)

with open("app/api/voice_endpoints.py", "w") as f:
    f.write(content)

print("Voice endpoints tool call loop patched!")
