from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, UTC

db = SQLAlchemy()

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    course = db.Column(db.String(100))
    tags = db.Column(db.String(200))  # 存储为逗号分隔的字符串
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    def get_tags(self):
        """将存储的标签字符串转换为列表"""
        return self.tags.split(',') if self.tags else []

    def set_tags(self, tags_list):
        """将标签列表转换为逗号分隔的字符串"""
        self.tags = ','.join(tags_list) if tags_list else ''

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(20), default='medium')
    course = db.Column(db.String(100))
    is_favorite = db.Column(db.Boolean, default=False)
    reviewed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)) 