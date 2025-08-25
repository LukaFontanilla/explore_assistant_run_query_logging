# Explore Assistant Cloud Run Service

This cloud run service provides an API for generating Looker queries using the Vertex AI Gemini Pro model. It allows users to input natural language descriptions of data queries, which the function then converts into Looker Explore URLs or query suggestions using a generative AI model.

## Directory Structure

- `main.py`: The entry point for the Cloud Run service.
- `api/`: This directory contains the API endpoints for the service.
  - `endpoints.py`: Defines the main API routes.
- `core/`: This directory contains the core configuration for the service.
  - `config.py`: Defines the environment variables used by the service.
- `services/`: This directory contains the business logic for the service.
  - `vertex_ai.py`: Contains the logic for interacting with the Vertex AI API.
- `schemas/`: This directory contains the data schemas for the service.
  - `query.py`: Defines the schema for the query request.
- `auth/`: This directory contains the authentication logic for the service.
  - `google_auth.py`: Contains the logic for authenticating with Google Cloud.

## Model configuration

By default, the cloud run service will use a default model. However, you may want to test out different Gemini models are they are released. We have made the model name configurable via an environment variable. 

In development, you can run the main script with a new MODEL_NAME variable:

```bash
PROJECT=XXXX LOCATION=us-central-1 MODEL_NAME=XXXXX TEMPERATURE=0.2 python main.py
```

In production, on the cloud run service, you can manually set a variable in the GCP UI. Updating the variable will re-deploy the cloud run service.