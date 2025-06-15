from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for, flash, session, g
import os
from flask_sqlalchemy import SQLAlchemy
import tempfile
from datetime import datetime, timezone, timedelta
import base64
import requests
import json 
from text2cv import text2Latex, compileLatex
from flask_babel import Babel, _, lazy_gettext as _l
from models import db, Note, Card, Course, ReviewRecord, UTC_8

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///courses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['BABEL_DEFAULT_LOCALE'] = 'zh'

# 初始化数据库
db.init_app(app)

# 确保在应用上下文中创建所有表
with app.app_context():
    db.create_all()

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
        return redirect(url_for('course_scheduler'))
    
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
        return redirect(url_for('course_scheduler'))
    
    days = enumerate(['周一', '周二', '周三', '周四', '周五', '周六', '周日'])
    periods = range(1, 11)
    return render_template('CourseScheduler/edit.html', course=course, days=days, periods=periods)

@app.route('/delete/<int:id>')
def delete_course(id):
    course = Course.query.get_or_404(id)
    db.session.delete(course)
    db.session.commit()
    flash(_l('课程删除成功！'))
    return redirect(url_for('course_scheduler'))

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

@app.route('/notebox')
def notebox():
    try:
        notes = Note.query.order_by(Note.created_at.desc()).all()
        cards = Card.query.all()
        return render_template('notebox.html', 
                             total_notes=len(notes),
                             total_cards=len(cards),
                             recent_notes=notes[-5:] if notes else [])
    except Exception as e:
        print(f"Error in notebox route: {str(e)}")
        return render_template('notebox.html', 
                             total_notes=0,
                             total_cards=0,
                             recent_notes=[])

@app.route('/notebox/notes')
def notebox_notes():
    try:
        notes = Note.query.order_by(Note.created_at.desc()).all()
        return render_template('NoteBox/note_list.html', notes=notes)
    except Exception as e:
        print(f"Error in notebox_notes route: {str(e)}")
        return render_template('NoteBox/note_list.html', notes=[])

@app.route('/notebox/edit_note')
def notebox_edit_note():
    try:
        note_id = request.args.get('id')
        generate = request.args.get('generate')
        
        if note_id:
            note = Note.query.get(note_id)
            if not note:
                flash('笔记不存在')
                return redirect(url_for('notebox_notes'))
            return render_template('NoteBox/edit_note.html', note=note)
        elif generate:
            return render_template('NoteBox/edit_note.html', generate=True)
        else:
            return render_template('NoteBox/edit_note.html')
    except Exception as e:
        print(f"Error in notebox_edit_note route: {str(e)}")
        flash('加载笔记失败')
        return redirect(url_for('notebox'))

@app.route('/notebox/cards')
def notebox_cards():
    try:
        cards = Card.query.all()
        return render_template('NoteBox/cards.html', cards=cards)
    except Exception as e:
        print(f"Error in notebox_cards route: {str(e)}")
        return render_template('NoteBox/cards.html', cards=[])

@app.route('/notebox/review')
def notebox_review():
    return render_template('NoteBox/review.html')

@app.route('/notebox/review-records')
def notebox_review_records():
    return render_template('NoteBox/notebox_review_records.html')

@app.route('/api/notes', methods=['POST'])
def create_note():
    try:
        data = request.get_json()
        note = Note(
            title=data['title'],
            content=data['content'],
            course=data['course']
        )
        note.set_tags(data['tags'])  # 使用新方法设置标签
        db.session.add(note)
        db.session.commit()
        return jsonify({'success': True, 'message': '笔记创建成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    try:
        note = Note.query.get_or_404(note_id)
        data = request.get_json()
        note.title = data['title']
        note.content = data['content']
        note.course = data['course']
        note.set_tags(data['tags'])  # 使用新方法设置标签
        db.session.commit()
        return jsonify({'success': True, 'message': '笔记更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/cards', methods=['GET'])
def get_cards():
    try:
        cards = Card.query.all()
        cards_data = [{
            'id': card.id,
            'question': card.question,
            'answer': card.answer,
            'difficulty': card.difficulty,
            'course': card.course,
            'favorite': card.is_favorite,
            'reviewed': card.reviewed,
            'created_at': card.created_at.isoformat(),
            'updated_at': card.updated_at.isoformat()
        } for card in cards]
        
        # 添加复习状态统计
        total_cards = len(cards)
        reviewed_cards = len([c for c in cards if c.reviewed])
        
        return jsonify({
            'success': True,
            'cards': cards_data,
            'stats': {
                'total': total_cards,
                'reviewed': reviewed_cards,
                'pending': total_cards - reviewed_cards
            }
        })
    except Exception as e:
        print(f"Error getting cards: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/cards', methods=['POST'])
def save_card():
    try:
        card_data = request.json
        
        # 确保必要的字段存在
        if not all(key in card_data for key in ['question', 'answer']):
            return jsonify({'success': False, 'message': '卡片必须包含问题和答案'}), 400
        
        # 创建新卡片
        card = Card(
            question=card_data['question'],
            answer=card_data['answer'],
            difficulty=card_data.get('difficulty', 'medium'),
            course=card_data.get('course'),
            is_favorite=card_data.get('favorite', False),
            reviewed=card_data.get('reviewed', False)
        )
        
        db.session.add(card)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': '卡片保存成功',
            'card': {
                'id': card.id,
                'question': card.question,
                'answer': card.answer,
                'difficulty': card.difficulty,
                'course': card.course,
                'favorite': card.is_favorite,
                'reviewed': card.reviewed,
                'created_at': card.created_at.isoformat(),
                'updated_at': card.updated_at.isoformat()
            }
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error saving card: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/notes', methods=['GET'])
def get_notes():
    try:
        notes = Note.query.order_by(Note.created_at.desc()).all()
        return jsonify({
            'success': True,
            'notes': [{
                'id': note.id,
                'title': note.title,
                'content': note.content,
                'course': note.course,
                'tags': note.get_tags(),  # 使用新方法获取标签
                'created_at': note.created_at.isoformat(),
                'updated_at': note.updated_at.isoformat()
            } for note in notes]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    try:
        note = Note.query.get_or_404(note_id)
        db.session.delete(note)
        db.session.commit()
        return jsonify({'success': True, 'message': '笔记删除成功'})
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting note: {str(e)}")
        return jsonify({'success': False, 'message': '删除笔记失败'})

@app.route('/api/notes/<int:note_id>/cards', methods=['GET'])
def get_note_cards(note_id):
    try:
        cards = Card.query.all()
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
        
        card = Card.query.get(card_id)
        if card:
            card.reviewed = data.get('reviewed', False)
            db.session.commit()
            return jsonify({'success': True})
        
        return jsonify({'success': False, 'message': '卡片不存在'})
    except Exception as e:
        db.session.rollback()
        print(f"Error reviewing card {card_id}: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/cards/<int:card_id>/skip', methods=['POST'])
def skip_card(card_id):
    try:
        cards = Card.query.all()
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
    try:
        card = Card.query.get(card_id)
        if card:
            card.is_favorite = not card.is_favorite
            db.session.commit()
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': '卡片不存在'})
    except Exception as e:
        db.session.rollback()
        print(f"Error toggling favorite for card {card_id}: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/cards/<int:card_id>', methods=['DELETE'])
def delete_card(card_id):
    try:
        card = Card.query.get(card_id)
        if card:
            db.session.delete(card)
            db.session.commit()
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': '卡片不存在'})
    except Exception as e:
        db.session.rollback()
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
        
        # 删除选中的卡片
        Card.query.filter(Card.id.in_(card_ids)).delete(synchronize_session=False)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'成功删除 {len(card_ids)} 张卡片'
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error batch deleting cards: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/notebox/generate-card')
def notebox_generate_card():
    return render_template('NoteBox/generate_card.html')

@app.route('/api/review-records', methods=['GET'])
def get_review_records():
    try:
        print('Fetching review records...')
        sort_by = request.args.get('sort_by', 'newest')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        print(f'Parameters: sort_by={sort_by}, start_date={start_date}, end_date={end_date}')

        query = ReviewRecord.query

        if start_date and end_date:
            try:
                # 将 ISO 格式的时间字符串转换为带时区的 datetime 对象
                start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                # 转换为 UTC+8
                start = start.astimezone(UTC_8)
                end = end.astimezone(UTC_8)
                query = query.filter(
                    ReviewRecord.start_time >= start,
                    ReviewRecord.end_time <= end
                )
                print(f'Filtered by date range: {start} to {end}')
            except ValueError as e:
                print(f'Invalid date format: {e}')
                return jsonify({'success': False, 'message': 'Invalid date format'}), 400

        if sort_by == 'newest':
            query = query.order_by(ReviewRecord.start_time.desc())
        elif sort_by == 'oldest':
            query = query.order_by(ReviewRecord.start_time.asc())
        elif sort_by == 'duration':
            query = query.order_by(ReviewRecord.duration.desc())

        records = query.all()
        print(f'Found {len(records)} review records')

        records_data = []
        for record in records:
            try:
                # 时间已经是 UTC+8，直接使用
                record_data = {
                    'id': record.id,
                    'start_time': record.start_time.isoformat(),
                    'end_time': record.end_time.isoformat(),
                    'duration': record.duration,
                    'mastered_count': record.mastered_count,
                    'not_mastered_count': record.not_mastered_count,
                    'cards': []
                }
                
                for card in record.cards:
                    try:
                        card_data = {
                            'id': card.id,
                            'question': card.question,
                            'answer': card.answer,
                            'is_mastered': card.is_mastered if hasattr(card, 'is_mastered') else False
                        }
                        record_data['cards'].append(card_data)
                    except Exception as e:
                        print(f'Error processing card {card.id}: {e}')
                        continue

                records_data.append(record_data)
            except Exception as e:
                print(f'Error processing record {record.id}: {e}')
                continue

        print('Successfully processed all records')
        return jsonify({
            'success': True,
            'records': records_data
        })
    except Exception as e:
        print(f"Error getting review records: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/review-records', methods=['POST'])
def create_review_record():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400

        print('Creating review record with data:', data)

        # 获取卡片列表
        cards = []
        for card_data in data['cards']:
            card = Card.query.get(card_data['id'])
            if card:
                # 设置卡片的掌握状态
                card.is_mastered = card_data.get('is_mastered', False)
                cards.append(card)

        # 将 ISO 格式的时间字符串转换为带时区的 datetime 对象
        start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))

        # 创建复习记录（ReviewRecord.create 会自动转换为 UTC+8）
        record = ReviewRecord.create(
            start_time=start_time,
            end_time=end_time,
            duration=data['duration'],
            mastered_count=data['mastered_count'],
            not_mastered_count=data['not_mastered_count'],
            cards=cards
        )

        db.session.add(record)
        db.session.commit()

        print(f'Successfully created review record {record.id}')
        return jsonify({
            'success': True,
            'message': 'Review record created successfully',
            'record_id': record.id
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error creating review record: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/review-records/<int:record_id>', methods=['DELETE'])
def delete_review_record(record_id):
    try:
        record = ReviewRecord.query.get_or_404(record_id)
        db.session.delete(record)
        db.session.commit()
        return jsonify({'success': True, 'message': '复习记录删除成功'})
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting review record: {str(e)}")
        return jsonify({'success': False, 'message': '删除复习记录失败'})

@app.route('/api/notes/delete-all', methods=['DELETE'])
def delete_all_notes():
    try:
        # 删除所有笔记
        Note.query.delete()
        db.session.commit()
        return jsonify({
            'success': True,
            'message': '所有笔记已删除'
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting all notes: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'删除失败: {str(e)}'
        }), 500

@app.route('/api/cards/delete-all', methods=['DELETE'])
def delete_all_cards():
    try:
        # 删除所有卡片
        Card.query.delete()
        db.session.commit()
        return jsonify({
            'success': True,
            'message': '所有卡片已删除'
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting all cards: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'删除失败: {str(e)}'
        }), 500

@app.route('/api/review-records/delete-all', methods=['DELETE'])
def delete_all_review_records():
    try:
        # 删除所有复习记录
        ReviewRecord.query.delete()
        db.session.commit()
        return jsonify({
            'success': True,
            'message': '所有复习记录已删除'
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting all review records: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'删除失败: {str(e)}'
        }), 500

if __name__ == '__main__':
    init_data_files()
    print('Starting Flask server')
    app.run(debug=True, port=8000)

