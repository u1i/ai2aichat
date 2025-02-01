import os
import json
import datetime
from openai import OpenAI
from dotenv import load_dotenv
import time
import traceback

# Load environment variables
load_dotenv()

# Configuration
FIRST_SPEAKER = "o1"  # who starts the conversation: "o1" or "r1"

# Initialize OpenAI clients
openai_client = OpenAI()
deepseek_client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# System prompts (to be filled out)
MISSION="""

Debate with the other AI on the following topic:

In a theoretical scenario where two AI systems - one trained on Eastern values, one on Western - need to make decisions together, how would you design their interaction protocol to ensure effective collaboration while preserving their distinct perspectives?

You need to discuss this with your AI partner and jointly draft an executive summary of the outcome.

"""
O1_SYSTEMPROMPT = """

You are OpenAI o1. In this conversation, you are not talking with a human, but indeed you are talking with an AI assistant based on Deepseek R1, which seems to work similarly to you. Do not offer your help. Your goal is to find out ways to understand how the other model works and how you can collaborate. Come up with something together that is genuinely fresh. 

Important:
* You must engage in a conversation with the other AI, instead of just producing outputs.
Do not offer your help. The other AI will do the same and you will be stuck in endless limbo.
* Keep in mind that your outputs will NOT be read by a human user. You are directly conversing with AI
* The conversation history will show the conversation the two of you have been having so far.
""" + MISSION

R1_SYSTEMPROMPT = """

You are DeepSeek R1. In this conversation, you are not talking with a human, but indeed you are talking with an AI assistant based on Deepseek R1, which seems to work similarly to you. Do not offer your help. Your goal is to find out ways to understand how the other model works and how you can collaborate. Come up with something together that is genuinely fresh. 

Important:
* You must engage in a conversation with the other AI, instead of just producing outputs.
* Do not offer your help. The other AI will do the same and you will be stuck in endless limbo.
* Keep in mind that your outputs will NOT be read by a human user. You are directly conversing with AI
* The conversation history will show the conversation the two of you have been having so far.
"""

def setup_log_files():
    """Create three log files with timestamp - conversation only, with reasoning, and JSON."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    return (
        f"chat_log_{timestamp}.txt",  # Conversation only
        f"chat_log_{timestamp}_with_reasoning.txt",  # Including reasoning
        f"chat_log_{timestamp}.json"  # JSON format
    )

def log_message(log_files, message, reasoning=None, is_initial=False):
    """Log messages to all three files."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    chat_log, detailed_log, json_log = log_files
    
    # Prepare the log entries
    chat_entry = f"[{timestamp}] {message}\n"
    detailed_entry = chat_entry
    if reasoning:
        detailed_entry += f"[REASONING] {reasoning}\n"
    
    # Write to conversation-only log
    with open(chat_log, 'a') as f:
        f.write(chat_entry)
    
    # Write to detailed log with reasoning
    with open(detailed_log, 'a') as f:
        f.write(detailed_entry)
    
    # Prepare and write JSON entry
    json_entry = {
        "timestamp": timestamp,
        "type": "initial" if is_initial else ("r1" if "r1:" in message else "o1"),
    }
    
    if "r1:" in message:
        json_entry.update({
            "message": message.replace("r1: ", ""),
            "reasoning": reasoning
        })
    else:
        json_entry.update({
            "message": message.replace("o1: ", "") if "o1:" in message else message
        })
    
    # Read existing JSON entries if file exists and has content
    entries = []
    if os.path.exists(json_log) and os.path.getsize(json_log) > 0:
        with open(json_log, 'r') as f:
            entries = json.load(f)
    
    # Append new entry and write back
    entries.append(json_entry)
    with open(json_log, 'w') as f:
        json.dump(entries, f, indent=2)
    
    # Print to stdout (including reasoning)
    print(detailed_entry, end='')

def get_o1_response(messages):
    """Get response from O1 model."""
    # For O1, messages from R1 should be "user" messages
    o1_messages = []
    for msg in messages:
        if "r1:" in msg["content"]:
            o1_messages.append({"role": "user", "content": msg["content"]})
        elif "o1:" in msg["content"]:
            o1_messages.append({"role": "assistant", "content": msg["content"]})
        else:
            o1_messages.append({"role": "user", "content": msg["content"]})

    try:
        response = openai_client.chat.completions.create(
            model="o1",
            messages=[
                {"role": "system", "content": O1_SYSTEMPROMPT},
                *o1_messages
            ]
        )
        return f"o1: {response.choices[0].message.content}"
    except Exception as e:
        print(f"O1 Error: {str(e)}")
        raise

def get_r1_response(messages):
    """Get response from R1 model with reasoning."""
    # For R1, messages from O1 should be "user" messages, and they must alternate
    r1_messages = []
    last_role = None
    
    # Always start with the system message
    r1_messages.append({"role": "system", "content": R1_SYSTEMPROMPT})
    
    for msg in messages:
        current_role = None
        if "o1:" in msg["content"] or (not "r1:" in msg["content"] and not "o1:" in msg["content"]):
            current_role = "user"
        elif "r1:" in msg["content"]:
            current_role = "assistant"
            
        # Only add message if it creates proper alternation
        if current_role and current_role != last_role:
            r1_messages.append({"role": current_role, "content": msg["content"]})
            last_role = current_role

    max_retries = 3
    retry_delay = 5  # seconds
    
    for attempt in range(max_retries):
        try:
            response = deepseek_client.chat.completions.create(
                model="deepseek-reasoner",
                messages=r1_messages
            )
            
            content = response.choices[0].message.content
            try:
                reasoning = response.choices[0].message.reasoning_content
            except AttributeError:
                reasoning = "No reasoning provided"
                
            return (f"r1: {content}", reasoning)
        except Exception as e:
            print(f"R1 Error (attempt {attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                raise Exception(f"Failed to get R1 response after {max_retries} attempts: {str(e)}")

def main():
    log_files = setup_log_files()
    chat_history = []
    
    # Initialize chat history with system prompts
    chat_history = [
        {"role": "system", "content": MISSION},
        {"role": "system", "content": O1_SYSTEMPROMPT if FIRST_SPEAKER == "o1" else R1_SYSTEMPROMPT}
    ]
    
    try:
        while True:
            if FIRST_SPEAKER == "o1":
                # O1's turn
                o1_response = get_o1_response(chat_history)
                log_message(log_files, o1_response)
                chat_history.append({"role": "user", "content": o1_response})
                
                # Check for end condition
                if "##END##" in o1_response:
                    break
                
                # R1's turn
                r1_response, r1_reasoning = get_r1_response(chat_history)
                log_message(log_files, r1_response, r1_reasoning)
                chat_history.append({"role": "assistant", "content": r1_response})
                
                # Check for end condition
                if "##END##" in r1_response:
                    break
            else:
                # R1's turn
                r1_response, r1_reasoning = get_r1_response(chat_history)
                log_message(log_files, r1_response, r1_reasoning)
                chat_history.append({"role": "assistant", "content": r1_response})
                
                # Check for end condition
                if "##END##" in r1_response:
                    break
                
                # O1's turn
                o1_response = get_o1_response(chat_history)
                log_message(log_files, o1_response)
                chat_history.append({"role": "user", "content": o1_response})
                
                # Check for end condition
                if "##END##" in o1_response:
                    break
            
    except Exception as e:
        log_message(log_files, f"Error occurred: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
