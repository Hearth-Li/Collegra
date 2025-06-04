from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Certificate(db.Model):
    __tablename__ = 'certificates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(20), nullable=False)  # competition, volunteer, research, scholarship, internship
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)  # pdf, jpg, png
    file_size = db.Column(db.Integer, nullable=False)  # in bytes
    volunteer_hours = db.Column(db.Float)  # Only for volunteer category
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'description': self.description,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'volunteer_hours': self.volunteer_hours,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    @staticmethod
    def get_stats(user_id):
        """Get statistics for the dashboard"""
        stats = {
            'total': Certificate.query.filter_by(user_id=user_id).count(),
            'competition': Certificate.query.filter_by(user_id=user_id, category='competition').count(),
            'volunteer': Certificate.query.filter_by(user_id=user_id, category='volunteer').count(),
            'research': Certificate.query.filter_by(user_id=user_id, category='research').count(),
            'scholarship': Certificate.query.filter_by(user_id=user_id, category='scholarship').count(),
            'internship': Certificate.query.filter_by(user_id=user_id, category='internship').count(),
            'volunteer_hours': db.session.query(db.func.sum(Certificate.volunteer_hours))
                .filter_by(user_id=user_id, category='volunteer')
                .scalar() or 0
        }
        return stats 