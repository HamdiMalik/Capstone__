from models import db
from datetime import datetime
import json

class Scan(db.Model):
    __tablename__ = 'scans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    image_path = db.Column(db.Text, nullable=False)
    result_condition = db.Column(db.String(100))
    result_confidence = db.Column(db.Float)
    result_recommendations = db.Column(db.Text)  # JSON string
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def set_result(self, condition, confidence, recommendations):
        self.result_condition = condition
        self.result_confidence = confidence
        self.result_recommendations = json.dumps(recommendations)
    
    def get_result(self):
        if self.result_condition:
            return {
                'condition': self.result_condition,
                'confidence': self.result_confidence,
                'recommendations': json.loads(self.result_recommendations) if self.result_recommendations else []
            }
        return None
    
    def to_dict(self):
        result = self.get_result()
        return {
            'id': str(self.id),
            'image_path': self.image_path,
            'result': result,
            'timestamp': self.timestamp.isoformat(),
            'created_at': self.created_at.isoformat(),
            'synced': True  # Always true for server records
        }
    
    def __repr__(self):
        return f'<Scan {self.id} by User {self.user_id}>'