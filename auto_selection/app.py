from flask import Flask, render_template, request, jsonify
import random
import json
import os

app = Flask(__name__)

OPTIONS_FILE = 'options.json'

def load_options_from_file():
    if os.path.exists(OPTIONS_FILE):
        with open(OPTIONS_FILE, 'r', encoding='utf-8') as f:
            try:
                options = json.load(f)
                # Ensure loaded data is a list of strings
                if isinstance(options, list) and all(isinstance(item, str) for item in options):
                    return options
            except json.JSONDecodeError:
                # Handle corrupted JSON file
                print(f"Error decoding JSON from {OPTIONS_FILE}")
                return []
    return []

def save_options_to_file(options):
    with open(OPTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(options, f, ensure_ascii=False, indent=4)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/make_decision', methods=['POST'])
def make_decision():
    options = request.json.get('options', [])
    
    # 过滤掉空选项
    valid_options = [opt.strip() for opt in options if opt.strip()]
    
    if not valid_options:
        return jsonify({'error': '请至少输入一个有效选项'}), 400
    
    # 随机选择一个选项
    selected = random.choice(valid_options)
    return jsonify({'result': selected})

@app.route('/save_options', methods=['POST'])
def save_current_options():
    options = request.json.get('options', [])
    # Validate options received from frontend
    if not isinstance(options, list) or not all(isinstance(item, str) for item in options):
         return jsonify({'error': 'Invalid options format'}), 400
    
    save_options_to_file(options)
    return jsonify({'message': 'Options saved successfully!'})

@app.route('/load_options', methods=['GET'])
def load_current_options():
    options = load_options_from_file()
    return jsonify({'options': options})

if __name__ == '__main__':
    # Load options on startup
    initial_options = load_options_from_file()
    # If no options loaded, add a default empty input field for the user
    if not initial_options:
         print("No options file found or empty, starting with a blank state.")
    
    app.run(debug=True) 