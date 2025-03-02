import openai
import os
import requests
import tempfile

openai.api_key = os.getenv("OPENAI_API_KEY", "your-openai-api-key")

def generate_draft_image(enhanced_prompt: str):
    """
    Calls OpenAI's DALL·E 3 API to generate an initial image based on the enhanced prompt.
    """
    response = openai.Image.create(
        model="dall-e-3",
        prompt=enhanced_prompt,
        n=1,
        size="1024x1024"
    )
    image_url = response["data"][0]["url"]
    return image_url

def refine_image_draft(original_image_url: str, refined_prompt: str):
    """
    Downloads the original image from its URL and calls OpenAI's image editing API (DALL·E 2)
    to generate a refined image based on the updated prompt.
    For simplicity, the same image is used as a mask.
    """
    # Download the original image
    response = requests.get(original_image_url)
    if response.status_code != 200:
        raise Exception("Failed to download original image.")
    
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_image_file:
        temp_image_file.write(response.content)
        temp_image_file_path = temp_image_file.name

    # Use the downloaded image as both the image and mask (a placeholder approach)
    with open(temp_image_file_path, "rb") as image_file, open(temp_image_file_path, "rb") as mask_file:
        edit_response = openai.Image.create_edit(
            model="dall-e-2",
            image=image_file,
            mask=mask_file,
            prompt=refined_prompt,
            n=1,
            size="1024x1024"
        )
    
    refined_image_url = edit_response["data"][0]["url"]
    return refined_image_url
