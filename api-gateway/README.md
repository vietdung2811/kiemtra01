# API Gateway

This is a standalone API Gateway built with FastAPI. It routes requests to the microservices of the project.

## Services Routed
- `/customer/` -> `http://localhost:8001`
- `/staff/` -> `http://localhost:8002`
- `/laptop/` -> `http://localhost:8003`
- `/mobile/` -> `http://localhost:8004`
- `/ai/` -> `http://localhost:8005`

## How to Run (Outside Docker)

1. **Navigate to the directory:**
   ```bash
   cd api-gateway
   ```

2. **(Optional) Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the gateway:**
   ```bash
   python main.py
   ```
   The gateway will be available at `http://localhost:8000`.

## Example Usage
To search for products via the gateway:
`http://localhost:8000/customer/search/`
