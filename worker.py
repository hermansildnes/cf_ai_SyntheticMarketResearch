from workers import WorkerEntrypoint, Response
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from urllib.parse import urlparse

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

class Default(WorkerEntrypoint):
    async def fetch(self, request):
        # Parse the URL to extract components
        parsed_url = urlparse(request.url)

        # Create the ASGI scope
        scope = {
            "type": "http",
            "method": request.method,
            "path": parsed_url.path,
            "query_string": parsed_url.query.encode(),
            "headers": [(k.encode(), v.encode()) for k, v in request.headers.items()],
        }

        # Define the ASGI receive and send functions
        async def receive():
            body = await request.body
            return {"type": "http.request", "body": body}

        async def send(message):
            nonlocal response, response_status, response_headers
            if message["type"] == "http.response.start":
                response_status = message["status"]
                response_headers = {k.decode(): v.decode() for k, v in message["headers"]}
            elif message["type"] == "http.response.body":
                response_body = message.get("body", b"").decode("utf-8")  # Decode bytes to string
                response = Response(
                    body=response_body,
                    status=response_status,
                    headers=response_headers,
                )

        # Initialize variables
        response = None
        response_status = 500  # Default to internal server error
        response_headers = {}

        # Call the FastAPI app with the ASGI interface
        await app(scope, receive, send)
        return response