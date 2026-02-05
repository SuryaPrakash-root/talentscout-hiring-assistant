import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

from prompts.prompts import SYSTEM_PROMPT

api_key = os.getenv("GEMINI_API_KEY")
model = None

if api_key and api_key != "your_api_key_here":
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-flash-latest", system_instruction=SYSTEM_PROMPT)
    except Exception as e:
        print(f"Failed to initialize Gemini model: {e}")

def ask_llm(messages):
    # Convert chat history to text prompt
    prompt = ""
    for m in messages:
        role = m["role"]
        content = m["content"]
        prompt += f"{role.upper()}: {content}\n"

    if model is None:
        yield "⚠️ **Error:** GEMINI_API_KEY is not set or invalid. Please add your API key to the `.env` file."
        return

    import time
    from google.api_core import exceptions

    # Use stream=True for streaming response
    retry_count = 0
    max_retries = 3
    base_delay = 5

    while retry_count < max_retries:
        try:
            response = model.generate_content(prompt, stream=True)
            for chunk in response:
                yield chunk.text
            return # Success, exit
        except exceptions.ResourceExhausted as e:
            retry_count += 1
            wait_time = base_delay * (2 ** (retry_count - 1))
            if retry_count == max_retries:
                yield f"⚠️ **Error:** Quota exceeded. Please try again later. (Details: {str(e)})"
                return
            yield f"*Rate limit hit. Retrying in {wait_time} seconds...*\n\n"
            time.sleep(wait_time)
        except Exception as e:
            yield f"⚠️ **Error:** Failed to generate response: {str(e)}"
            return

def extract_candidate_info(messages):
    from prompts.prompts import EXTRACTION_PROMPT
    import json
    
    if model is None:
        return None

    # Convert chat history to text
    conversation_text = ""
    for m in messages:
        conversation_text += f"{m['role'].upper()}: {m['content']}\n"

    try:
        # Use a separate generation call for extraction, asking for JSON
        prompt = f"{EXTRACTION_PROMPT}\n\nConversation:\n{conversation_text}"
        response = model.generate_content(prompt)
        
        # Clean up code blocks if Present
        text = response.text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
            
        return json.loads(text.strip())
    except Exception as e:
        print(f"Extraction error: {e}")
        return None
