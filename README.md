# AI-Powered Terminal Assistant

This script provides an AI-powered terminal assistant for Linux environments. It offers a choice between normal terminal usage and an AI chat interface that can help with commands, scripting, and other terminal-related tasks.

## Features

*   **Interactive AI Chat:** Engage with an AI (via OpenRouter) to get help with terminal commands, scripting, and troubleshooting.
*   **Command Suggestions:** The AI can suggest commands, which you can then choose to run directly or copy to your clipboard.
*   **Personalized Greeting:** Greets the user with their Linux username.
*   **Easy to Launch:** Designed to be easily integrated for launch on every terminal start (e.g., with oh-my-zsh).

## Prerequisites

*   Python 3.6+
*   `pip` (Python package installer)
*   `git` (for cloning the repository)
*   An OpenRouter API Key

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/overspend1/ai-powered-terminal.git
    cd ai-powered-terminal
    ```

2.  **Install Python dependencies:**
    ```bash
    pip install requests pyperclip
    ```
    *   `requests`: For making API calls to OpenRouter.
    *   `pyperclip`: For copying suggested commands to the clipboard. You might need to install a backend for it on Linux, e.g.:
        ```bash
        sudo apt-get install xclip
        # or
        sudo apt-get install xsel
        ```

3.  **Configure your API Key:**
    Open the `ai_terminal.py` script in a text editor.
    Find the line:
    ```python
    OPENROUTER_API_KEY = "your_api_key_here" # Replace with your actual key
    ```
    Replace `"your_api_key_here"` with your actual OpenRouter API key. **Do not commit your API key to any public repository if you fork this project.**

## Usage

1.  **Make the script executable:**
    ```bash
    chmod +x ai_terminal.py
    ```

2.  **Run the script:**
    ```bash
    ./ai_terminal.py
    ```
    You will be greeted and presented with a menu to either use the normal terminal or start an AI chat session.

### Integrating with Oh My Zsh (or other shells)

To have the assistant launch every time you open a new terminal with Oh My Zsh, you can add the script to your `.zshrc` file.

1.  Open your `.zshrc` file (usually located at `~/.zshrc`):
    ```bash
    nano ~/.zshrc
    ```

2.  Add the following line at the end of the file, replacing `/path/to/your/script/` with the actual absolute path to where you cloned the `ai-powered-terminal` repository:
    ```bash
    # Launch AI Terminal Assistant
    if [[ -z "$AI_TERMINAL_ACTIVE" ]]; then
        export AI_TERMINAL_ACTIVE="true"
        /path/to/your/script/ai-powered-terminal/ai_terminal.py
        unset AI_TERMINAL_ACTIVE # Clean up for subsequent shells in the same session if needed
    fi
    ```
    The `AI_TERMINAL_ACTIVE` environment variable check is a simple way to prevent the script from re-launching itself if it exits and returns to a shell that would otherwise re-trigger it (e.g., if you choose "Use normal terminal" which exits the script).

3.  Save the file (Ctrl+O, Enter, then Ctrl+X in nano) and reload your zsh configuration:
    ```bash
    source ~/.zshrc
    ```
    Now, every new terminal session should start with the AI Terminal Assistant.

## AI Model

Currently, the script is configured to use `deepseek/deepseek-r1-0528` via OpenRouter. You can change this by modifying the `AI_MODEL` variable in `ai_terminal.py`.

## Contributing

Contributions, issues, and feature requests are welcome. Feel free to check the [issues page](https://github.com/overspend1/ai-powered-terminal/issues).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
