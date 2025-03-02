import openai
import os

# Set your OpenAI API key via environment variable or directly
openai.api_key = os.getenv("OPENAI_API_KEY", "your-openai-api-key")

def generate_chat_response(messages):
    """
    Uses GPT‑4 to generate a conversational response based on chat history.
    """
    system_prompt = {
        "role": "system",
        "content": (
            "You are a Memory Lane assistant. Engage in a friendly, interactive conversation to help the user "
            "recall details about a memorable place. Ask follow-up questions to extract details like colors, objects, "
            "layout, lighting, and mood."
        )
    }
    full_messages = [system_prompt] + messages
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=full_messages
    )
    return response.choices[0].message.content

def generate_image_prompt(conversation: str):
    """
    Uses GPT‑40‑mini to generate a detailed and vivid image prompt for DALL·E based on the user's conversation.
    """
    prompt_instructions = (
        "Based on the following conversation about a memorable place, generate a detailed image prompt for DALL·E. "
        "Include vivid descriptions of colors, objects, layout, lighting, and overall mood. The conversation is:\n\n"
        f"{conversation}\n\n"
        "Generate the image prompt:"
    )
    response = openai.chat.completions.create(
        model="gpt-40-mini",
        messages=[
            {"role": "system", "content": "You are a prompt generation assistant."},
            {"role": "user", "content": prompt_instructions}
        ]
    )
    generated_prompt = response.choices[0].message.content.strip()
    return generated_prompt

def generate_refinement_prompt(corrections: str):
    """
    Uses GPT‑40‑mini to generate an improved image prompt based on user corrections for image refinement.
    """
    prompt_instructions = (
        "Based on the following corrections or refinements provided by the user, generate an updated and more detailed "
        "image prompt for DALL·E. Include any additional details about colors, objects, or layout that would improve the image. "
        "The corrections are:\n\n"
        f"{corrections}\n\n"
        "Generate the updated image prompt:"
    )
    response = openai.chat.completions.create(
        model="gpt-40-mini",
        messages=[
            {"role": "system", "content": "You are a prompt generation assistant for image refinement."},
            {"role": "user", "content": prompt_instructions}
        ]
    )
    generated_prompt = response.choices[0].message.content.strip()
    return generated_prompt
