import httpx
from fastapi import HTTPException
from typing import List

from auth.google_auth import get_auth_token
from core.config import REGION, PROJECT, MODEL_NAME, TEMPERATURE
from schemas.query import Content

# In-memory chat history store
chat_histories = {}

def get_chat_history(user_id: str) -> List[Content]:
    return chat_histories.get(user_id, [])

def update_chat_history(user_id: str, chat_history: List[Content]):
    chat_histories[user_id] = chat_history

async def generate_looker_query(user_id: str, contents: str, parameters=None):
    # Define default parameters
    default_parameters = {
        "temperature": TEMPERATURE,
        "maxOutputTokens": 1200,
        "topP": 0.8,
        "topK": 1
    }

    # Override default parameters with any provided in the request
    if parameters:
        default_parameters.update(parameters)

    # Split the prompt into system instructions and user request
    prompt_parts = contents.split("User Request\n      ----------\n")
    print(prompt_parts)
    system_prompt = prompt_parts[0]
    user_request = prompt_parts[1].strip() if len(prompt_parts) > 1 else ""

    # Get the user's chat history if user_id is available
    chat_history = get_chat_history(user_id) if user_id else []

    access_token = await get_auth_token()
    if not access_token:
        raise HTTPException(status_code=500, detail="Could not generate access token")

    url = f"https://aiplatform.googleapis.com/v1/projects/{PROJECT}/locations/{REGION}/publishers/google/models/{MODEL_NAME}:generateContent"

    payload = {
        "contents": [{"role": "user", "parts": [{"text": contents}]}],
        "generation_config": default_parameters
    }

    if user_id:
        payload["system_instruction"] = {
            "parts": [{
                "text": system_prompt
            }]
        }
        # Add the new user message to the chat history
        chat_history.append({"role": "user", "parts": [{"text": user_request}]})

        payload["contents"] = chat_history

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    print(payload)

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
    
    response_json = response.json()

    if not response_json.get('candidates') or not response_json['candidates'][0].get('content', {}).get('parts'):
        raise HTTPException(status_code=500, detail=f"Invalid response from Vertex AI: {response.text}")

    response_text = response_json['candidates'][0]['content']['parts'][0]['text']

    # Update the chat history for the user, if a user_id is present
    if user_id:
         # Add the model's response to the chat history
        chat_history.append({"role": "model", "parts": [{"text": response_text}]})

        update_chat_history(user_id, chat_history)

    return response_text
