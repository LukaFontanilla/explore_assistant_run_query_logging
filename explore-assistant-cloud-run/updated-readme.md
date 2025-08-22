# Cloud Run Service Changes

Here is an illustration of the changes made to the Cloud Run service.

### 1. Cloud Run Service with Dockerfile

The service is set up to be deployed as a containerized application on Cloud Run.

*   **`Dockerfile`**: This file defines the container image. It uses a Python 3.11 base image, installs dependencies from `requirements.txt`, and runs the application using `uvicorn`, a fast ASGI server. This makes the application portable and easy to deploy on Cloud Run.
*   **`main.py`**: This is the entry point for the FastAPI application. It initializes the app and includes the API routes.
*   **`requirements.txt`**: This file lists the Python dependencies (like `fastapi`, `uvicorn`, `google-auth`, and `httpx`) that are installed in the Docker container.

### 2. Private Endpoint with Auth Token

The service is configured to be a private endpoint and uses an auth token to communicate with the Vertex AI API.

*   **Private Endpoint**: While the code itself doesn't enforce a private endpoint (this is a Cloud Run configuration), the application is ready to be deployed as a private service. The `test.sh` script would need to be run from within the same VPC or be modified to use Identity-Aware Proxy (IAP) to access a private Cloud Run service.
*   **`auth/google_auth.py`**: This module is responsible for obtaining a Google Auth token. The `get_auth_token` function gets a token with the `cloud-platform` scope, which is then used to authorize requests to the Vertex AI API. It also includes a simple in-memory cache for the token to improve performance.

### 3. In-Memory Chat/Session Store

The service maintains a simple in-memory chat history for each user.

*   **`services/vertex_ai.py`**:
    *   A dictionary named `chat_histories` is used as an in-memory store, with the `user_id` as the key.
    *   The `get_chat_history` and `update_chat_history` functions are used to manage the chat history for each user.
    *   In the `generate_looker_query` function, the chat history is retrieved for the user, updated with the latest user query and model response, and then stored back in the `chat_histories` dictionary.
*   **`api/endpoints.py`**: The `user_id` is extracted from the incoming request's `loggingData` and used to identify the user's session.

### 4. Cloud Logging for Each Request

Each request to generate a Looker Explore URL is logged to Cloud Logging.

*   **`api/endpoints.py`**:
    *   The standard Python `logging` library is used.
    *   A structured log entry is created as a JSON object containing the message "Explore Assistant Request" and a `data` field with the `loggingData` from the request, including the generated `explore_url`.
*   **Cloud Logging Integration**: When deployed on Cloud Run, any logs written to standard output/error (as the `logging` module does by default) are automatically sent to Cloud Logging. This structured logging approach makes it easy to search, filter, and analyze the request logs.
