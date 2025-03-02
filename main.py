from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import uvicorn
from src.image_generation import generate_draft_image, refine_image_draft
from src.llm_interaction import (
    generate_chat_response,
    generate_image_prompt,
    generate_refinement_prompt
)

app = FastAPI()

# Data model for chat messages (for interactive conversation)
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatPayload(BaseModel):
    chat_history: List[ChatMessage]

# Data model for submitting memory (conversation text)
class MemoryInput(BaseModel):
    conversation: str

# Data model for image refinement
class RefinementInput(BaseModel):
    corrections: str
    original_image_url: str

@app.post("/chat")
def chat_endpoint(payload: ChatPayload):
    """
    Receives the full conversation history and returns an assistant reply.
    Uses GPT‑4 for the chat interaction.
    """
    messages = [{"role": msg.role, "content": msg.content} for msg in payload.chat_history]
    response_text = generate_chat_response(messages)
    return {"response": response_text}

@app.post("/submit_memory")
def submit_memory(memory: MemoryInput):
    """
    Receives the conversation text, uses GPT‑40‑mini to generate an enhanced prompt,
    and calls DALL·E 3 to generate an initial draft image.
    """
    enhanced_prompt = generate_image_prompt(memory.conversation)
    draft_image_url = generate_draft_image(enhanced_prompt)
    return {"draft_image_url": draft_image_url}

@app.post("/refine_image")
def refine_image(refine: RefinementInput):
    """
    Uses GPT‑40‑mini to generate a refined image prompt based on user corrections,
    then calls DALL·E 2’s image editing API to produce an updated image.
    """
    refined_prompt = generate_refinement_prompt(refine.corrections)
    refined_image_url = refine_image_draft(refine.original_image_url, refined_prompt)
    return {"refined_image_url": refined_image_url}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
