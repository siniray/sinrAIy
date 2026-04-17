import os
import json
import requests
from flask import Flask, render_template, request, jsonify, Response, stream_with_context
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = """Ты - полезный ассистент. Отвечай на том же языке, на котором задан вопрос. Если вопрос на русском - отвечай на русском. Не добавляй лишних приветствий, подписей и повторений. Отвечай кратко и по существу."""

AVAILABLE_MODELS = [
    {"id": "arcee-ai/trinity-large-preview:free", "name": "Trinity Large Preview"},
    {"id": "nvidia/nemotron-3-super-120b-a12b:free", "name": "NVIDIA NeMo 3 Super 120B"},
    {"id": "openai/gpt-oss-120b:free", "name": "GPT-OSS 120B"},
    {"id": "nvidia/nemotron-3-nano-30b-a3b:free", "name": "NVIDIA NeMo 3 Nano 30B"},
    {"id": "openrouter/free", "name": "Auto (Best Free)"},
    {"id": "deepseek/deepseek-chat-v3-0324:free", "name": "DeepSeek Chat V3 0324"},
    #{"id": "z-ai/glm-4.5-air:free", "name": "GLM-4.5 Air"},
    #{"id": "google/gemma-4-31b-it:free", "name": "Gemma 4 31B IT"},
    #{"id": "cognitivecomputations/dolphin-mistral-24b-venice-edition:free", "name": "Dolphin Mistral 24B Venice Edition"},
    #{"id": "meta-llama/llama-guard-4-12b:free", "name": "Llama Guard 4 12B"},
    #{"id": "minimax/minimax-m2.5:free", "name": "MiniMax M2.5"},
    #{"id": "nvidia/nemotron-nano-9b-v2:free", "name": "Nemotron Nano 9B V2"},
    #{"id": "nousresearch/hermes-3-llama-3.1-405b:free", "name": "Hermes 3 Llama 3.1 405B"},
    #{"id": "google/gemma-4-26b-a4b-it:free", "name": "Gemma 4 26B IT"},
]

@app.route('/')
def index():
    return render_template('index.html', models=AVAILABLE_MODELS)

@app.route('/api/models')
def get_models():
    return jsonify(AVAILABLE_MODELS)

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        messages = data.get('messages', [])
        model = data.get('model', 'openrouter/auto')
        
        full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5000",
            "X-Title": "OpenRouter Web App"
        }

        payload = {
            "model": model,
            "messages": full_messages,
        }

        response = requests.post(
            OPENROUTER_API_URL,
            headers=headers,
            json=payload,
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            return jsonify({
                'success': True,
                'response': result['choices'][0]['message']['content'],
                'usage': result.get('usage', {}),
                'model': result.get('model', model)
            })
        else:
            return jsonify({
                'success': False,
                'error': f"API Error: {response.status_code} - {response.text}"
            }), response.status_code

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chat/stream', methods=['POST'])
def chat_stream():
    data = request.json
    messages = data.get('messages', [])
    model = data.get('model', 'openrouter/auto')
    
    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "OpenRouter Web App"
    }

    payload = {
        "model": model,
        "messages": full_messages,
        "stream": True
    }

    def generate():
        response = None
        try:
            response = requests.post(
                OPENROUTER_API_URL,
                headers=headers,
                json=payload,
                stream=True,
                timeout=60
            )

            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data_str = line[6:]
                        if data_str != '[DONE]':
                            try:
                                chunk = json.loads(data_str)
                                if 'choices' in chunk and len(chunk['choices']) > 0:
                                    delta = chunk['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        yield f"data: {json.dumps({'content': delta['content']})}\n\n"
                            except json.JSONDecodeError:
                                continue

            yield "data: [DONE]\n\n"

        except GeneratorExit:
            if response:
                response.close()
            raise
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive'
        }
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)