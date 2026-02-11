
import os
import sys
import json
import traceback
import subprocess
import config
from ai_providers import OpenAIProvider, ZhipuProvider, GeminiProvider

# Import existing bot tools
from telegram_bot import check_telegram, report_telegram, mark_done_telegram, combine_tasks, create_working_lock, remove_working_lock, reserve_memory_telegram, load_memory, get_task_dir

# ==========================================
# Tool Definitions
# ==========================================

def run_command(command):
    """Executes a shell command."""
    print(f"Executing command: {command}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8')
        return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    except Exception as e:
        return f"Error executing command: {e}"

def read_file(path):
    """Reads a file."""
    print(f"Reading file: {path}")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file {path}: {e}"

def write_file(path, content):
    """Writes to a file."""
    print(f"Writing file: {path}")
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing file {path}: {e}"

def list_dir(path="."):
    """Lists directory contents."""
    print(f"Listing directory: {path}")
    try:
        items = os.listdir(path)
        return "\n".join(items)
    except Exception as e:
        return f"Error listing directory {path}: {e}"

def run_python(code):
    """Executes Python code."""
    print(f"Executing Python code:\n{code}")
    from io import StringIO
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    
    try:
        exec_globals = {
            'os': os, 'sys': sys, 'json': json,
            'check_telegram': check_telegram,
            'report_telegram': report_telegram, 
            'mark_done_telegram': mark_done_telegram,
            'combine_tasks': combine_tasks,
            'create_working_lock': create_working_lock,
            'remove_working_lock': remove_working_lock,
            'reserve_memory_telegram': reserve_memory_telegram,
            'load_memory': load_memory,
            'get_task_dir': get_task_dir,
            'print': print
        }
        exec(code, exec_globals)
        sys.stdout = old_stdout
        return redirected_output.getvalue()
    except Exception as e:
        sys.stdout = old_stdout
        return f"Error executing Python code: {e}\n{traceback.format_exc()}"

# Mapping for unified execution
TOOLS_MAP = {
    'run_command': run_command,
    'read_file': read_file,
    'write_file': write_file,
    'list_dir': list_dir,
    'run_python': run_python
}

# OpenAI/Zhipu Tool Schema
OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Execute a shell command",
            "parameters": {
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read file content",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "List files in a directory",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_python",
            "description": "Execute Python code to interact with bot functions",
            "parameters": {
                "type": "object",
                "properties": {"code": {"type": "string"}},
                "required": ["code"]
            }
        }
    }
]

# Gemini Callables List
GEMINI_TOOLS = [run_command, read_file, write_file, list_dir, run_python]

# ==========================================
# Main Agent Logic
# ==========================================

def get_provider():
    p_name = config.AI_PROVIDER
    api_key = config.AI_API_KEY
    model = config.AI_MODEL_NAME
    base_url = config.AI_BASE_URL
    
    print(f"Initializing Provider: {p_name} ({model})")

    if p_name == 'openai':
        return OpenAIProvider(api_key, model, base_url), OPENAI_TOOLS
    elif p_name == 'zhipu':
        # Zhipu uses same schema as OpenAI
        return ZhipuProvider(api_key, model), OPENAI_TOOLS 
    elif p_name == 'gemini':
        # Gemini uses list of functions
        return GeminiProvider(api_key, model), GEMINI_TOOLS
    else:
        raise ValueError(f"Unknown provider: {p_name}")

SYSTEM_PROMPT = """
You are an intelligent agent replacing Claude in an automated bot system.
Your goal is to process tasks received via Telegram using the provided tools.

Standard Workflow:
1. Check tasks: `run_python("check_telegram()")`
2. If tasks exist:
   a. Combine: `combine_tasks`
   b. Notify user: `send_message_sync`
   c. Lock & Memory: `create_working_lock`, `load_memory`
   d. EXECUTE TASK (use tools)
   e. Report & Finish: `report_telegram`, `mark_done_telegram`, `remove_working_lock`
3. If no tasks, exit.
"""

def main():
    if not config.validate_config():
        sys.exit(1)
        
    try:
        provider, tools = get_provider()
    except Exception as e:
        print(f"Failed to initialize AI Provider: {e}")
        sys.exit(1)

    # Initial Message to kickstart the loop
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "Check for new Telegram messages and process them if any."}
    ]

    print("--- Agent Loop Started ---")
    
    # Simple Loop Limit to prevent infinite loops during testing
    MAX_TURNS = 10 
    turn = 0
    
    while turn < MAX_TURNS:
        turn += 1
        print(f"Turn {turn}...")
        
        # 1. Generate Response
        if config.AI_PROVIDER == 'gemini':
             # Gemini handles loop internally differently if using chat session
             # But our wrapper returns unified object
             response = provider.generate_response(messages, tools)
        else:
             response = provider.generate_response(messages, tools)
        
        content = response.get("content")
        tool_calls = response.get("tool_calls")
        
        if content:
            print(f"[AI]: {content}")
            messages.append({"role": "assistant", "content": content})
            
            # Simple heuristic exit if AI says it's done or no messages
            if "No messages" in content or "임무 완료" in content:
                print("Agent indicated completion.")
                break

        if tool_calls:
            # Append assistant message with tool calls (required for OpenAI history)
            # For our manual loop, we construct it properly
            # Note: real OpenAI api requires the tool call ID in the assistant message
            # Our Wrapper returns simplified list, but we need to match history format for next call
            
            # Construct formatted assistant message for history
            # (Simplification: re-using the raw response object if possible would be better, 
            # but here we reconstruct for demonstration)
            if config.AI_PROVIDER in ['openai', 'zhipu']:
                # We need to construct the 'tool_calls' object again for the history
                pass # The generic loop is tricky with different SDK objects. 
                     # For now, we trust the providers handle state or we just append results
            
            for tc in tool_calls:
                fn_name = tc['name']
                args = tc['arguments']
                call_id = tc['id']
                
                print(f"[Tool Call]: {fn_name}({args})")
                
                if fn_name in TOOLS_MAP:
                    try:
                        result = TOOLS_MAP[fn_name](**args)
                    except Exception as e:
                        result = f"Error: {e}"
                else:
                    result = f"Error: Unknown tool {fn_name}"
                
                print(f"[Tool Output]: {result[:100]}...")
                
                # Append tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": call_id,
                    "name": fn_name,
                    "content": str(result)
                })

        if not tool_calls and not content:
             print("Error: Empty response from AI")
             break
             
        if not tool_calls and content:
             # If AI just talks without calling tools, we might be done or it needs a nudge
             # If it looks like a question, we let it be. If it looks like "Done", we exit.
             if "exit" in content.lower() or "bye" in content.lower():
                 break

if __name__ == "__main__":
    main()
