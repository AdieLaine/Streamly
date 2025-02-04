import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import os
from gtts import gTTS
from google.generativeai.types import GenerateContentResponse  # Add this import

# Google AI API setup
GOOGLE_API_KEY = st.secrets["google"]["api_key"]
GOOGLE_PROJECT_ID = st.secrets["google"]["project_id"] # Make sure you create one in the Google AI platform
genai.configure(api_key=GOOGLE_API_KEY)
# Model setup
gemini_pro_vision_model = genai.GenerativeModel("gemini-pro-vision")
gemini_pro_model = genai.GenerativeModel("gemini-pro")

# Function to generate an image using Gemini
def gemini_generate_image(text_input):
    try:
       
        response = gemini_pro_vision_model.generate_content(
             [ text_input,
                {
                  "mime_type": "image/png",  # Or "image/jpeg" if you prefer
                   "data":  None,  # No image input, just text
                }
                ]
            )
        response.resolve()
        if response.text :
           return response.text
        else : 
           st.error(f"Image generation error: Unable to generate image.")
           return None
    except Exception as e:
        st.error(f"Image generation error: {e}")
        return None


# Function to caption an image using Gemini
def gemini_caption_image(image_bytes):
    try:
        image_part = {"mime_type": "image/jpeg", "data": image_bytes}
        prompt = "Describe this image in detail."
        response = gemini_pro_vision_model.generate_content([prompt, image_part])
        response.resolve()
        if response.text:
          return response.text
        else:
           st.error(f"Captioning error: Unable to get caption.")
           return None
    except Exception as e:
        st.error(f"Captioning error: {e}")
        return None


# Function to handle chatbot conversation
def gemini_chatbot(prompt):
     try:
        response = gemini_pro_model.generate_content(prompt, stream=False)
        response.resolve()
        if response.text:
            return response.text
        else:
            st.error(f"Chatbot error: Unable to get response.")
            return "I'm sorry, I couldn't generate a response."
     except Exception as e:
        st.error(f"Chatbot error: {e}")
        return "I'm sorry, I couldn't generate a response."


# Function to convert text to speech using gTTS
def text_to_speech(text):
    try:
        tts = gTTS(text, lang='en')
        tts_file = "story.mp3"
        tts.save(tts_file)
        return tts_file
    except Exception as e:
        st.error(f"Text-to-Speech error: {e}")
        return None

# Function to translate text from English to Arabic using Gemini
def translate_to_arabic(text):
    try:
        prompt = f"Translate the following English text to Arabic: {text}"
        response = gemini_pro_model.generate_content(prompt)
        response.resolve()
        if response.text:
           return response.text
        else :
           st.error(f"Translation error: Unable to get translation.")
           return None
    except Exception as e:
        st.error(f"Translation error: {e}")
        return None

# Function to generate music using Gemini (placeholder, as Gemini does not generate audio currently)
def generate_music(genre_input):
    st.warning("Music generation is not supported with Gemini. Please enter a text description of the music instead.")
    try :
       prompt = f"Please describe music with the following properties: {genre_input}"
       response = gemini_pro_model.generate_content(prompt)
       response.resolve()
       if response.text:
           return response.text
       else :
           st.error(f"Music generation error: unable to get music description")
           return None
    except Exception as e :
      st.error(f"Music generation error: {e}")
      return None


# Enhanced Streamlit UI
st.set_page_config(page_title="Creative AI Suite", page_icon="🎨", layout="wide")

st.title("🎨 Creative AI Suite")
st.markdown("Unlock the power of AI for **image generation**, **story creation**, **music generation**, and **speech conversion**.")

# Use session state to preserve the selected option
if 'option' not in st.session_state:
    st.session_state.option = None  # Initialize the option

# Row layout for options
# Row layout for options
st.header("Choose an option:")
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    if st.button("Create an Image and Story", key="create_image_story"):
        st.session_state.option = "Create an Image and Story from Your Description"

with col2:
    if st.button("Interactive AI Chat", key="interactive_ai_chat"):
        st.session_state.option = "Interactive AI Chat"

with col3:
    if st.button("Convert Text to Speech", key="convert_text_to_speech"):
        st.session_state.option = "Convert Text to Speech"

with col4:
    if st.button("Generate an Image", key="generate_image"):
        st.session_state.option = "Generate an Image"

with col5:
    if st.button("Translate to Arabic", key="translate_to_arabic"):
        st.session_state.option = "Translate to Arabic"

with col6:
    if st.button("Generate Music", key="generate_music"):
        st.session_state.option = "Generate Music"


# Add help tooltips to guide users
st.info("Select an option to interact with the AI tools.")

# Option handling
if st.session_state.option == "Create an Image and Story from Your Description":
    st.subheader("🖼️ Create an Image and Story")
    st.markdown("Describe the image you want, and we'll generate it for you along with a creative story.")
    description_input = st.text_input("🔎 Describe the image you want:")
    
    if st.button("Generate Image"):
        if description_input:
            with st.spinner("Generating image..."):
                generated_image = gemini_generate_image(description_input)
                if generated_image:
                    st.image(generated_image, caption="Generated Image", use_column_width=True)

                    with st.spinner("✍️ Generating caption..."):
                        caption = gemini_caption_image(generated_image)
                    
                    if caption:
                        title = caption
                        st.write("### 🖋️ Caption (Title):", title)

                        with st.spinner("📖 Generating story..."):
                            story_script = gemini_chatbot(f"Write a creative and useful story about: {title}.")
                            st.markdown("### 📜 Story Script:")
                            st.write(story_script)

                            # Translate the generated story to Arabic
                            with st.spinner("🌍 Translating story to Arabic..."):
                                arabic_translation = translate_to_arabic(story_script)
                            
                            if arabic_translation:
                                st.markdown("### 🌍 Arabic Translation:")
                                st.write(arabic_translation)

                        with st.spinner("🔊 Converting story to speech..."):
                            audio_file = text_to_speech(story_script)

                        if audio_file:
                            st.audio(audio_file, format="audio/mp3")
                            os.remove(audio_file)  # Cleanup after playing
                    else:
                        st.error("⚠️ Unable to generate caption for the image.")
        else:
            st.warning("Please provide a description to generate the image.")  

elif st.session_state.option == "Interactive AI Chat":
    st.subheader("🤖 Interactive AI Chat")
    st.markdown("Ask the AI any question, and it will respond with a creative answer.")
    user_input = st.text_input("💬 Enter your question or prompt:")
    
    if st.button("🚀 Submit"):
        if user_input:
            with st.spinner("🤖 AI is generating a response..."):
                response = gemini_chatbot(user_input)
                if response:
                    st.markdown("### 💡 AI Response:")
                    st.success(f"🤖 {response}")  # Use emoji to enhance the feedback
        else:
            st.warning("Please enter a prompt to get started!")

elif st.session_state.option == "Generate an Image":
    st.subheader("🖼️ Generate an Image")
    st.markdown("Describe the image, and we will generate it for you.")
    image_description = st.text_input("🔎 Describe the image you want:")
    
    if st.button("Generate Image"):
        if image_description:
            with st.spinner("🔄 Generating image..."):
                generated_image = gemini_generate_image(image_description)
                if generated_image:
                    st.image(generated_image, caption="Generated Image", use_column_width=True)

elif st.session_state.option == "Convert Text to Speech":
    st.subheader("🔊 Convert Text to Speech")
    st.markdown("Enter text to convert it into natural-sounding speech.")
    text_to_convert = st.text_area("📝 Enter the text you want to convert to speech:")
    
    if st.button("Convert"):
        if text_to_convert:
            with st.spinner("🔊 Converting text to speech..."):
                audio_file = text_to_speech(text_to_convert)
                if audio_file:
                    st.audio(audio_file, format="audio/mp3")
                    os.remove(audio_file)
        else:
            st.warning("Please enter the text to convert.")

elif st.session_state.option == "Translate to Arabic":
    st.subheader("🌍 Translate Text to Arabic")
    st.markdown("Enter the text you want to translate from English to Arabic.")
    text_to_translate = st.text_area("📝 Enter the text you want to translate:")
    
    if st.button("Translate"):
        if text_to_translate:
            with st.spinner("🌍 Translating text..."):
                arabic_translation = translate_to_arabic(text_to_translate)
                if arabic_translation:
                    st.markdown("### 🌍 Arabic Translation:")
                    st.write(arabic_translation)
        else:
            st.warning("Please enter the text to translate.")

elif st.session_state.option == "Generate Music":
    st.subheader("🎵 Generate Music")
    st.markdown("Enter a description of the music you want, and the AI will generate it for you.")
    genre_description = st.text_input("🔎 Describe the music genre or vibe:")
    
    if st.button("Generate Music"):
        if genre_description:
           with st.spinner("🎵 Generating music description..."):
                generated_music = generate_music(genre_description)
                if generated_music:
                     st.write(f"AI generated text description of music: {generated_music}")
        else:
            st.warning("Please provide a description to generate music.")