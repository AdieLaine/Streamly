import logging
import streamlit as st
import openai
from langchain.adapters import openai as lc_openai
from PIL import Image, ImageEnhance
import time
import json
import requests
import base64

logging.basicConfig(level=logging.INFO)

# Streamlit Page Configuration
st.set_page_config(
    page_title="Streamly Streamlit Assistant",
    page_icon="imgs/avatar_streamly.png",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get help": "https://github.com/AdieLaine/Streamly",
        "Report a bug": "https://github.com/AdieLaine/Streamly",
        "About": """
            ## Streamly Streamlit Assistant
            
            **GitHub**: https://github.com/AdieLaine/
            
            The AI Assistant named, Streamly, aims to provide the latest updates from Streamlit,
            generate code snippets for Streamlit widgets,
            and answer questions about Streamlit's latest features, issues, and more.
            Streamly has been trained on the latest Streamlit updates and documentation.
        """
    }
)

# Streamlit Updates and Expanders
st.title("Streamly Streamlit Assistant")

API_DOCS_URL = "https://docs.streamlit.io/library/api-reference"

@st.cache_data(show_spinner=False)
def long_running_task(duration):
    """
    Simulates a long-running operation.
    """
    time.sleep(duration)
    return "Long-running operation completed."

@st.cache_data(show_spinner=False)
def load_and_enhance_image(image_path, enhance=False):
    """
    Load and optionally enhance an image.

    Parameters:
    - image_path: str, path of the image
    - enhance: bool, whether to enhance the image or not

    Returns:
    - img: PIL.Image.Image, (enhanced) image
    """
    img = Image.open(image_path)
    if enhance:
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.8)
    return img

@st.cache_data(show_spinner=False)
def load_streamlit_updates():
    """Load the latest Streamlit updates from a local JSON file."""
    try:
        with open("data/streamlit_updates.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

@st.cache_data(show_spinner=False)
def get_latest_update_from_json(keyword, latest_updates):
    """
    Fetch the latest Streamlit update based on a keyword.

    Parameters:
        keyword (str): The keyword to search for in the Streamlit updates.
        latest_updates (dict): The latest Streamlit updates data.

    Returns:
        str: The latest update related to the keyword, or a message if no update is found.
    """
    for section in ["Highlights", "Notable Changes", "Other Changes"]:
        for sub_key, sub_value in latest_updates.get(section, {}).items():
            for key, value in sub_value.items():
                if keyword.lower() in key.lower() or keyword.lower() in value.lower():
                    return f"Section: {section}\nSub-Category: {sub_key}\n{key}: {value}"

    return "No updates found for the specified keyword."

def get_streamlit_api_code_version():
    """
    Get the current Streamlit API code version from the Streamlit API documentation.

    Returns:
        str: The current Streamlit API code version.
    """
    try:
        response = requests.get(API_DOCS_URL)
        if response.status_code == 200:
            return "1.28.0"
    except requests.exceptions.RequestException as e:
        print("Error connecting to the Streamlit API documentation:", str(e))
    return None

def display_streamlit_updates():
    """It displays the latest updates of the Streamlit."""
    with st.expander("Streamlit 1.28 Announcement", expanded=False):
        image_path = "imgs/streamlit128.png"
        enhance = st.checkbox("Enhance Image?", False)
        img = load_and_enhance_image(image_path, enhance)
        st.image(img, caption="Streamlit 1.28 Announcement", use_column_width="auto", clamp=True, channels="RGB", output_format="PNG")
        st.markdown("For more details on this version, check out the [Streamlit Forum post](https://discuss.streamlit.io/t/version-1-28-0/54194).")

def img_to_base64(image_path):
    """Convert image to base64"""
    with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()

@st.cache_data(show_spinner=False)
def on_chat_submit(chat_input, api_key, latest_updates, use_langchain=False):
    """
    Handle chat input submissions and interact with the OpenAI API.

    Parameters:
        chat_input (str): The chat input from the user.
        api_key (str): The OpenAI API key.
        latest_updates (dict): The latest Streamlit updates fetched from a JSON file or API.
        use_langchain (bool): Whether to use LangChain OpenAI wrapper.

    Returns:
        None: Updates the chat history in Streamlit's session state.
    """
    user_input = chat_input.strip().lower()

    # Initialize the OpenAI API
    openai.api_key = api_key
    model_engine = "gpt-3.5-turbo"

    # Initialize the conversation history with system and assistant messages
    if 'conversation_history' not in st.session_state:
        assistant_message = "Hello! I am Streamly. How can I assist you with Streamlit today?"
        formatted_message = []
        highlights = latest_updates.get("Highlights", {})
        
        # Include version info in highlights if available
        version_info = highlights.get("Version 1.28", {})
        if version_info:
            description = version_info.get("Description", "No description available.")
            formatted_message.append(f"- **Version 1.28**: {description}")

        for category, updates in latest_updates.items():
            formatted_message.append(f"**{category}**:")
            for sub_key, sub_values in updates.items():
                if sub_key != "Version 1.28":  # Skip the version info as it's already included
                    description = sub_values.get("Description", "No description available.")
                    documentation = sub_values.get("Documentation", "No documentation available.")
                    formatted_message.append(f"- **{sub_key}**: {description}")
                    formatted_message.append(f"  - **Documentation**: {documentation}")

        assistant_message += "\n".join(formatted_message)
        
        # Initialize conversation_history
        st.session_state.conversation_history = [
            {"role": "system", "content": "You are Streamly, a specialized AI assistant trained in Streamlit and the current update and version 1.28."},
            {"role": "system", "content": "Refer to conversation history to provide context to your reponse."},
            {"role": "system", "content": "Use the streamlit_updates.json local file to look up the latest Streamlit feature updates."},
            {"role": "assistant", "content": assistant_message}
        ]


    # Append user's query to conversation history
    st.session_state.conversation_history.append({"role": "user", "content": user_input})

    try:
        # Logic for assistant's reply
        assistant_reply = ""

        if use_langchain:
            # LangChain OpenAI wrapper call
            lc_result = lc_openai.ChatCompletion.create(
                messages=st.session_state.conversation_history,
                model=model_engine,
                temperature=0
            )
            assistant_reply = lc_result["choices"][0]["message"]["content"]

        else:
            if "latest updates" in user_input:
                assistant_reply = "Here are the latest highlights from Streamlit:\n"
                highlights = latest_updates.get("Highlights", {})
                if highlights:
                    for version, info in highlights.items():
                        description = info.get("Description", "No description available.")
                        assistant_reply += f"- **{version}**: {description}\n"
            else:
                
                # Direct OpenAI API call
                response = openai.ChatCompletion.create(
                    model=model_engine,
                    messages=st.session_state.conversation_history
                )
                
                assistant_reply = response["choices"][0]["message"]["content"]

            # Append assistant's reply to the conversation history
            st.session_state.conversation_history.append({"role": "assistant", "content": assistant_reply})

        # Update the Streamlit chat history
        if "history" in st.session_state:
            st.session_state.history.append({"role": "user", "content": user_input})
            st.session_state.history.append({"role": "assistant", "content": assistant_reply})

    except openai.error.OpenAIError as e:
        logging.error(f"Error occurred: {e}")
        error_message = f"OpenAI Error: {str(e)}"
        st.error(error_message)
        st.session_state.history.append({"role": "assistant", "content": error_message})

def main():
    """
    Display Streamlit updates and handle the chat interface.
    """
    # Initialize session state variables for chat history and conversation history
    if "history" not in st.session_state:
        st.session_state.history = []
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []

    # Initialize the chat with a greeting and Streamlit updates if the history is empty
    if not st.session_state.history:
        latest_updates = load_streamlit_updates()  # This function should be defined elsewhere to load updates
        initial_bot_message = "Hello! How can I assist you with Streamlit today? Here are some of the latest highlights:\n"
        updates = latest_updates.get("Highlights", {})
        if isinstance(updates, dict):  # Check if updates is a dictionary
            initial_bot_message = "### Latest Streamlit Highlights:\n"
            for key, value in updates.items():
                description = value.get("Description", "No description available.")
                documentation = value.get("Documentation", "No documentation available.")
                initial_bot_message += f"- **{key}**: {description}\n  - **Documentation**: {documentation}\n"
            st.session_state.history.append({"role": "assistant", "content": initial_bot_message})
            st.session_state.conversation_history = [
                {"role": "system", "content": "You are Streamly, a specialized AI assistant trained in Streamlit and the current update and version 1.28."},
                {"role": "system", "content": "Refer to conversation history to provide context to your reponse."},
                {"role": "system", "content": "Use the streamlit_updates.json local file to look up the latest Streamlit feature updates."},
                {"role": "system", "content": "When responding, provide code examples, links to documentation, and code examples from Streamlit API to help the user."},
                {"role": "assistant", "content": initial_bot_message}
            ]
        else:
            st.error("Unexpected structure for 'Highlights' in latest updates.")
    
    # Inject custom CSS for glowing border effect
    st.markdown(
        """
        <style>
        .cover-glow {
            width: 100%;
            height: auto;
            padding: 3px;
            box-shadow: 
                0 0 5px #330000,
                0 0 10px #660000,
                0 0 15px #990000,
                0 0 20px #CC0000,
                0 0 25px #FF0000,
                0 0 30px #FF3333,
                0 0 35px #FF6666;
            position: relative;
            z-index: -1;
            border-radius: 30px;  /* Rounded corners */
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Function to convert image to base64
    def img_to_base64(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()

    # Load and display sidebar image with glowing effect
    img_path = "imgs/sidebar_streamly_avatar.png"
    img_base64 = img_to_base64(img_path)
    st.sidebar.markdown(
        f'<img src="data:image/png;base64,{img_base64}" class="cover-glow">',
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")
    
    # Sidebar for Mode Selection
    mode = st.sidebar.radio("Select Mode:", options=["Latest Updates", "Chat with Streamly"], index=1)
    use_langchain = st.sidebar.checkbox("Use LangChain OpenAI Adapter 🦜️🔗 ", value=False)
    st.sidebar.markdown("---")
    # Toggle checkbox in the sidebar for basic interactions
    show_basic_info = st.sidebar.toggle("Show Basic Interactions", value=True)

    # Display the st.info box if the checkbox is checked
    if show_basic_info:
        st.sidebar.markdown("""
        ### Basic Interactions
        - **Ask About Streamlit**: Type your questions about Streamlit's latest updates, features, or issues.
        - **Search for Code**: Use keywords like 'code example', 'syntax', or 'how-to' to get relevant code snippets.
        - **Navigate Updates**: Switch to 'Updates' mode to browse the latest Streamlit updates in detail.
        """)

    # Add another toggle checkbox in the sidebar for advanced interactions
    show_advanced_info = st.sidebar.toggle("Show Advanced Interactions", value=False)

    # Display the st.info box if the checkbox is checked
    if show_advanced_info:
        st.sidebar.markdown("""
        ### Advanced Interactions
        - **Generate an App**: Use keywords like **generate app**, **create app** to get a basic Streamlit app code.
        - **Code Explanation**: Ask for **code explanation**, **walk me through the code** to understand the underlying logic of Streamlit code snippets.
        - **Project Analysis**: Use **analyze my project**, **technical feedback** to get insights and recommendations on your current Streamlit project.
        - **Debug Assistance**: Use **debug this**, **fix this error** to get help with troubleshooting issues in your Streamlit app.
        """)

    st.sidebar.markdown("---")
    # Load image and convert to base64
    img_path = "imgs/stsidebarimg.png"  # Replace with the actual image path
    img_base64 = img_to_base64(img_path)



    # Display image with custom CSS class for glowing effect
    st.sidebar.markdown(
        f'<img src="data:image/png;base64,{img_base64}" class="cover-glow">',
        unsafe_allow_html=True,
    )

    # Access API Key from st.secrets and validate it
    api_key = st.secrets["OPENAI_API_KEY"]
    if not api_key:
        st.error("Please add your OpenAI API key to the Streamlit secrets.toml file.")
        st.stop()
    
    # Handle Chat and Update Modes
    if mode == "Chat with Streamly":
        chat_input = st.chat_input("Ask me about Streamlit updates:")
        if chat_input:
            latest_updates = load_streamlit_updates()
            on_chat_submit(chat_input, api_key, latest_updates, use_langchain)

        # Display chat history with custom avatars
        for message in st.session_state.history[-20:]:
            role = message["role"]
            
            # Set avatar based on role
            if role == "assistant":
                avatar_image = "imgs/avatar_streamly.png"
            elif role == "user":
                avatar_image = "imgs/stuser.png"
            else:
                avatar_image = None  # Default
            
            with st.chat_message(role, avatar=avatar_image):
                st.write(message["content"])

    else:
        display_streamlit_updates()

if __name__ == "__main__":
    main()