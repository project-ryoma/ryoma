from fastapi import APIRouter

from app.schemas import ChatResponse

router = APIRouter()


@router.post("/", response_model=ChatResponse)
def autocomplete(text: str):
    try:
        # Get the text input from the request body
        if not text:
            return {"error": "Missing text input"}, 400

        prompt = f"""
Using the chat history, complete the sentence: {text}.
Please finish the sentence beginning with the input text as it is.
Please ensure that the completed sentence starts with the exact input text.
"""

        messages = [{"role": "user", "content": prompt}]

        # Send a request to the GPT-3 API with the text input
        response = {}
        # Extract suggestions from the GPT-3 response
        suggestions = [choice.message.content.strip() for choice in response.choices]
        suggestions = list(dict.fromkeys(suggestions))

        # Return suggestions as a JSON response
        return {"suggestions": suggestions}

    except Exception as e:
        return {"error": str(e)}, 500
