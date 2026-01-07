import streamlit as st
from src.agent import run_agent_stream
from src.ui_utils import render_sidebar_header, render_chat_history, display_debug_log

# 1. Page Config
st.set_page_config(page_title="Agent Engineer Pharmacy", page_icon="💊", layout="wide")

# 2. Sidebar & User Setup
user_id = render_sidebar_header() # Also gets the user ID from sidebar input
st.sidebar.subheader("🛠️ Agent Internals (Debug)")
debug_container = st.sidebar.container() # Tool calls will appear here

# 3. Session State (Memory)
# We store the conversation history here.
# Since the agent is stateless, we pass the full history each time.
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Main Chat Interface
st.title("🏥 AI Pharmacist Assistant")

# Render previous conversation
render_chat_history(st.session_state.messages)

# 5. Input Loop
if user_prompt := st.chat_input("How can I help you today?"):
    
    # A. Display User Message
    with st.chat_message("user"):
        # chat_message returns a container that holds the user_prompt, we format it as markdown
        st.markdown(user_prompt)
    
    # Add to history
    # We inject the current USER ID into the context so the agent knows who it is talking to.
    # This is how we make the stateless agent context-aware.
    context_prompt = f"[User ID: {user_id}] {user_prompt}"
    st.session_state.messages.append({"role": "user", "content": context_prompt})
    

    # B. Generate Assistant Response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        # Call the generator of the agent.
        # We pass the full history because agent is stateless.
        stream_generator = run_agent_stream(st.session_state.messages)
        
        for update in stream_generator:
            
            # Case 1: Text content for the user
            # Streaming it update by update as they come.
            if update["type"] == "content":
                full_response += update["data"]
                response_placeholder.markdown(full_response + "▌")
                
            # Case 2: Debug/Tool usage info - Showing tool calls)
            elif update["type"] == "debug":
                display_debug_log(debug_container, update["data"])
        
        # Display final response without cursor
        response_placeholder.markdown(full_response)
    
    # C. Save Assistant Response to History
    st.session_state.messages.append({"role": "assistant", "content": full_response})