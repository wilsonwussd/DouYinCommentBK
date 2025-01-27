from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def update_login_time(self):
        self.last_login = datetime.utcnow()
        db.session.commit()

class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.String(20), nullable=False)
    comment_id = db.Column(db.String(20), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    likes = db.Column(db.Integer, default=0)
    user_nickname = db.Column(db.String(100))
    user_id = db.Column(db.String(100))
    ip_location = db.Column(db.String(50))
    reply_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime)
    collected_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """将评论对象转换为字典"""
        return {
            'id': self.id,
            'video_id': self.video_id,
            'comment_id': self.comment_id,
            'content': self.content if self.content else '',
            'created_at': self.created_at.strftime('%Y-%m-%dT%H:%M:%S') if self.created_at else '',
            'likes': self.likes,
            'reply_count': self.reply_count,
            'user_id': self.user_id,
            'user_nickname': self.user_nickname if self.user_nickname else '',
            'ip_location': self.ip_location if self.ip_location else '',
            'collected_at': self.collected_at.strftime('%Y-%m-%dT%H:%M:%S.%f') if self.collected_at else ''
        } 