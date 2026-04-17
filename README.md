# sinrAIy
sinrAIy - Local AI Chat with OpenRouter API

## Description
A web application for interacting with various artificial intelligence models via the OpenRouter API. It supports streaming responses and works with several free LLM models.

## Technical Specifications

### Technology Stack
- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript (vanilla JS)
- **API**: OpenRouter API
- **Streaming**: Server-Sent Events (SSE)

### System Requirements
- Python 3.8+
- pip (Python package manager)
- OpenRouter API key (obtain at https://openrouter.ai/)

## Installation

### 1. Cloning the repository
```bash
git clone https://github.com/siniray/sinrAIy.git
cd sinrAIy
```

### 2. Create a virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Installing dependencies
```bash
pip install -r requirements.txt
```

### 4. Configuring environment variables
Create a `.env` file in the project's root directory:
```
OPENROUTER_API_KEY=your_api_key
```

You can obtain an API key on the [OpenRouter](https://openrouter.ai/) website

## Running the application

### Development
```bash
python app.py
```

The application will be accessible at: `http://localhost:5000`

### Launch parameters
- `debug=True` - debug mode (automatic restart when code changes)
- `port=5000` - application port

## 🔧 Project structure
```
sinrAIy/
├── app.py                 # Main
```