import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from src.tools import tools_schema, available_functions
from CONSTS import AGENT_MODEL, SYSTEM_PROMPT

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def _initialize_messages(messages):
    """
    Prepares the message history by ensuring the System Prompt is present.
    Returns a copy to avoid side-effects on the UI state.
    
    Args:
        messages (list): The current list of message dictionaries.
    
    Returns:
        internal_messages (list): A copy of messages with System Prompt prepended if missing.
    """
    internal_messages = list(messages)
    if not internal_messages or internal_messages[0].get("role") != "system":
        internal_messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})
    return internal_messages

def _get_openai_stream(messages):
    """
    Wraps the OpenAI API call to keep the main logic clean.
    
    Args:
        messages (list): The list of message dictionaries for the conversation.
    
    Returns:
        (chat completion chunk): The streaming response from OpenAI.
    """
    return client.chat.completions.create(
        model=AGENT_MODEL,  
        messages=messages,
        tools=tools_schema,
        tool_choice="auto",
        stream=True
    )

def _process_stream_chunks(stream):
    """
    Iterates over the raw stream. 
    1. Yields text content to the UI immediately.
    2. Accumulates tool call fragments internally.
    Returns the final accumulated content and tool calls.
    
    Exmaple for a chuck from openAI website: 
    {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1694268190,"model":"gpt-4o-mini",
    "system_fingerprint": "fp_44709d6fcb",
    "choices":[{"index":0,"delta":{"role":"assistant","content":""},"logprobs":null,"finish_reason":null}]}

    Args:
        stream: The streaming response from OpenAI.
    
    Yields:
        (dict): Updates for the UI, either text content or debug info.
    
    Returns:
        content_accumulator (str): The full text content accumulated.
        tool_calls_accumulator (dict): The accumulated tool calls. The agent used for the current stream
    """
    content_accumulator = ""
    tool_calls_accumulator = {}

    for chunk in stream:
        delta = chunk.choices[0].delta

        # Case A: Text Content (Yield to UI)
        if delta.content:
            content_accumulator += delta.content
            yield {
                "type": "content",
                "data": delta.content
            }

        # Case B: Tool Call Fragments (Accumulate only) 
        if delta.tool_calls:
            for tool_call in delta.tool_calls:
                index = tool_call.index
                if index not in tool_calls_accumulator:
                    tool_calls_accumulator[index] = {
                        "id": tool_call.id,
                        "type": "function",  # Fix for the API requirement
                        "function": {"name": "", "arguments": ""}
                    }
                # If we already have initialized a tool_call in the accumelator at this index
                if tool_call.id:
                    tool_calls_accumulator[index]["id"] = tool_call.id
                if tool_call.function.name:
                    tool_calls_accumulator[index]["function"]["name"] += tool_call.function.name
                if tool_call.function.arguments:
                    tool_calls_accumulator[index]["function"]["arguments"] += tool_call.function.arguments


    # We return the accumulated data so the main loop can decide what to do next
    return content_accumulator, tool_calls_accumulator

def _execute_tool_calls(tool_calls_acc, content_acc, messages):
    """
    Handles the execution of tools if the model requested them.
    Updates the 'messages' list in-place.
    
    Args:
        tool_calls_acc (dict): The accumulated tool calls from the stream.
        content_acc (str): The accumulated text content from the stream.
        messages (list): The current list of message dictionaries to update.
        
    Yields:
        (dict): Updates for the UI, mainly debug info about tool execution.
    """
    # 1. Convert accumulator dict to a list
    tool_calls_list = list(tool_calls_acc.values())

    # 2. Append the Assistant's "Intent" message to history
    # (Required by OpenAI so it knows it asked for a tool)
    messages.append({
        "role": "assistant",
        "content": content_acc if content_acc else None,
        "tool_calls": tool_calls_list
    })

    # 3. Run each tool
    for tool_call in tool_calls_list:
        func_name = tool_call["function"]["name"]
        func_args_str = tool_call["function"]["arguments"]
        call_id = tool_call["id"]

        # Debug Output for UI
        yield {
            "type": "debug",
            "data": f"🛠️ Tool Call: {func_name}({func_args_str})"
        }

        # Execute Python Function
        if func_name in available_functions:
            try:
                args = json.loads(func_args_str)
                result = available_functions[func_name](**args)
            except Exception as e:
                result = json.dumps({"error": str(e)})
        else:
            result = json.dumps({"error": "Function not found"})

        # 4. Append the Tool Output to history
        messages.append({
            "tool_call_id": call_id,
            "role": "tool",
            "name": func_name,
            "content": result
        })

        # Debug Output for UI
        yield {
            "type": "debug",
            "data": f"✅ Result: {result}"
        }
        
def run_agent_stream(messages):
    """
    The main coordinator.
    1. Initializes context.
    2. Loops: Streams text -> Checks for tools -> Executes tools -> Repeats.
    
    Args:
        messages (list): The current list of message dictionaries.
    
    Yields:
        (dict): Updates for the UI, either text content or debug info.
    """
    # 1. Setup
    internal_messages = _initialize_messages(messages)

    # 2. Conversation Loop
    while True:
        # A. Start the stream
        stream = _get_openai_stream(internal_messages)
        
        # B. Process the stream (yields text to UI, returns accumulated data)
        # 'yield from' allows the sub-function to yield directly to the main caller
        content, tool_calls = yield from _process_stream_chunks(stream)

        # C. Decide: Do we need to run tools?
        if tool_calls:
            # Execute tools and yield debug info
            yield from _execute_tool_calls(tool_calls, content, internal_messages)
            
            # Loop continues to send tool outputs back to OpenAI
            continue
        
        else:
            # No tools called? We are done.
            break