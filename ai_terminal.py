#!/usr/bin/env python3
import json
import os
import shlex
import subprocess
import sys
import getpass
import random

try:
    import requests
except ImportError:
    print("The 'requests' library is not installed. Please install it by running:")
    print("pip install requests")
    sys.exit(1)

try:
    import pyperclip
except ImportError:
    print("The 'pyperclip' library is not installed. It's needed for copying to clipboard.")
    print("Please install it by running:")
    print("pip install pyperclip")
    # We can let the script continue, but copy functionality will be disabled.
    pass

# --- Configuration ---
# IMPORTANT: Replace "your_api_key_here" with your actual OpenRouter API key.
# Do NOT commit your API key to a public repository.
# Consider using an environment variable or a local config file for the API key.
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "your_api_key_here") 
AI_MODEL = "deepseek/deepseek-r1-0528"
SYSTEM_PROMPT = """You are a specialized Linux terminal assistant.
Your sole purpose is to help users with shell commands, scripting, and other terminal-related tasks.
Do not engage in conversations outside of this scope.
Do not provide general knowledge, opinions, or creative content.
If the user asks for something unrelated to the Linux terminal, politely state that you can only assist with terminal-related queries.
When you suggest a shell command that the user can run directly in their terminal, please wrap it clearly like this:
<<CMD_START>>
the_command_here
<<CMD_END>>
Only provide one such command block per response if a command is relevant.
The command should be complete and executable as is.
If the command is multi-line, ensure all lines are within the tags and correctly formatted for direct execution (e.g., using backslashes for line continuation if necessary).
For other code snippets, configurations, or explanations, use standard markdown code blocks."""

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
MAX_HISTORY_MESSAGES = 10 # Number of user/assistant message pairs to keep (plus system prompt)

# --- Helper Functions ---
def print_error(message):
    print(f"\033[91mError: {message}\033[0m", file=sys.stderr)

def print_info(message):
    print(f"\033[94m{message}\033[0m")

def print_ai_message(message):
    print(f"\033[92mAI:\033[0m {message}")

def check_dependencies():
    try:
        import requests
    except ImportError:
        print_error("The 'requests' library is not installed. Please install it by running: pip install requests")
        return False
    return True

def copy_to_clipboard(text):
    try:
        import pyperclip
        pyperclip.copy(text)
        print_info("Copied to clipboard.")
    except ImportError:
        print_error("pyperclip library not found. Cannot copy to clipboard.")
        print_info("To enable clipboard functionality, please install it: pip install pyperclip")
    except pyperclip.PyperclipException as e:
        print_error(f"Could not copy to clipboard: {e}")
        print_info("You may need to install a copy/paste mechanism for your system, e.g.,")
        print_info("sudo apt-get install xclip  OR  sudo apt-get install xsel")


def extract_command(ai_response):
    start_tag = "<<CMD_START>>"
    end_tag = "<<CMD_END>>"
    start_index = ai_response.find(start_tag)
    end_index = ai_response.find(end_tag)

    if start_index != -1 and end_index != -1 and start_index < end_index:
        command = ai_response[start_index + len(start_tag):end_index].strip()
        return command
    return None

# --- Main AI Chat Logic ---
def chat_with_ai():
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your_api_key_here":
        print_error("OpenRouter API key is not set or is a placeholder.")
        print_info("Please set your OPENROUTER_API_KEY environment variable or edit the script.")
        print_info("Example: export OPENROUTER_API_KEY='your_actual_key_here'")
        return

    print_info(f"Entering AI Chat Mode with model: {AI_MODEL}")
    print_info("Type 'exit' or 'quit' to return to the main menu.")

    conversation_history = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        try:
            user_input = input("\033[94mYou:\033[0m ")
        except EOFError: # Handle Ctrl+D
            print_info("\nExiting AI Chat...")
            break
        except KeyboardInterrupt: # Handle Ctrl+C
            print_info("\nExiting AI Chat...")
            break

        if user_input.lower() in ["exit", "quit"]:
            print_info("Exiting AI Chat...")
            break

        if not user_input:
            continue

        conversation_history.append({"role": "user", "content": user_input})

        if len(conversation_history) > (MAX_HISTORY_MESSAGES * 2 + 1):
            conversation_history = [conversation_history[0]] + conversation_history[-(MAX_HISTORY_MESSAGES * 2):]

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "Python Terminal AI Assistant"
        }
        payload = {
            "model": AI_MODEL,
            "messages": conversation_history,
            "stream": False
        }

        try:
            response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            response_data = response.json()

            if "choices" not in response_data or not response_data["choices"]:
                print_error("API response did not contain 'choices'.")
                print_error(f"Raw response: {response_data}")
                conversation_history.pop()
                continue

            ai_message_data = response_data["choices"][0].get("message", {})
            ai_message_content = ai_message_data.get("content")

            if not ai_message_content:
                print_error("AI response was empty or malformed.")
                print_error(f"Raw choice: {response_data['choices'][0]}")
                conversation_history.pop()
                continue

            print_ai_message(ai_message_content)
            conversation_history.append({"role": "assistant", "content": ai_message_content})

            suggested_command = extract_command(ai_message_content)
            if suggested_command:
                print_info("\n-----------------------------------------------------")
                print_info(f"AI suggested the following command:\n{suggested_command}")
                print_info("-----------------------------------------------------")
                
                while True:
                    try:
                        cmd_choice = input("Options: (R)un, (C)opy, (I)gnore, (Q)uit AI [I]: ").strip().lower()
                        cmd_choice = cmd_choice or 'i'
                    except EOFError:
                        print_info("\nDefaulting to Ignore.")
                        cmd_choice = 'i'
                        break
                    except KeyboardInterrupt:
                        print_info("\nDefaulting to Ignore.")
                        cmd_choice = 'i'
                        break

                    if cmd_choice == 'r':
                        confirm_run = input(f"Execute: '{suggested_command}'? (yes/No): ").strip().lower()
                        if confirm_run == 'yes':
                            print_info(f"Running: {suggested_command}")
                            try:
                                process = subprocess.run(suggested_command, shell=True, check=False, text=True, capture_output=True)
                                if process.stdout:
                                    print("\n--- Command STDOUT ---")
                                    print(process.stdout.strip())
                                    print("--- End STDOUT ---")
                                if process.stderr:
                                    print("\n--- Command STDERR ---")
                                    print_error(process.stderr.strip())
                                    print("--- End STDERR ---")
                                print_info(f"Command finished with exit code: {process.returncode}")
                            except Exception as e:
                                print_error(f"Failed to run command: {e}")
                        else:
                            print_info("Command not executed.")
                        break 
                    elif cmd_choice == 'c':
                        copy_to_clipboard(suggested_command)
                        break
                    elif cmd_choice == 'i':
                        print_info("Ignoring command suggestion.")
                        break
                    elif cmd_choice == 'q':
                        print_info("Exiting AI Chat...")
                        return
                    else:
                        print_error("Invalid option. Please choose R, C, I, or Q.")
        
        except requests.exceptions.HTTPError as e:
            print_error(f"HTTP Error: {e}")
            print_error(f"Response content: {e.response.text if e.response else 'No response content'}")
            conversation_history.pop()
        except requests.exceptions.RequestException as e:
            print_error(f"Request failed: {e}")
            conversation_history.pop()
        except json.JSONDecodeError as e:
            print_error(f"Failed to decode JSON response: {e}")
            print_error(f"Raw response text: {response.text if 'response' in locals() and hasattr(response, 'text') else 'No response object'}")
            conversation_history.pop()
        except Exception as e:
            print_error(f"An unexpected error occurred: {e}")
            conversation_history.pop()

# --- Main Menu ---
def main():
    if not check_dependencies():
        sys.exit(1)

    username = getpass.getuser()
    
    print_info(f"Welcome, {username}, to your Python AI Terminal Assistant! 🤖")
    print_info("--------------------------------------------------")
    
    # Check for API key at startup and inform user if missing/placeholder
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your_api_key_here":
        print_error("OpenRouter API key is not configured correctly.")
        print_info("AI Chat functionality will be limited until the API key is set.")
        print_info("Please set the OPENROUTER_API_KEY environment variable or edit the script.")
        print_info("Example: export OPENROUTER_API_KEY='your_actual_key_here'")
        print_info("--------------------------------------------------")

    while True:
        print_info("\n🖥️  Please choose an option:")
        print_info("1. 💻  Use normal terminal (Exit script)")
        print_info("2. 🤖  Chat with AI (OpenRouter)")
        print_info("--------------------------------------------------")
        
        try:
            choice = input("Enter your choice (1 or 2): ").strip()
        except EOFError:
            print_info("\nExiting.")
            break
        except KeyboardInterrupt:
            print_info("\nExiting.")
            break

        if choice == '1':
            print_info("Exiting script. Your normal terminal will resume.")
            break
        elif choice == '2':
            chat_with_ai()
            print_info("Returned to main menu.")
        else:
            print_error("Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    main()
