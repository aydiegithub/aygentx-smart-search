import json

def fix_tool_responses(tool_result_str):
    try:
        return json.loads(tool_result_str)
    except:
        return {"result": tool_result_str}
