
import os
import json
import logging
from abc import ABC, abstractmethod

# Initialize Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BaseProvider(ABC):
    """Abstract Base Class for AI Providers"""
    
    def __init__(self, api_key, model_name, base_url=None):
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = base_url

    @abstractmethod
    def generate_response(self, messages, tools=None):
        """
        Generates a response from the AI model.
        
        Args:
            messages (list): List of message dictionaries (role, content).
            tools (list): List of tool definitions (functions or schemas).
            
        Returns:
            dict: standardized response object {
                "content": str or None,
                "tool_calls": list or None [ { "id": str, "name": str, "arguments": dict } ]
            }
        """
        pass

class OpenAIProvider(BaseProvider):
    """Provider for OpenAI-compatible APIs (OpenAI, Kimi, DeepSeek, etc.)"""
    
    def __init__(self, api_key, model_name, base_url=None):
        super().__init__(api_key, model_name, base_url)
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        except ImportError:
            logger.error("OpenAI package not installed. Please install 'openai'.")
            raise

    def generate_response(self, messages, tools=None):
        try:
            # Convert python functions to OpenAI tool schema if necessary
            # For simplicity in this implementation, we assume 'tools' passed here 
            # are already in OpenAI JSON schema format or we convert them.
            # In universal_agent.py, we will handle the schema generation.
            
            kwargs = {
                "model": self.model_name,
                "messages": messages,
            }
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

            response = self.client.chat.completions.create(**kwargs)
            message = response.choices[0].message
            
            tool_calls = []
            if message.tool_calls:
                for tc in message.tool_calls:
                    tool_calls.append({
                        "id": tc.id,
                        "name": tc.function.name,
                        "arguments": json.loads(tc.function.arguments)
                    })
            
            return {
                "content": message.content,
                "tool_calls": tool_calls if tool_calls else None
            }
        except Exception as e:
            logger.error(f"OpenAI API Error: {e}")
            return {"content": f"Error: {e}", "tool_calls": None}

class ZhipuProvider(BaseProvider):
    """Provider for Zhipu AI (GLM models)"""
    
    def __init__(self, api_key, model_name, base_url=None):
        super().__init__(api_key, model_name, base_url)
        try:
            from zhipuai import ZhipuAI
            self.client = ZhipuAI(api_key=api_key)
        except ImportError:
            logger.error("ZhipuAI package not installed. Please install 'zhipuai'.")
            raise

    def generate_response(self, messages, tools=None):
        try:
            kwargs = {
                "model": self.model_name,
                "messages": messages,
            }
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"
                
            response = self.client.chat.completions.create(**kwargs)
            message = response.choices[0].message
            
            tool_calls = []
            if message.tool_calls:
                for tc in message.tool_calls:
                    tool_calls.append({
                        "id": tc.id,
                        "name": tc.function.name,
                        "arguments": json.loads(tc.function.arguments)
                    })

            return {
                "content": message.content,
                "tool_calls": tool_calls if tool_calls else None
            }
        except Exception as e:
            logger.error(f"ZhipuAI API Error: {e}")
            return {"content": f"Error: {e}", "tool_calls": None}

class GeminiProvider(BaseProvider):
    """Provider for Google Gemini"""
    
    def __init__(self, api_key, model_name, base_url=None):
        super().__init__(api_key, model_name, base_url)
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.genai = genai
            # Tools are passed at model initialization or generate_content in standard SDK
            # But here we initialize model per call or manage state?
            # Creating model instance here
        except ImportError:
            logger.error("Google Generative AI package not installed.")
            raise

    def generate_response(self, messages, tools=None):
        # Gemini handles tools differently (passes actual functions).
        # We need to bridge the gap. 
        # For this version, 'tools' arg is expected to be a list of CALLABLES for Gemini,
        # and list of DICTS for OpenAI/Zhipu. 
        # universal_agent.py needs to handle this distinction.
        
        try:
            # Convert messages to Gemini format
            # Gemini history: [{"role": "user", "parts": [...]}, {"role": "model", "parts": [...]}]
            # System prompt is usually separate.
            
            system_instruction = None
            gemini_history = []
            
            for msg in messages:
                if msg['role'] == 'system':
                    system_instruction = msg['content']
                elif msg['role'] == 'user':
                    gemini_history.append({"role": "user", "parts": [msg['content']]})
                elif msg['role'] == 'assistant':
                    # If assistant message has tool calls, Gemini needs special handling
                    # Assuming basic text for now or simple turns
                    gemini_history.append({"role": "model", "parts": [msg['content'] or ""]})
                # Tool outputs handling is complex in stateless calls without chat session
            
            # Use ChatSession for ease
            model = self.genai.GenerativeModel(self.model_name, tools=tools, system_instruction=system_instruction)
            chat = model.start_chat(history=gemini_history[:-1] if gemini_history else [])
            
            last_msg = gemini_history[-1]['parts'][0] if gemini_history else "Start"
            
            response = chat.send_message(last_msg)
            
            # Parse response
            # Gemini auto-calls tools if enabled? 
            # If using 'tools', response might contain function_call
            
            tool_calls = []
            for part in response.parts:
                if fn := part.function_call:
                    tool_calls.append({
                        "id": "gemini_tool", # Gemini doesn't have IDs like OpenAI
                        "name": fn.name,
                        "arguments": dict(fn.args)
                    })
            
            return {
                "content": response.text if not tool_calls else None, # Gemini might throw if asking for text on tool call
                "tool_calls": tool_calls if tool_calls else None
            }

        except Exception as e:
            # Gemini often errors on `response.text` if it's a tool call
            # We need to be careful checking parts
            logger.error(f"Gemini API Error: {e}")
            return {"content": f"Error: {e}", "tool_calls": None}
