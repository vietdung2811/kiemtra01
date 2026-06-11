from fastapi import FastAPI, Request, Response
import httpx
import logging

app = FastAPI(title="Project API Gateway")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Service URLs (Assuming services are running on these names in the docker network)
SERVICES = {
    "customer": "http://customer_service:8001",
    "staff": "http://staff_service:8002",
    "laptop": "http://laptop_service:8003",
    "mobile": "http://mobile_service:8004",
    "ai": "http://ai-service:8005",
}

@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def gateway(service: str, path: str, request: Request):
    if service not in SERVICES:
        return Response(content=f"Service '{service}' not found", status_code=404)

    base_url = SERVICES[service]
    url = f"{base_url}/{path}"
    
    # Extract just the hostname for the internal Host header
    # e.g., "http://customer_service:8001" -> "customer_service"
    internal_host = base_url.split("://")[-1].split(":")[0]

    # Append query parameters if any
    query_params = request.query_params
    if query_params:
        url += f"?{query_params}"

    logger.info(f"Routing request to {service}: {url}")

    async with httpx.AsyncClient() as client:
        try:
            # Prepare request data
            body = await request.body()
            headers = dict(request.headers)
            
            # Set forwarding headers
            original_host = headers.get("host", "localhost")
            headers["X-Forwarded-Host"] = original_host
            
            # DO NOT set the 'host' header manually. 
            # httpx will automatically set the Host header based on the target URL (e.g., customer_service:8001)
            # which is what Django expects when not behind a proxy that sets X-Forwarded-Host.
            headers.pop("host", None)

            # Forward the request
            response = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=body,
                timeout=10.0
            )

            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
        except httpx.RequestError as exc:
            logger.error(f"Error connecting to {service}: {exc}")
            return Response(content=f"Error connecting to service: {str(exc)}", status_code=502)

@app.get("/")
async def root():
    return {
        "message": "API Gateway is running",
        "services": list(SERVICES.keys())
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
