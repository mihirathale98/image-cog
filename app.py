import streamlit as st
import requests
import time

backend_url = "http://localhost:8000"

st.set_page_config(page_title="Memory Lane", layout="wide")
st.title("Memory Lane")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": "Welcome to Memory Lane! I'm here to help you explore and visualize your memories of special places. Tell me about a place that's meaningful to you, and I can help create an image of it. What place would you like to talk about today?"
        }
    ]
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "image_url" in message:
                st.image(message["image_url"], use_column_width=True)

if "current_image_url" not in st.session_state:
    st.session_state.current_image_url = None
if "image_ready" not in st.session_state:
    st.session_state.image_ready = False
if "show_draft_button" not in st.session_state:
    st.session_state.show_draft_button = False




def generate_draft_image():
    conversation_text = "\n".join(
        [msg["content"] for msg in st.session_state.messages if msg["role"] == "user"]
    )
    
    payload = {"conversation": conversation_text}
    
    with st.spinner("Generating draft image..."):
        response = requests.post(f"{backend_url}/submit_memory", json=payload)
    
    if response.ok:
        image_url = response.json().get("draft_image_url")
        st.session_state.original_prompt = response.json().get("enhanced_prompt")
        
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

def refine_image(corrections):
    payload = {
        "original_prompt": st.session_state.original_prompt,
        "corrections": corrections,
        "original_image_url": st.session_state.current_image_url
    }
    
    with st.spinner("Refining image..."):
        response = requests.post(f"{backend_url}/refine_image", json=payload)
    
    if response.ok:
        refined_image_url = response.json().get("refined_image_url")
        
        response_message = {
            "role": "assistant",
            "content": f"I've refined the image based on your feedback. Is this closer to what you had in mind?",
            "image_url": refined_image_url
        }
        st.session_state.messages.append(response_message)
        st.session_state.current_image_url = refined_image_url
    else:
        st.error("Failed to refine the image.")


prompt = st.chat_input("Say something about a memorable place...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    payload = {"chat_history": st.session_state.messages}

    if st.session_state.current_image_url == None:

        route_response = requests.post(f"{backend_url}/route", json=payload)
        if route_response.ok:
            route_response = route_response.json().get("response")['endpoint']
        
        if route_response == "image generation":
            st.session_state.show_draft_button = True
            generate_draft_image()

        else:
        
            with st.spinner("Thinking..."):
                response = requests.post(f"{backend_url}/chat", json=payload)
        
                if response.ok:
                    assistant_reply = response.json().get("response")
                    
                    response_message = {
                        "role": "assistant",
                        "content": assistant_reply
                    }
                    st.session_state.messages.append(response_message)
                    
                else:
                    st.error("Error in receiving chat response.")
                    
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        payload = {"chat_history": st.session_state.messages}
        refine_image(prompt)
    
    if st.session_state.messages:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "image_url" in message:
                    st.image(message["image_url"], use_column_width=True)





# if st.session_state.image_ready and st.session_state.current_image_url:
#     with st.expander("Refine this image"):
#         corrections = st.text_area("What would you like to change about the image?")
#         if st.button("Submit Refinements"):
#             if corrections.strip():
#                 st.session_state.messages.append({"role": "user", "content": corrections})
#                 refine_image(corrections)
#             else:
#                 st.warning("Please enter some refinements")
    
#     if st.session_state.messages:
#         for message in st.session_state.messages:
#             with st.chat_message(message["role"]):
#                 st.markdown(message["content"])
#                 if "image_url" in message:
#                     st.image(message["image_url"], use_column_width=True)