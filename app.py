from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for, flash, session, g
import os
from flask_sqlalchemy import SQLAlchemy
import tempfile
from datetime import datetime
import base64
import requests
import json 
from text2cv import text2Latex, compileLatex
from flask_babel import Babel, _, lazy_gettext as _l

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///courses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['BABEL_DEFAULT_LOCALE'] = 'zh'

DATA_DIR = os.path.join(os.path.join(os.path.dirname(__file__), 'static'), 'data')
NOTES_FILE = os.path.join(DATA_DIR, 'notes.json')
CARDS_FILE = os.path.join(DATA_DIR, 'cards.json')
os.makedirs(DATA_DIR, exist_ok=True)

def init_data_files():
    if not os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)
    if not os.path.exists(CARDS_FILE):
        with open(CARDS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)


def get_locale():
    return session.get('language', request.args.get('language', 'zh'))

babel = Babel(app, locale_selector=get_locale)

db = SQLAlchemy(app)

@app.before_request
def set_language():
    g.lang = session.get('language', request.args.get('language', 'zh'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommender')
def recommender():
    return render_template('recommender.html')

@app.route('/llm')
def llm():
    return render_template('PathRecommender/llm/main.html')

@app.route('/aigc')
def aigc():
    return render_template('PathRecommender/aigc/main.html')

@app.route('/embodied')
def embodied():
    return render_template('PathRecommender/embodied/main.html')

@app.route('/algorithms')
def algorithms():
    return render_template('PathRecommender/embodied/algorithms.html')

@app.route('/control_and_robotics')
def control_and_robotics():
    return render_template('PathRecommender/embodied/control_and_robotics.html')

@app.route('/llm_basics')
def llm_basics():
    return render_template('PathRecommender/llm/llm_basics.html')

@app.route('/modern_algorithm_architecture')
def modern_algorithm_architecture():
    return render_template('PathRecommender/llm/modern_algorithm_architecture.html')

@app.route('/resume')
def resume():
    return render_template('resume.html')

@app.route('/preview')
def preview():
    return render_template('/ResumeGenerator/preview.html')

@app.route('/MiKTeX_installation')
def MiKTeX_installation():
    return render_template('/ResumeGenerator/MiKTeX_installation.html')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'GET':
        return render_template('chat.html')
    
    try:
        data = request.get_json()
        if not data:
            print('No JSON data provided')
            return jsonify({'error': 'No JSON data provided'}), 400

        user_message = data.get('message')
        prompt_type = data.get('promptType', 'user')
        model = data.get('model', 'V1')
        language = data.get('language', 'zh')

        if not user_message:
            print('Message is required')
            return jsonify({'error': 'Message is required'}), 400

        print(f'Received chat request: model={model}, promptType={prompt_type}, language={language}, message="{user_message}"')

        if language in ['en', 'zh']:
            session['language'] = language
            g.lang = language

        model_map = {
            'V1': 'deepseek-chat',
            'R3': 'deepseek-reasoner',
            'V3': 'deepseek-chat'  # Fallback to deepseek-chat
        }
        deepseek_model = model_map.get(model, 'deepseek-chat')

        api_key = os.getenv('DEEPSEEK_API_KEY', 'sk-d17817fa3e1f46d686c760dd53215078')
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        payload = {
            'model': deepseek_model,
            'messages': [
                {'role': prompt_type, 'content': user_message}
            ]
        }

        print(f'Sending request to DeepSeek API: model={deepseek_model}, messages={payload["messages"]}')

        response = requests.post('https://api.deepseek.com/v1/chat/completions', headers=headers, json=payload)
        print(f'API response status: {response.status_code}')
        response.raise_for_status()
        api_data = response.json()
        print(f'API response data: {api_data}')

        if 'choices' not in api_data or not api_data['choices']:
            print('Invalid API response: no choices found')
            return jsonify({'error': 'Invalid API response'}), 500

        ai_response = api_data['choices'][0]['message']['content']
        print(f'Returning AI response: {ai_response[:50]}...')
        return jsonify({'response': ai_response})

    except requests.exceptions.HTTPError as e:
        error_msg = f'HTTP Error: {str(e)}'
        print(error_msg)
        return jsonify({'error': error_msg}), e.response.status_code
    except requests.exceptions.RequestException as e:
        error_msg = 'Error: Unable to connect to AI service.' if g.lang == 'en' else '错误：无法连接到AI服务。'
        print(f'Network error: {e}')
        return jsonify({'error': error_msg}), 500
    except Exception as e:
        error_msg = f'Unexpected error: {str(e)}'
        print(f'Unexpected error: {e}')
        return jsonify({'error': error_msg}), 500

@app.route('/todo')
def todo():
    return render_template('todo.html')

@app.route('/api/preview-resume', methods=['POST'])
def preview_resume():
    try:
        data = request.get_json()
        print('Received preview data:', data)
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        download_option = data.get('download_option', 'pdf')
        print(f'Processing preview for {download_option}')
        with tempfile.TemporaryDirectory() as temp_dir:
            tex_file = os.path.join(temp_dir, 'cv.tex')
            latex_content = text2Latex(data, tex_file)
            if download_option == 'pdf':
                compileLatex(tex_file, temp_dir)
                pdf_file = os.path.join(temp_dir, 'cv.pdf')
                print(f'PDF exists: {os.path.exists(pdf_file)}, size: {os.path.getsize(pdf_file) if os.path.exists(pdf_file) else 0}')
                if not os.path.exists(pdf_file):
                    return jsonify({"error": "PDF generation failed: No PDF file produced"}), 500
                with open(pdf_file, 'rb') as f:
                    pdf_base64 = base64.b64encode(f.read()).decode('utf-8')
                print(f'PDF base64 length: {len(pdf_base64)}')
                result = {"type": "pdf", "content": pdf_base64}
            else:
                result = {"type": "latex", "content": latex_content}
            print(f'Returning {result["type"]} content')
            return jsonify(result), 200
    except Exception as e:
        print(f"Error in preview_resume: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-resume', methods=['POST'])
def generate_cv_route():
    try:
        data = request.get_json()
        print('Received generate data:', data)
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        download_option = data.get('download_option', 'pdf')
        print(f'Generating {download_option} file')
        with tempfile.TemporaryDirectory() as temp_dir:
            tex_file = os.path.join(temp_dir, 'cv.tex')
            text2Latex(data, tex_file)
            if download_option == 'latex':
                return send_file(
                    tex_file,
                    as_attachment=True,
                    download_name='resume.tex',
                    mimetype='text/x-tex'
                )
            else:
                compileLatex(tex_file, temp_dir)
                pdf_file = os.path.join(temp_dir, 'cv.pdf')
                print(f'PDF exists: {os.path.exists(pdf_file)}, size: {os.path.getsize(pdf_file) if os.path.exists(pdf_file) else 0}')
                if not os.path.exists(pdf_file):
                    return jsonify({"error": "PDF generation failed: No PDF file produced"}), 500
                with open(pdf_file, 'rb') as f:
                    pdf_content = f.read()
                from io import BytesIO
                return send_file(
                    BytesIO(pdf_content),
                    as_attachment=True,
                    download_name='resume.pdf',
                    mimetype='application/pdf'
                )
    except Exception as e:
        print(f"Error in generate_cv_route: {str(e)}")
        return jsonify({"error": str(e)}), 500

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    teacher = db.Column(db.String(100), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)
    start_period = db.Column(db.Integer, nullable=False)
    end_period = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    weeks = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Course {self.name} ({self.day_of_week} {self.start_period}-{self.end_period})'

with app.app_context():
    db.create_all()
    print('Database tables created.')

@app.route('/course_scheduler')
def course_scheduler():
    courses = Course.query.order_by(Course.day_of_week, Course.start_period).all()
    schedule = {}
    for i in range(7):
        schedule[i] = {}
        for j in range(1, 11):
            schedule[i][j] = []

    for course in courses:
        for period in range(course.start_period, course.end_period + 1):
            if period <= 10:
                schedule[course.day_of_week][period].append(course)

    days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    periods = range(1, 11)

    return render_template('course_scheduler.html', schedule=schedule, days=days, periods=periods)

@app.route('/CourseScheduler/add', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        name = request.form['name']
        teacher = request.form['teacher']
        day_of_week = int(request.form['day_of_week'])
        start_period = int(request.form['start_period'])
        end_period = int(request.form['end_period'])
        location = request.form['location']
        weeks = request.form['weeks']
        
        if not name or not teacher or day_of_week is None or not start_period or not end_period or not location or not weeks:
            flash(_l('所有字段都必须填写！'))
            return redirect(url_for('add_course'))
            
        if start_period > end_period or start_period < 1 or end_period > 10:
            flash(_l('节次输入无效！'))
            return redirect(url_for('add_course'))
        
        course = Course(name=name, teacher=teacher, day_of_week=day_of_week, start_period=start_period, end_period=end_period, location=location, weeks=weeks)
        db.session.add(course)
        db.session.commit()
        flash(_l('课程添加成功！'))
        return redirect(url_for('index'))
    
    days = enumerate(['周一', '周二', '周三', '周四', '周五', '周六', '周日'])
    periods = range(1, 11)
    return render_template('CourseScheduler/add.html', days=days, periods=periods)

@app.route('/CourseScheduler/edit/<int:id>', methods=['GET', 'POST'])
def edit_course(id):
    course = Course.query.get_or_404(id)
    
    if request.method == 'POST':
        course.name = request.form['name']
        course.teacher = request.form['teacher']
        course.day_of_week = int(request.form['day_of_week'])
        course.start_period = int(request.form['start_period'])
        course.end_period = int(request.form['end_period'])
        course.location = request.form['location']
        course.weeks = request.form['weeks']
        
        if not course.name or not course.teacher or course.day_of_week is None or not course.start_period or not course.end_period or not course.location or not course.weeks:
            flash(_l('所有字段都必须填写！'))
            return redirect(url_for('edit_course', id=id))
            
        if course.start_period > course.end_period or course.start_period < 1 or course.end_period > 10:
            flash(_l('节次输入无效！'))
            return redirect(url_for('edit_course', id=id))
        
        db.session.commit()
        flash(_l('课程更新成功！'))
        return redirect(url_for('index'))
    
    days = enumerate(['周一', '周二', '周三', '周四', '周五', '周六', '周日'])
    periods = range(1, 11)
    return render_template('CourseScheduler/edit.html', course=course, days=days, periods=periods)

@app.route('/delete/<int:id>')
def delete_course(id):
    course = Course.query.get_or_404(id)
    db.session.delete(course)
    db.session.commit()
    flash(_l('课程删除成功！'))
    return redirect(url_for('index'))

@app.route('/Resources_Collection')
def Resources_Collection():
    return render_template('Resources_Collection.html')


def load_notes():
    with open(NOTES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_notes(notes):
    with open(NOTES_FILE, 'w', encoding='utf-8') as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)

def load_cards():
    try:
        if os.path.exists(CARDS_FILE):
            with open(CARDS_FILE, 'r', encoding='utf-8') as f:
                cards = json.load(f)
                print(f"Loaded {len(cards)} cards from file")  # 调试信息
                return cards
        return []
    except Exception as e:
        print(f"Error loading cards: {str(e)}")
        return []

def save_cards(cards):
    try:
        with open(CARDS_FILE, 'w', encoding='utf-8') as f:
            json.dump(cards, f, ensure_ascii=False, indent=2)
            print(f"Saved {len(cards)} cards to file")  # 调试信息
    except Exception as e:
        print(f"Error saving cards: {str(e)}")

@app.route('/NoteBox')
def NoteBox():
    notes = load_notes()
    cards = load_cards()
    return render_template('notebox.html', 
                         total_notes=len(notes),
                         total_cards=len(cards),
                         recent_notes=notes[-5:] if notes else [])

@app.route('/notebox/notes')
def notebox_notes():
    notes = load_notes()
    return render_template('NoteBox/note_list.html', notes=notes)

@app.route('/notebox/edit_note')
def notebox_edit_note():
    note_id = request.args.get('id')
    if note_id:
        notes = load_notes()
        note = next((n for n in notes if n['id'] == int(note_id)), None)
        if note:
            return render_template('NoteBox/edit_note.html', note=note)
    return render_template('NoteBox/edit_note.html')

@app.route('/notebox/cards')
def notebox_cards():
    cards = load_cards()
    return render_template('NoteBox/cards.html', cards=cards)

@app.route('/notebox/review')
def notebox_review():
    return render_template('NoteBox/review.html')

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
        card_data['reviewed'] = False
        card_data['favorite'] = False
        card_data['skipped'] = False
        
        # 确保必要的字段存在
        if not all(key in card_data for key in ['question', 'answer']):
            return jsonify({'success': False, 'message': '卡片必须包含问题和答案'}), 400
        
        cards.append(card_data)
        save_cards(cards)
        
        return jsonify({
            'success': True, 
            'message': '卡片保存成功',
            'card': card_data
        })
    except Exception as e:
        print(f"Error saving card: {str(e)}")  # 添加错误日志
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/notes', methods=['GET'])
def get_notes():
    notes = load_notes()
    return jsonify(notes)

@app.route('/api/cards', methods=['GET'])
def get_cards():
    try:
        cards = load_cards()
        # 添加复习状态统计
        total_cards = len(cards)
        reviewed_cards = len([c for c in cards if c.get('reviewed', False)])
        
        return jsonify({
            'success': True,
            'cards': cards,
            'stats': {
                'total': total_cards,
                'reviewed': reviewed_cards,
                'pending': total_cards - reviewed_cards
            }
        })
    except Exception as e:
        print(f"Error getting cards: {str(e)}")  # 添加错误日志
        return jsonify({'success': False, 'message': str(e)}), 500

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

@app.route('/api/cards/<int:card_id>/review', methods=['POST'])
def review_card(card_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '缺少数据'})
        
        cards = load_cards()
        card = next((c for c in cards if c['id'] == card_id), None)
        
        if card:
            # 更新卡片状态
            card['reviewed'] = data.get('reviewed', False)
            card['reviewed_at'] = datetime.utcnow().isoformat()
            
            # 保存更新后的卡片
            save_cards(cards)
            print(f"Card {card_id} reviewed successfully, reviewed={card['reviewed']}")  # 调试信息
            return jsonify({'success': True})
        
        print(f"Card {card_id} not found")  # 调试信息
        return jsonify({'success': False, 'message': '卡片不存在'})
    except Exception as e:
        print(f"Error reviewing card {card_id}: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/cards/<int:card_id>/skip', methods=['POST'])
def skip_card(card_id):
    try:
        cards = load_cards()
        card = next((c for c in cards if c['id'] == card_id), None)
        
        if card:
            card['skipped'] = True
            card['skipped_at'] = datetime.utcnow().isoformat()
            save_cards(cards)
            print(f"Card {card_id} skipped successfully")  # 调试信息
            return jsonify({'success': True})
        
        print(f"Card {card_id} not found")  # 调试信息
        return jsonify({'success': False, 'message': '卡片不存在'})
    except Exception as e:
        print(f"Error skipping card {card_id}: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/cards/<int:card_id>/toggle-favorite', methods=['POST'])
def toggle_favorite(card_id):
    cards = load_cards()
    card = next((c for c in cards if c['id'] == card_id), None)
    if card:
        card['favorite'] = not card.get('favorite', False)
        save_cards(cards)
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': '卡片不存在'})

@app.route('/api/cards/<int:card_id>', methods=['DELETE'])
def delete_card(card_id):
    try:
        cards = load_cards()
        card = next((c for c in cards if c['id'] == card_id), None)
        if card:
            cards.remove(card)
            save_cards(cards)
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': '卡片不存在'})
    except Exception as e:
        print(f"Error deleting card {card_id}: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/cards/batch-delete', methods=['POST'])
def batch_delete_cards():
    try:
        data = request.get_json()
        if not data or 'card_ids' not in data:
            return jsonify({'success': False, 'message': '缺少卡片ID列表'})
        
        # 确保所有ID都是整数
        try:
            card_ids = [int(id) for id in data['card_ids']]
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': '无效的卡片ID格式'})
        
        print(f"Received delete request for card IDs: {card_ids}")  # 调试信息
        
        cards = load_cards()
        print(f"Total cards before deletion: {len(cards)}")  # 调试信息
        
        # 验证所有要删除的卡片ID是否存在
        existing_ids = {card['id'] for card in cards}
        invalid_ids = [id for id in card_ids if id not in existing_ids]
        if invalid_ids:
            return jsonify({
                'success': False,
                'message': f'以下卡片ID不存在: {invalid_ids}'
            })
        
        # 记录要删除的卡片
        cards_to_delete = [card for card in cards if card['id'] in card_ids]
        print(f"Cards to delete: {[card['id'] for card in cards_to_delete]}")  # 调试信息
        
        # 过滤掉要删除的卡片
        remaining_cards = [card for card in cards if card['id'] not in card_ids]
        print(f"Remaining cards after deletion: {len(remaining_cards)}")  # 调试信息
        
        # 验证删除操作
        deleted_count = len(cards) - len(remaining_cards)
        if deleted_count != len(card_ids):
            return jsonify({
                'success': False,
                'message': f'删除操作异常：预期删除 {len(card_ids)} 张，实际删除 {deleted_count} 张'
            })
        
        # 保存更新后的卡片列表
        save_cards(remaining_cards)
        print(f"Successfully deleted {deleted_count} cards")  # 调试信息
        
        return jsonify({
            'success': True,
            'message': f'成功删除 {deleted_count} 张卡片'
        })
    except Exception as e:
        print(f"Error in batch delete: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    init_data_files()
    print('Starting Flask server')
    app.run(debug=True, port=8000)

