import os
import requests
import tempfile
from PIL import Image
from PIL import ImageDraw
from src.llm_interaction import generate_mask
from src.utils import parse_json_response
from ast import literal_eval

def get_coords(mask_response):
    coords = parse_json_response(mask_response)['mask']
    print("coords", coords)
    return coords

def generate_draft_image(enhanced_prompt: str):
    """
    Calls Replicate's Flux model to generate an initial image based on the enhanced prompt.
    """
    model = replicate.models.get("black-forest-labs/flux-1.1-pro-ultra")
    output = model.predict(prompt=enhanced_prompt, width=1024, height=1024)
    image_url = output[0]
    return image_url

import replicate

def refine_image_draft(original_image_url: str, refined_prompt: str):
    """
    Downloads the original image from its URL, creates a valid mask, 
    and calls Replicate's Flux Fill model to generate a refined image.
    """
    print("refined_prompt", refined_prompt)

    response = requests.get(original_image_url)
    if response.status_code != 200:
        raise Exception("Failed to download original image.")

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_image_file:
        temp_image_file.write(response.content)
        temp_image_file_path = temp_image_file.name

    img = Image.open(temp_image_file_path).convert("RGBA")

    mask = Image.new("L", img.size, 255)  # White mask (255 means editable)

    draw = ImageDraw.Draw(mask)

    mask_coords = generate_mask(temp_image_file_path, refined_prompt)
    coords = literal_eval(get_coords(mask_coords))
    transparent_area = (coords[0], coords[1], coords[2], coords[3])

    draw.rectangle(transparent_area, fill=0)

    # Save the mask as a temporary file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_mask_file:
        mask_path = temp_mask_file.name
        mask.save(mask_path)

    # Call Replicate's Flux Fill model with the image and mask
    model = replicate.models.get("black-forest-labs/flux-fill-dev")
    with open(temp_image_file_path, "rb") as image_file, open(mask_path, "rb") as mask_file:
        output = model.predict(
            prompt=refined_prompt,
            image=image_file,
            mask=mask_file
        )

    refined_image_url = output[0]
    print(f"Refined image URL: {refined_image_url}")
    return refined_image_url
