import logging
from fastapi import APIRouter, Request, Response, HTTPException

from schemas.query import QueryRequest
from services.vertex_ai import generate_looker_query

router = APIRouter()

@router.post("/")
async def base(request: Request, query_request: QueryRequest):
    try:
        user_id = None
        print("Request: ", query_request)
        if query_request.loggingData:
            user_id = query_request.loggingData.get('user')
            if not user_id:
                raise HTTPException(status_code=400, detail="User ID not found in loggingData")

        response_text = await generate_looker_query(user_id, query_request.contents, query_request.parameters)

        if query_request.loggingData:
            logging_data = query_request.loggingData
            logging_data['explore_url'] = response_text
            logging.info({"message": "Explore Assistant Request", "data": logging_data})

        return Response(content=response_text, media_type="text/plain")
    except Exception as e:
        logging.error(f"Internal server error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.options("/")
def options():
    return Response(status_code=204)