import streamlit as st
from src.database import load_data


def render_sidebar_header():
    """
    Renders the sidebar configuration and debug area.
    
    Returns:
        current_user_id (str): The currently selected user ID for testing.
    """
    st.sidebar.title("💊 Pharmacy Agent")
    st.sidebar.markdown("---")
    
    # Feature: User Selection for Testing Prescription Flows
    st.sidebar.header("Testing Controls")
    # We load users from the DB to make testing flows easy
    # (Mocking a login system)
    try:
        users = load_data()["users"]
        user_options = {u["name"]: u["id"] for u in users}
        selected_name = st.sidebar.selectbox("Simulate User:", list(user_options.keys()))
        # selected_name = "Yehosua Cohen" # A name not on the DB to test unknown user handling
        current_user_id = user_options[selected_name]
        st.sidebar.info(f"User ID: `{current_user_id}`")
    except Exception as e:
        st.sidebar.error("Could not load users or specified user name doesn't exist. Check database.py")
        current_user_id = "guest"
        
    return current_user_id

def render_chat_history(messages):
    """
    Renders the existing chat history.
    Used to keep all the Q&A visible in the UI.
    Skipping system prompts to keep the UI clean.
    
    Args:
        messages (list): The list of message dictionaries in the conversation history.
    """
    for msg in messages:
        if msg["role"] == "system":
            continue
        
        # Tool outputs are technical; usually hidden or shown in a special way.
        # Here we only show User and Assistant text.
        if msg["role"] == "tool":
            continue
        
        with st.chat_message(msg["role"]):
            # chat_message returns a container that holds the msg["content"], we format it as markdown
            st.markdown(msg["content"])

def display_debug_log(log_container, message):
    """
    Updates the debug log in the sidebar to show tool calls.
    
    Args:
        log_container: The Streamlit container that holds the debug log.
        message (str): The debug message to display.
    """
    with log_container:
        st.code(message, language="json")