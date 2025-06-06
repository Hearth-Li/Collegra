from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for, flash, session, g
import os
from flask_sqlalchemy import SQLAlchemy
import tempfile
from datetime import datetime
import base64
import requests
from text2cv import text2Latex, compileLatex
from flask_babel import Babel, _, lazy_gettext as _l

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///courses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['BABEL_DEFAULT_LOCALE'] = 'zh'

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
def MiKTeX_install():
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

if __name__ == '__main__':
    print('Starting Flask server')
    app.run(debug=True, port=8000)

