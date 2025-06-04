from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from flask_babel import Babel, _, lazy_gettext as _l

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///courses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['BABEL_DEFAULT_LOCALE'] = 'zh'

babel = Babel(app)




db = SQLAlchemy(app)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    teacher = db.Column(db.String(100), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False) # 0-6 for Mon-Sun
    start_period = db.Column(db.Integer, nullable=False)
    end_period = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    weeks = db.Column(db.String(100), nullable=False) # e.g., "1-15周"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Course {self.name} ({self.day_of_week} {self.start_period}-{self.end_period})'


with app.app_context():
    db.create_all()
    print('Database tables created.')

@app.route('/')
def index():
    courses = Course.query.order_by(Course.day_of_week, Course.start_period).all()
    # Structure courses by day and period for the grid view
    schedule = {} # { day: { period: [courses] } }
    for i in range(7): # Days 0-6 (Mon-Sun)
        schedule[i] = {}
        for j in range(1, 11): # Periods 1-10
            schedule[i][j] = []

    for course in courses:
        for period in range(course.start_period, course.end_period + 1):
            if period <= 10: # Limit to periods 1-10 for display
                 schedule[course.day_of_week][period].append(course)

    days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    periods = range(1, 11)

    return render_template('index.html', schedule=schedule, days=days, periods=periods)

@app.route('/add', methods=['GET', 'POST'])
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
    
    days = enumerate([_l('周一'), _l('周二'), _l('周三'), _l('周四'), _l('周五'), _l('周六'), _l('周日')])
    periods = range(1, 11)
    return render_template('add.html', days=days, periods=periods)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
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
    
    days = enumerate([_l('周一'), _l('周二'), _l('周三'), _l('周四'), _l('周五'), _l('周六'), _l('周日')])
    periods = range(1, 11)
    return render_template('edit.html', course=course, days=days, periods=periods)

@app.route('/delete/<int:id>')
def delete_course(id):
    course = Course.query.get_or_404(id)
    db.session.delete(course)
    db.session.commit()
    flash(_l('课程删除成功！'))
    return redirect(url_for('index'))

@app.route('/set_language/<lang>')
def set_language(lang):
    if lang in ['zh', 'en']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('index'))

if __name__ == '__main__':
    app.run(debug=True) 