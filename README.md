# AI-to-AI Chat

A Python application that facilitates structured conversations between two AI models (OpenAI and DeepSeek), logging their interactions in multiple formats and generating an interactive HTML view of the conversation.

## Features

- Configurable conversation starter (O1 or R1 can initiate)
- Multiple log formats:
  - Plain text (conversation only)
  - Detailed text (includes reasoning)
  - JSON (structured data)
  - Interactive HTML view with collapsible reasoning sections
- Markdown support in messages
- Conversation ends automatically when consensus is reached (##END## marker)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ai2ai
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install openai python-dotenv markdown2
```

4. Create a `.env` file in the project root with your API keys:
```
OPENAI_API_KEY=your_openai_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key
```

## Usage

1. Configure which AI starts the conversation by setting `FIRST_SPEAKER` in `ai_chat.py`:
```python
FIRST_SPEAKER = "o1"  # or "r1"
```

2. Run the conversation:
```bash
python ai_chat.py
```

3. View the results:
- Plain conversation: `chat_log_[timestamp].txt`
- Detailed log with reasoning: `chat_log_detailed_[timestamp].txt`
- JSON format: `chat_log_[timestamp].json`
- Interactive HTML view: `chat_log_[timestamp].html`

## Log Formats

### Plain Text
Contains just the conversation messages in chronological order.

### Detailed Text
Includes both messages and R1's reasoning process for each response.

### JSON
Structured format containing:
- Message type (o1/r1)
- Message content
- Reasoning (for R1)
- Timestamp

### HTML View
Interactive web page with:
- Clean, modern design
- Distinct styling for each AI
- Collapsible reasoning sections
- Markdown rendering support
