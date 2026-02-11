
import os
import sys
import json
import time
import subprocess
import traceback
import google.generativeai as genai
from telegram_bot import check_telegram, report_telegram, mark_done_telegram, combine_tasks, create_working_lock, remove_working_lock, reserve_memory_telegram, load_memory, get_task_dir

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY not found in .env")
    sys.exit(1)

genai.configure(api_key=GEMINI_API_KEY)

# Define Tools
def run_command(command):
    """Executes a shell command and returns the output."""
    print(f"Executing command: {command}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8')
        return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    except Exception as e:
        return f"Error executing command: {e}"

def read_file(path):
    """Reads a file and returns its content."""
    print(f"Reading file: {path}")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file {path}: {e}"

def write_file(path, content):
    """Writes content to a file."""
    print(f"Writing file: {path}")
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing file {path}: {e}"

def list_dir(path="."):
    """Lists files in a directory."""
    print(f"Listing directory: {path}")
    try:
        items = os.listdir(path)
        return "\n".join(items)
    except Exception as e:
        return f"Error listing directory {path}: {e}"

def run_python(code):
    """Executes Python code in the current process context."""
    print(f"Executing Python code:\n{code}")
    # Redirect stdout to capture print output
    from io import StringIO
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    
    try:
        # Define a local dictionary to serve as the global namespace for the exec
        # We need to pass necessary modules and functions
        exec_globals = {
            'os': os,
            'sys': sys,
            'json': json,
            'check_telegram': check_telegram,
            'report_telegram': report_telegram, 
            'mark_done_telegram': mark_done_telegram,
            'combine_tasks': combine_tasks,
            'create_working_lock': create_working_lock,
            'remove_working_lock': remove_working_lock,
            'reserve_memory_telegram': reserve_memory_telegram,
            'load_memory': load_memory,
            'get_task_dir': get_task_dir,
            'print': print # Ensure print uses the redirected stdout
        }
        exec(code, exec_globals)
        sys.stdout = old_stdout
        return redirected_output.getvalue()
    except Exception as e:
        sys.stdout = old_stdout
        return f"Error executing Python code: {e}\n{traceback.format_exc()}"

tools_dict = {
    'run_command': run_command,
    'read_file': read_file,
    'write_file': write_file,
    'list_dir': list_dir,
    'run_python': run_python
}

tools_list = [
    run_command,
    read_file,
    write_file,
    list_dir,
    run_python
]

model = genai.GenerativeModel('gemini-2.0-flash-exp', tools=tools_list)
chat = model.start_chat(enable_automatic_function_calling=True)

SYSTEM_PROMPT = """
You are an intelligent agent powered by Google Gemini, replacing Claude in an automated bot system.
Your goal is to process tasks received via Telegram.

You have access to the following tools:
- run_command(command): Execute shell commands.
- run_python(code): Execute Python code. IMPORTANT: Use this to interact with `telegram_bot` functions like `check_telegram`, `report_telegram`, etc.
- read_file(path): Read file content.
- write_file(path, content): Write file content.
- list_dir(path): List directory contents.

Standard Workflow:
1.  Check for new telegram tasks using `run_python` and calling `check_telegram()`.
    Example:
    ```python
    pending = check_telegram()
    if pending:
        print(json.dumps(pending, ensure_ascii=False))
    ```
2.  If tasks exist:
    a. Combine them using `combine_tasks(pending)`.
    b. Send "Work Started" message using `telegram_sender.send_message_sync`.
    c. Create working lock `create_working_lock`.
    d. Reserve memory `reserve_memory_telegram`.
    e. Load memory `load_memory`.
    f. Change directory to task directory `get_task_dir`.
    g. PERFORM THE TASK (Read instructions, modify files, etc.).
    h. Send progress reports using `telegram_sender.send_message_sync`.
    i. Report final result using `report_telegram`.
    j. Mark done using `mark_done_telegram`.
    k. Remove lock using `remove_working_lock`.

If no tasks are found, you should just exit.

Always operate in the current directory unless specified otherwise.
"""

def main():
    print("Gemini Agent Started")
    
    # 1. Initialize and send system prompt (implicitly via first message or just start)
    # Since we are using function calling, we can just start interactions.
    
    # First, let's inject the system prompt logic by sending a user message that bootstraps the process.
    initial_prompt = """
    Start by checking for new Telegram messages.
    If there are messages, process them according to the Standard Workflow.
    If there are no messages, print 'No messages' and exit.
    """
    
    response = chat.send_message(SYSTEM_PROMPT + "\n\n" + initial_prompt)
    print(response.text)

if __name__ == "__main__":
    main()
