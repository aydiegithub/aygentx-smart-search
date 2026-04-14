# from app.services.query_service import QueryService
# from colorama import Fore


# # def main():
# #     service = QueryService()
# #     print(Fore.CYAN + "Testing Agent Orchestration" + Fore.RESET)

# #     print(Fore.MAGENTA + "[TEST 1] Personal Question:" + Fore.RESET)
# #     q1 = "Why should I hire Adithya? What makes him stand out?"
# #     result1 = service.process_query(q1)
# #     print(f"Result: {result1}")

# #     print(Fore.MAGENTA + "\n[TEST 2] Database Question:" + Fore.RESET)
# #     q2 = "Tell me about the music track called Blue Spark."
# #     result2 = service.process_query(q2)
# #     print(f"Result: {result2}")


# # main()


import traceback

try:
    import uvicorn
    from app.api.server import app
    from mangum import Mangum

    # Lambda handler for AWS SAM / API Gateway integration
    handler = Mangum(app)
except Exception as e:
    err = traceback.format_exc()
    print("LAMBDA INIT ERROR:", err)
    def handler(event, context):
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "text/plain"},
            "body": "Initialization Error:\n" + err
        }

if __name__ == "__main__":
    print("Starting AygentX FastAPI Server...")
    # Run the FastAPI app on port 8000
    uvicorn.run("app.api.server:app", host="0.0.0.0", port=8000, reload=True)
