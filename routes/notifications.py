from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Notification

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('', methods=['GET'])
@jwt_required()
def get_notifications():
    try:
        current_user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        notifications_query = Notification.query.filter_by(user_id=current_user_id).order_by(Notification.timestamp.desc())
        
        paginated_notifications = notifications_query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        notifications = [notification.to_dict() for notification in paginated_notifications.items]
        
        return jsonify({
            'notifications': notifications,
            'total': paginated_notifications.total,
            'page': page,
            'per_page': per_page,
            'total_pages': paginated_notifications.pages
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/<int:notification_id>/read', methods=['PUT'])
@jwt_required()
def mark_notification_as_read(notification_id):
    try:
        current_user_id = get_jwt_identity()
        notification = Notification.query.filter_by(
            id=notification_id, 
            user_id=current_user_id
        ).first()
        
        if not notification:
            return jsonify({'error': 'Notification not found'}), 404
        
        notification.is_read = True
        db.session.commit()
        
        return jsonify({'notification': notification.to_dict()}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/mark-all-read', methods=['PUT'])
@jwt_required()
def mark_all_notifications_as_read():
    try:
        current_user_id = get_jwt_identity()
        
        Notification.query.filter_by(
            user_id=current_user_id,
            is_read=False
        ).update({'is_read': True})
        
        db.session.commit()
        
        return jsonify({'message': 'All notifications marked as read'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('', methods=['POST'])
@jwt_required()
def create_notification():
    """Create a notification (for admin/system use)"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        notification = Notification(
            user_id=current_user_id,
            title=data.get('title', ''),
            message=data.get('message', ''),
            type=data.get('type', 'general')
        )
        
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({'notification': notification.to_dict()}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500