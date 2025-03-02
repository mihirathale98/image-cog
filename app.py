import streamlit as st
import requests
import time

# URL of the FastAPI backend
backend_url = "http://localhost:8000"

st.set_page_config(page_title="Memory Lane - Interactive Chat Therapy", layout="wide")
st.title("Memory Lane - Interactive Chat Therapy")

# Initialize session state variables
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": "Welcome to Memory Lane! I'm here to help you explore and visualize your memories of special places. Tell me about a place that's meaningful to you, and I can help create an image of it. What place would you like to talk about today?"
        }
    ]
if "current_image_url" not in st.session_state:
    st.session_state.current_image_url = None
if "image_ready" not in st.session_state:
    st.session_state.image_ready = False
if "show_draft_button" not in st.session_state:
    st.session_state.show_draft_button = False

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "image_url" in message:
            st.image(message["image_url"], use_column_width=True)

# Chat input
prompt = st.chat_input("Say something about a memorable place...")

# Function to generate draft image
def generate_draft_image():
    # Combine all user messages to form the conversation text
    conversation_text = "\n".join(
        [msg["content"] for msg in st.session_state.messages if msg["role"] == "user"]
    )
    
    payload = {"conversation": conversation_text}
    
    with st.spinner("Generating draft image..."):
        response = requests.post(f"{backend_url}/submit_memory", json=payload)
    
    if response.ok:
        image_url = response.json().get("draft_image_url")
        
        # Add image to message
        response_message = {
            "role": "assistant",
            "content": "I've created a draft image based on your memory. What do you think? Would you like to make any refinements?",
            "image_url": image_url
        }
        st.session_state.messages.append(response_message)
        st.session_state.current_image_url = image_url
        st.session_state.image_ready = True
        st.session_state.show_draft_button = False
    else:
        st.error("Failed to generate draft image.")

# Function to refine image
def refine_image(corrections):
    payload = {
        "corrections": corrections,
        "original_image_url": st.session_state.current_image_url
    }
    
    with st.spinner("Refining image..."):
        response = requests.post(f"{backend_url}/refine_image", json=payload)
    
    if response.ok:
        refined_image_url = response.json().get("refined_image_url")
        
        # Add refined image to messages
        response_message = {
            "role": "assistant",
            "content": f"I've refined the image based on your feedback. Is this closer to what you had in mind?",
            "image_url": refined_image_url
        }
        st.session_state.messages.append(response_message)
        st.session_state.current_image_url = refined_image_url
    else:
        st.error("Failed to refine the image.")

# Button for generating image (appears contextually)
if st.session_state.show_draft_button:
    if st.button("Generate Image from My Memory"):
        generate_draft_image()

# Process user input
if prompt:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Prepare to send to backend
    payload = {"chat_history": st.session_state.messages}
    
    # Send to backend
    with st.spinner("Thinking..."):
        response = requests.post(f"{backend_url}/chat", json=payload)
    
    if response.ok:
        assistant_reply = response.json().get("response")
        
        # Check if assistant is asking to generate image
        suggest_image = any(phrase in assistant_reply.lower() for phrase in [
            "generate a draft", "create a draft", "should i create a draft", 
            "would you like to see", "generate an image", "create an image",
            "should i generate an image"
        ])
        
        # Add assistant message
        response_message = {
            "role": "assistant",
            "content": assistant_reply
        }
        st.session_state.messages.append(response_message)
        
        # Show draft button if suggested
        if suggest_image:
            st.session_state.show_draft_button = True
        
    else:
        st.error("Error in receiving chat response.")

# Only show refinement controls when we have an image
if st.session_state.image_ready and st.session_state.current_image_url:
    with st.expander("Refine this image"):
        corrections = st.text_area("What would you like to change about the image?")
        if st.button("Submit Refinements"):
            if corrections.strip():
                # First add user message with corrections
                st.session_state.messages.append({"role": "user", "content": corrections})
                refine_image(corrections)
            else:
                st.warning("Please enter some refinements")