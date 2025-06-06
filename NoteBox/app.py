from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import json
import os
from datetime import datetime

app = Flask(__name__, 
    static_folder='static',
    template_folder='prototype'
)
app.secret_key = 'your-secret-key'  # 用于flash消息

# 数据存储路径
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
NOTES_FILE = os.path.join(DATA_DIR, 'notes.json')
CARDS_FILE = os.path.join(DATA_DIR, 'cards.json')

# 确保数据目录存在
os.makedirs(DATA_DIR, exist_ok=True)

# 初始化数据文件
def init_data_files():
    if not os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)
    if not os.path.exists(CARDS_FILE):
        with open(CARDS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)

init_data_files()

def load_notes():
    with open(NOTES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_notes(notes):
    with open(NOTES_FILE, 'w', encoding='utf-8') as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)

def load_cards():
    with open(CARDS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_cards(cards):
    with open(CARDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(cards, f, ensure_ascii=False, indent=2)

@app.route('/')
def notebox_main():
    notes = load_notes()
    cards = load_cards()
    return render_template('main.html', 
                         total_notes=len(notes),
                         total_cards=len(cards),
                         recent_notes=notes[-5:] if notes else [])

@app.route('/notes')
def notebox_notes():
    notes = load_notes()
    return render_template('note_list.html', notes=notes)

@app.route('/edit_note')
def notebox_edit_note():
    note_id = request.args.get('id')
    if note_id:
        notes = load_notes()
        note = next((n for n in notes if n['id'] == int(note_id)), None)
        if note:
            return render_template('edit_note.html', note=note)
    return render_template('edit_note.html')

@app.route('/cards')
def notebox_cards():
    cards = load_cards()
    return render_template('cards.html', cards=cards)

@app.route('/review')
def notebox_review():
    return render_template('review.html')

@app.route('/api/notes', methods=['POST'])
def save_note():
    try:
        note_data = request.json
        notes = load_notes()
        
        # 添加创建时间和ID
        note_data['id'] = len(notes) + 1
        note_data['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        note_data['updated_at'] = note_data['created_at']
        
        notes.append(note_data)
        save_notes(notes)
        
        flash('笔记保存成功！', 'success')
        return jsonify({'success': True, 'message': '笔记保存成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/cards', methods=['POST'])
def save_card():
    try:
        card_data = request.json
        cards = load_cards()
        
        # 添加创建时间和ID
        card_data['id'] = len(cards) + 1
        card_data['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cards.append(card_data)
        save_cards(cards)
        
        return jsonify({'success': True, 'message': '卡片保存成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/notes', methods=['GET'])
def get_notes():
    notes = load_notes()
    return jsonify(notes)

@app.route('/api/cards', methods=['GET'])
def get_cards():
    cards = load_cards()
    return jsonify(cards)

@app.route('/api/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    try:
        note_data = request.json
        notes = load_notes()
        note = next((n for n in notes if n['id'] == note_id), None)
        
        if note:
            note.update({
                'title': note_data.get('title', note['title']),
                'course': note_data.get('course', note['course']),
                'tags': note_data.get('tags', note['tags']),
                'content': note_data.get('content', note['content']),
                'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            save_notes(notes)
            return jsonify({'success': True, 'message': '笔记更新成功'})
        return jsonify({'success': False, 'message': '笔记不存在'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    try:
        notes = load_notes()
        note = next((n for n in notes if n['id'] == note_id), None)
        
        if note:
            notes.remove(note)
            save_notes(notes)
            return jsonify({'success': True, 'message': '笔记删除成功'})
        return jsonify({'success': False, 'message': '笔记不存在'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/notes/<int:note_id>/cards', methods=['GET'])
def get_note_cards(note_id):
    try:
        cards = load_cards()
        note_cards = [card for card in cards if card.get('noteId') == note_id]
        return jsonify(note_cards)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 