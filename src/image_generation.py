from openai import OpenAI

import os
import requests
import tempfile
from PIL import Image

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "your-openai-api-key"))


def generate_draft_image(enhanced_prompt: str):
    """
    Calls OpenAI's DALL·E 3 API to generate an initial image based on the enhanced prompt.
    """
    response = client.images.generate(model="dall-e-3",
    prompt=enhanced_prompt,
    n=1,
    size="1024x1024")
    image_url = response.data[0].url
    return image_url
def refine_image_draft(original_image_url: str, refined_prompt: str):
    """
    Downloads the original image from its URL, creates a valid mask, 
    and calls OpenAI's image editing API (DALL·E 2) to generate a refined image.
    """
    # Download the original image
    response = requests.get(original_image_url)
    if response.status_code != 200:
        raise Exception("Failed to download original image.")

    # Save the original image to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_image_file:
        temp_image_file.write(response.content)
        temp_image_file_path = temp_image_file.name

    # Open the image and ensure it's in RGBA mode
    img = Image.open(temp_image_file_path).convert("RGBA")

    # Create a white mask (fully editable areas)
    mask = Image.new("L", img.size, 255)  # White mask (255 means editable)

    # Save the mask as a temporary file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_mask_file:
        mask_path = temp_mask_file.name
        mask.save(mask_path)

    # Call OpenAI's DALL·E API with the image and mask
    with open(temp_image_file_path, "rb") as image_file, open(mask_path, "rb") as mask_file:
        edit_response = client.images.edit(
            model="dall-e-2",
            image=image_file,
            mask=mask_file,
            prompt=refined_prompt,
            n=1,
            size="1024x1024"
        )

    refined_image_url = edit_response.data[0].url
    
    return refined_image_url
