from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    due_date = db.Column(db.DateTime)
    priority = db.Column(db.String(10), default='Medium')
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def index():
    # 获取所有任务并按优先级和截止日期排序
    tasks = Task.query.order_by(
        Task.completed,
        Task.priority.desc(),
        Task.due_date
    ).all()
    
    # 按完成状态分组
    active_tasks = [t for t in tasks if not t.completed]
    completed_tasks = [t for t in tasks if t.completed]
    
    return render_template('task.html', 
                          active_tasks=active_tasks,
                          completed_tasks=completed_tasks)

@app.route('/add', methods=['POST'])
def add_task():
    title = request.form['title']
    description = request.form['description']
    due_date_str = request.form['due_date']
    priority = request.form['priority']
    
    # 转换日期格式
    due_date = datetime.strptime(due_date_str, '%Y-%m-%d') if due_date_str else None
    
    new_task = Task(
        title=title,
        description=description,
        due_date=due_date,
        priority=priority
    )
    
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/complete/<int:task_id>')
def complete_task(task_id):
    task = Task.query.get(task_id)
    task.completed = True
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/uncomplete/<int:task_id>')
def uncomplete_task(task_id):
    task = Task.query.get(task_id)
    task.completed = False
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    task = Task.query.get(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 创建数据库表
    app.run(debug=True, port=5001)  # 使用不同端口避免冲突