from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone, timedelta

db = SQLAlchemy()

# 复习记录和卡片的关联表
review_cards = db.Table('review_cards',
    db.Column('review_id', db.Integer, db.ForeignKey('review_record.id'), primary_key=True),
    db.Column('card_id', db.Integer, db.ForeignKey('card.id'), primary_key=True)
)

# 定义 UTC+8 时区
UTC_8 = timezone(timedelta(hours=8))

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    course = db.Column(db.String(100))
    tags = db.Column(db.String(200))  # 存储为逗号分隔的字符串
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC_8))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC_8), onupdate=lambda: datetime.now(UTC_8))

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
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC_8))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC_8), onupdate=lambda: datetime.now(UTC_8))

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    teacher = db.Column(db.String(100), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)
    start_period = db.Column(db.Integer, nullable=False)
    end_period = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    weeks = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC_8))

    def __repr__(self):
        return f'<Course {self.name} ({self.day_of_week} {self.start_period}-{self.end_period})'

class ReviewRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime(timezone=True), nullable=False)
    end_time = db.Column(db.DateTime(timezone=True), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # 持续时间（秒）
    mastered_count = db.Column(db.Integer, nullable=False)
    not_mastered_count = db.Column(db.Integer, nullable=False)
    cards = db.relationship('Card', secondary=review_cards, backref=db.backref('review_records', lazy='dynamic'))

    def __repr__(self):
        return f'<ReviewRecord {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'duration': self.duration,
            'mastered_count': self.mastered_count,
            'not_mastered_count': self.not_mastered_count,
            'cards': [{
                'id': card.id,
                'question': card.question,
                'answer': card.answer,
                'is_mastered': getattr(card, 'is_mastered', False)
            } for card in self.cards]
        }

    @classmethod
    def create(cls, start_time, end_time, duration, mastered_count, not_mastered_count, cards=None):
        # 确保时间包含时区信息，并转换为 UTC+8
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)
        if end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=timezone.utc)
            
        # 转换为 UTC+8
        start_time = start_time.astimezone(UTC_8)
        end_time = end_time.astimezone(UTC_8)
            
        record = cls(
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            mastered_count=mastered_count,
            not_mastered_count=not_mastered_count
        )
        if cards:
            record.cards = cards
        return record