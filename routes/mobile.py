from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, DeviceInfo

mobile_bp = Blueprint('mobile', __name__)

@mobile_bp.route('/app-config', methods=['GET'])
def get_app_config():
    """Get mobile app configuration"""
    try:
        config = {
            'app_version': '1.0.0',
            'min_supported_version': '1.0.0',
            'features': {
                'skin_scanning': True,
                'offline_mode': True,
                'notifications': True,
                'history_sync': True
            },
            'ai_model': {
                'version': '1.0',
                'confidence_threshold': 0.7
            },
            'limits': {
                'max_scans_per_day': 50,
                'max_image_size_mb': 10
            }
        }
        
        return jsonify(config), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mobile_bp.route('/device-info', methods=['POST'])
def register_device():
    """Register or update device information"""
    try:
        data = request.get_json()
        device_id = data.get('device_id')
        
        if not device_id:
            return jsonify({'error': 'Device ID is required'}), 400
        
        # Check if device already exists
        device = DeviceInfo.query.filter_by(device_id=device_id).first()
        
        if device:
            # Update existing device
            device.platform = data.get('platform', device.platform)
            device.platform_version = data.get('platform_version', device.platform_version)
            device.app_version = data.get('app_version', device.app_version)
            if 'device_info' in data:
                device.set_device_info(data['device_info'])
        else:
            # Create new device
            device = DeviceInfo(
                device_id=device_id,
                platform=data.get('platform', 'unknown'),
                platform_version=data.get('platform_version'),
                app_version=data.get('app_version')
            )
            if 'device_info' in data:
                device.set_device_info(data['device_info'])
            
            db.session.add(device)
        
        db.session.commit()
        
        return jsonify({
            'device': device.to_dict(),
            'message': 'Device registered successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@mobile_bp.route('/device-info/<device_id>', methods=['GET'])
@jwt_required()
def get_device_info(device_id):
    """Get device information"""
    try:
        device = DeviceInfo.query.filter_by(device_id=device_id).first()
        
        if not device:
            return jsonify({'error': 'Device not found'}), 404
        
        return jsonify({'device': device.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500