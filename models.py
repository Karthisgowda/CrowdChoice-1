import uuid
import datetime
from app import db

class Poll(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    options = db.relationship('Option', backref='poll', lazy=True, cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'options': [option.to_dict() for option in self.options],
            'total_votes': sum(option.votes for option in self.options)
        }

class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(100), nullable=False)
    votes = db.Column(db.Integer, default=0)
    poll_id = db.Column(db.String(36), db.ForeignKey('poll.id'), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'votes': self.votes
        }
