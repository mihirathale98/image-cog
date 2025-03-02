import openai
import os
# from src.utils import parse_json_response

# Set your OpenAI API key via environment variable or directly


def routing_prompt(conversation: str):
    """
    Uses GPT-4 to generate a prompt for routing the conversation to the appropriate endpoint.
    """

    prompt = """
    The goal is to generate an image of a place based on the description provided by the user.
    
    Based on the information provided by user determine if the information is sufficient to generate an image or if you need more information to generate the image.
    If the information is sufficient route the request to the image generation endpoint. If the information is insufficient route the request to the information collection endpoint.

    Make sure atlease 3-4 turns of conversation have happened before routing to the image generation endpoint.

    conversation:
    {conversation}

    Output one of the following: 

    - "image generation"
    - "collect information"
    The output format should be in the following format:
    
    ```json
    {{"endpoint": "choice"}}
    ```

    Output:
    """

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a prompt routing assistant."},
            {"role": "user", "content": prompt.format(conversation=conversation)}
        ]
    )
    return response.choices[0].message.content

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
        model="gpt-4o-mini",
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
        model="gpt-4o-mini",
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
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a prompt generation assistant for image refinement."},
            {"role": "user", "content": prompt_instructions}
        ]
    )
    generated_prompt = response.choices[0].message.content.strip()
    return generated_prompt
