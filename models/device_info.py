from models import db
from datetime import datetime
import json

class DeviceInfo(db.Model):
    __tablename__ = 'device_info'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    device_id = db.Column(db.String(255), unique=True, nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    platform_version = db.Column(db.String(50))
    app_version = db.Column(db.String(50))
    device_info = db.Column(db.Text)  # JSON string for additional device info
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def set_device_info(self, info_dict):
        self.device_info = json.dumps(info_dict)
    
    def get_device_info(self):
        if self.device_info:
            return json.loads(self.device_info)
        return {}
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'platform': self.platform,
            'platform_version': self.platform_version,
            'app_version': self.app_version,
            'device_info': self.get_device_info(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<DeviceInfo {self.device_id}>'